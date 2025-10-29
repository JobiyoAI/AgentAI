import os
from typing import List
from pathlib import Path
import fitz  # PyMuPDF
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document
import vecs
from supabase import create_client, Client

class RAGSystem:
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        self.db_password = os.getenv("SUPABASE_DB_PASSWORD")
        
        # Inicializar embeddings
        self.embeddings = HuggingFaceEmbeddings(
            model_name=os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        )
        
        # Conexión a Supabase
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
        
        # Configurar vecs para vector store
        DB_CONNECTION = f"postgresql://postgres:{self.db_password}@db.{self.supabase_url.split('//')[1].split('.')[0]}.supabase.co:5432/postgres"
        self.vx = vecs.create_client(DB_CONNECTION)
        
        # Crear o obtener colección
        self.collection_name = "documents"
        self._setup_collection()
        
    def _setup_collection(self):
        """Configura la colección de vectores en Supabase"""
        try:
            # Intentar obtener colección existente
            self.collection = self.vx.get_collection(self.collection_name)
        except:
            # Crear nueva colección si no existe
            self.collection = self.vx.create_collection(
                name=self.collection_name,
                dimension=384  # Dimensión de all-MiniLM-L6-v2
            )
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extrae texto de un PDF usando PyMuPDF"""
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text
    
    def process_pdfs(self, docs_folder: str = "docs") -> int:
        """Procesa todos los PDFs en la carpeta docs"""
        docs_path = Path(docs_folder)
        if not docs_path.exists():
            docs_path.mkdir(parents=True)
            print(f"Carpeta '{docs_folder}' creada. Añade tus PDFs ahí.")
            return 0
        
        pdf_files = list(docs_path.glob("*.pdf"))
        if not pdf_files:
            print(f"No se encontraron PDFs en '{docs_folder}'")
            return 0
        
        all_documents = []
        
        for pdf_file in pdf_files:
            print(f"Procesando: {pdf_file.name}")
            text = self.extract_text_from_pdf(str(pdf_file))
            
            # Dividir en chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len,
            )
            
            chunks = text_splitter.split_text(text)
            
            # Crear documentos con metadata
            for i, chunk in enumerate(chunks):
                doc = Document(
                    page_content=chunk,
                    metadata={
                        "source": pdf_file.name,
                        "chunk": i,
                        "total_chunks": len(chunks)
                    }
                )
                all_documents.append(doc)
        
        # Generar embeddings e insertar en Supabase
        self._index_documents(all_documents)
        
        return len(all_documents)
    
    def _index_documents(self, documents: List[Document]):
        """Indexa documentos en la base de datos vectorial"""
        texts = [doc.page_content for doc in documents]
        metadatas = [doc.metadata for doc in documents]
        
        # Generar embeddings
        embeddings = self.embeddings.embed_documents(texts)
        
        # Preparar registros para vecs
        records = [
            (f"doc_{i}", embedding, {"text": text, **metadata})
            for i, (text, embedding, metadata) in enumerate(zip(texts, embeddings, metadatas))
        ]
        
        # Insertar en Supabase
        self.collection.upsert(records=records)
        
        # Crear índice para búsquedas rápidas
        self.collection.create_index()
        
        print(f"✅ {len(documents)} chunks indexados en Supabase")
    
    def search(self, query: str, k: int = 4) -> List[Document]:
        """Busca documentos relevantes usando similaridad vectorial"""
        # Generar embedding de la query
        query_embedding = self.embeddings.embed_query(query)
        
        # Buscar en Supabase
        results = self.collection.query(
            data=query_embedding,
            limit=k,
            include_value=True,
            include_metadata=True
        )
        
        # Convertir resultados a Documents
        documents = []
        for result_id, distance, metadata in results:
            doc = Document(
                page_content=metadata.get("text", ""),
                metadata={
                    "source": metadata.get("source", "unknown"),
                    "chunk": metadata.get("chunk", 0),
                    "similarity_score": 1 - distance  # Convertir distancia a score
                }
            )
            documents.append(doc)
        
        return documents
    
    def clear_collection(self):
        """Limpia toda la colección de vectores"""
        self.vx.delete_collection(self.collection_name)
        self._setup_collection()
        print("✅ Colección limpiada")