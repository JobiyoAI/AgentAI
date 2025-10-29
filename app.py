import streamlit as st
import os
from dotenv import load_dotenv
from pathlib import Path
from rag import RAGSystem
from agent import AIAgent

# Cargar variables de entorno
load_dotenv()

# Configuración de la página
st.set_page_config(
    page_title="AI Agent con RAG",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos personalizados
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1E88E5;
        margin-bottom: 1rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .user-message {
        background-color: #E3F2FD;
        border-left: 4px solid #1E88E5;
    }
    .assistant-message {
        background-color: #F5F5F5;
        border-left: 4px solid #43A047;
    }
    .sidebar-info {
        background-color: #FFF3E0;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #FF9800;
    }
</style>
""", unsafe_allow_html=True)

# Inicializar session state
if 'rag_system' not in st.session_state:
    st.session_state.rag_system = None
if 'agent' not in st.session_state:
    st.session_state.agent = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'system_ready' not in st.session_state:
    st.session_state.system_ready = False

def initialize_system():
    """Inicializa el sistema RAG y el agente"""
    try:
        with st.spinner("🔄 Inicializando sistema..."):
            st.session_state.rag_system = RAGSystem()
            st.session_state.agent = AIAgent(st.session_state.rag_system)
            st.session_state.system_ready = True
            st.success("✅ Sistema inicializado correctamente")
    except Exception as e:
        st.error(f"❌ Error al inicializar: {str(e)}")
        st.session_state.system_ready = False

def process_documents():
    """Procesa los documentos PDF en la carpeta docs"""
    try:
        with st.spinner("📚 Procesando documentos PDF..."):
            num_chunks = st.session_state.rag_system.process_pdfs("docs")
            if num_chunks > 0:
                st.success(f"✅ {num_chunks} fragmentos indexados correctamente")
            else:
                st.warning("⚠️ No se encontraron PDFs en la carpeta 'docs'")
    except Exception as e:
        st.error(f"❌ Error al procesar documentos: {str(e)}")

# Sidebar
with st.sidebar:
    st.markdown("## ⚙️ Configuración")
    
    # Estado del sistema
    if st.session_state.system_ready:
        st.markdown('<div class="sidebar-info">✅ Sistema Activo</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="sidebar-info">⚠️ Sistema No Inicializado</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Botón de inicialización
    if st.button("🚀 Inicializar Sistema", use_container_width=True):
        initialize_system()
    
    st.markdown("---")
    
    # Gestión de documentos
    st.markdown("## 📚 Documentos")
    
    docs_path = Path("docs")
    if docs_path.exists():
        pdf_files = list(docs_path.glob("*.pdf"))
        st.write(f"PDFs encontrados: **{len(pdf_files)}**")
        
        if pdf_files:
            with st.expander("Ver archivos"):
                for pdf in pdf_files:
                    st.write(f"📄 {pdf.name}")
    else:
        st.info("Carpeta 'docs' no encontrada")
    
    if st.button("🔄 Procesar/Actualizar PDFs", use_container_width=True, disabled=not st.session_state.system_ready):
        process_documents()
    
    if st.button("🗑️ Limpiar Base de Datos", use_container_width=True, disabled=not st.session_state.system_ready):
        st.session_state.rag_system.clear_collection()
        st.success("✅ Base de datos limpiada")
    
    st.markdown("---")
    
    # Limpiar chat
    if st.button("🆕 Nuevo Chat", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()
    
    st.markdown("---")
    
    # Información
    with st.expander("ℹ️ Información"):
        st.markdown("""
        **Características:**
        - 🤖 LLM: Gemini Pro
        - 📚 RAG: PDFs en carpeta `docs`
        - 🔍 Búsqueda Web: Tavily
        - 💾 Vector DB: Supabase
        
        **Uso:**
        1. Inicializa el sistema
        2. Añade PDFs a la carpeta `docs`
        3. Procesa los documentos
        4. ¡Pregunta lo que quieras!
        """)

# Main area
st.markdown('<div class="main-header">🤖 AI Agent Local</div>', unsafe_allow_html=True)

# Verificar si el sistema está listo
if not st.session_state.system_ready:
    st.info("👈 Haz clic en 'Inicializar Sistema' en la barra lateral para comenzar")
else:
    # Área de chat
    st.markdown("### 💬 Chat")
    
    # Mostrar historial de chat
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                st.markdown(f'<div class="chat-message user-message">👤 <b>Tú:</b><br>{message["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-message assistant-message">🤖 <b>Asistente:</b><br>{message["content"]}</div>', unsafe_allow_html=True)
    
    # Input del usuario
    with st.form(key="chat_form", clear_on_submit=True):
        col1, col2 = st.columns([6, 1])
        with col1:
            user_input = st.text_input(
                "Escribe tu mensaje...",
                placeholder="Pregunta sobre tus documentos o cualquier tema...",
                label_visibility="collapsed"
            )
        with col2:
            submit_button = st.form_submit_button("Enviar 📤", use_container_width=True)
    
    # Procesar mensaje
    if submit_button and user_input:
        # Añadir mensaje del usuario al historial
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input
        })
        
        # Obtener respuesta del agente
        with st.spinner("🤔 Pensando..."):
            response = st.session_state.agent.chat(user_input)
        
        # Añadir respuesta al historial
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": response
        })
        
        # Recargar para mostrar el nuevo mensaje
        st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    Desarrollado con ❤️ usando LangChain, Gemini, Supabase y Streamlit
</div>
""", unsafe_allow_html=True)