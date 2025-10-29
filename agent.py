import os
from typing import List, Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import Tool
from langchain.prompts import PromptTemplate
from langchain_community.tools.tavily_search import TavilySearchResults
from rag import RAGSystem

class AIAgent:
    def __init__(self, rag_system: RAGSystem):
        self.rag = rag_system
        
        # Inicializar Gemini
        self.llm = ChatGoogleGenerativeAI(
            model=os.getenv("GEMINI_MODEL", "gemini-pro"),
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            temperature=0.7,
            convert_system_message_to_human=True
        )
        
        # Configurar herramientas
        self.tools = self._setup_tools()
        
        # Crear agente
        self.agent = self._create_agent()
    
    def _setup_tools(self) -> List[Tool]:
        """Configura las herramientas disponibles para el agente"""
        tools = []
        
        # Tool 1: RAG - Búsqueda en documentos
        def search_documents(query: str) -> str:
            """Busca información en los documentos PDF indexados"""
            docs = self.rag.search(query, k=4)
            if not docs:
                return "No se encontró información relevante en los documentos."
            
            context = "\n\n".join([
                f"📄 Fuente: {doc.metadata.get('source', 'desconocida')}\n{doc.page_content}"
                for doc in docs
            ])
            return f"Información encontrada en los documentos:\n\n{context}"
        
        tools.append(Tool(
            name="BuscarDocumentos",
            func=search_documents,
            description="Útil para buscar información en los documentos PDF que han sido indexados. Úsala cuando necesites información específica de los documentos locales."
        ))
        
        # Tool 2: Búsqueda Web
        try:
            web_search = TavilySearchResults(
                max_results=3,
                api_key=os.getenv("TAVILY_API_KEY")
            )
            tools.append(Tool(
                name="BuscarWeb",
                func=web_search.run,
                description="Útil para buscar información actualizada en internet. Úsala cuando necesites datos recientes, noticias, o información que no está en los documentos locales."
            ))
        except Exception as e:
            print(f"⚠️ Búsqueda web no disponible: {e}")
        
        return tools
    
    def _create_agent(self) -> AgentExecutor:
        """Crea el agente ReAct con LangChain"""
        
        # Prompt template para el agente
        template = """Eres un asistente AI útil con acceso a documentos locales y búsqueda web.

                    Tienes acceso a las siguientes herramientas:

                    {tools}

                    Usa el siguiente formato:

                    Pregunta: la pregunta de entrada que debes responder
                    Pensamiento: siempre debes pensar qué hacer
                    Acción: la acción a tomar, debe ser una de [{tool_names}]
                    Entrada de Acción: la entrada para la acción
                    Observación: el resultado de la acción
                    ... (este Pensamiento/Acción/Entrada de Acción/Observación puede repetirse N veces)
                    Pensamiento: Ahora sé la respuesta final
                    Respuesta Final: la respuesta final a la pregunta de entrada original

                    Cuando busques en documentos, primero intenta con BuscarDocumentos. Si no encuentras información suficiente, usa BuscarWeb.

                    Pregunta: {input}
                    {agent_scratchpad}"""

        prompt = PromptTemplate.from_template(template)
        
        # Crear agente ReAct
        agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        # Crear ejecutor
        agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            max_iterations=5,
            handle_parsing_errors=True
        )
        
        return agent_executor
    
    def run(self, query: str) -> Dict[str, Any]:
        """Ejecuta una consulta en el agente"""
        try:
            result = self.agent.invoke({"input": query})
            return {
                "success": True,
                "output": result.get("output", ""),
                "intermediate_steps": result.get("intermediate_steps", [])
            }
        except Exception as e:
            return {
                "success": False,
                "output": f"Error: {str(e)}",
                "error": str(e)
            }
    
    def chat(self, message: str) -> str:
        """Interfaz simple de chat"""
        result = self.run(message)
        return result.get("output", "Lo siento, ocurrió un error.")