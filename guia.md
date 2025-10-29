# 🚀 Guía de Instalación - AI Agent Local

## 📋 Prerrequisitos

- Python 3.9 o superior
- Cuenta de Google Cloud (para Gemini API)
- Proyecto de Supabase
- Cuenta de Tavily (para búsqueda web)

## 🔧 Paso 1: Configurar Supabase

### 1.1 Habilitar pgvector en Supabase

1. Ve a tu proyecto en Supabase: https://inegydiqsscibuumbkeo.supabase.co
2. Ve a **SQL Editor** en el menú lateral
3. Ejecuta el siguiente SQL:

```sql
-- Habilitar extensión pgvector
CREATE EXTENSION IF NOT EXISTS vector;

-- Verificar que se instaló correctamente
SELECT * FROM pg_extension WHERE extname = 'vector';
```

### 1.2 Obtener credenciales

1. **URL del proyecto**: Ya la tienes `https://inegydiqsscibuumbkeo.supabase.co`
2. **API Key (anon/public)**:
   - Ve a Settings > API
   - Copia la `anon` `public` key
3. **Contraseña de la DB**:
   - La que usaste al crear el proyecto
   - Si no la recuerdas, ve a Settings > Database y resetéala

## 🔑 Paso 2: Obtener API Keys

### 2.1 Gemini API Key

1. Ve a [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Crea una nueva API key
3. Cópiala (solo se muestra una vez)

### 2.2 Tavily API Key (para búsqueda web)

1. Ve a [Tavily](https://tavily.com/)
2. Regístrate (tiene plan gratuito)
3. Ve a tu dashboard y copia la API key

## 💻 Paso 3: Instalación Local

### 3.1 Clonar/Crear estructura del proyecto

```bash
# Crear directorio del proyecto
mkdir mi-agente-ai
cd mi-agente-ai

# Crear carpeta para PDFs
mkdir docs

# Crear estructura
touch app.py agent.py rag.py requirements.txt .env
```

### 3.2 Instalar dependencias

```bash
# Crear entorno virtual (recomendado)
python -m venv venv

# Activar entorno virtual
# En Windows:
venv\Scripts\activate
# En Mac/Linux:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### 3.3 Configurar variables de entorno

Crea un archivo `.env` con tus credenciales:

```bash
# Gemini API
GOOGLE_API_KEY=tu_gemini_api_key_aqui

# Supabase
SUPABASE_URL=https://inegydiqsscibuumbkeo.supabase.co
SUPABASE_KEY=tu_supabase_anon_key_aqui
SUPABASE_DB_PASSWORD=tu_password_db_aqui

# Tavily Search
TAVILY_API_KEY=tu_tavily_api_key_aqui

# Configuración (opcional - estos son los valores por defecto)
EMBEDDING_MODEL=all-MiniLM-L6-v2
GEMINI_MODEL=gemini-pro
```

## 🎯 Paso 4: Ejecutar la Aplicación

### 4.1 Añadir documentos PDF

Copia tus PDFs a la carpeta `docs/`:

```bash
cp /ruta/a/tus/pdfs/*.pdf docs/
```

### 4.2 Iniciar Streamlit

```bash
streamlit run app.py
```

La aplicación se abrirá en tu navegador en `http://localhost:8501`

## 📚 Paso 5: Usar el Agente

1. **Inicializar Sistema**: Haz clic en "🚀 Inicializar Sistema" en la barra lateral
2. **Procesar PDFs**: Haz clic en "🔄 Procesar/Actualizar PDFs"
3. **Chatear**: Escribe tus preguntas en el chat

### Ejemplos de preguntas:

**RAG (búsqueda en documentos):**
- "Resume el contenido de los documentos"
- "¿Qué dice sobre [tema específico]?"
- "Encuentra información sobre [término]"

**Búsqueda Web:**
- "¿Cuáles son las últimas noticias sobre IA?"
- "Búscame información actualizada sobre [tema]"

**Combinado:**
- "Compara lo que dicen mis documentos con la información actual en internet sobre [tema]"

## 🔧 Solución de Problemas

### Error: "No module named 'vecs'"

```bash
pip install vecs
```

### Error de conexión a Supabase

- Verifica que la URL y API Key sean correctas
- Asegúrate de haber habilitado pgvector
- Verifica que la contraseña de la DB sea correcta

### Error: "Embedding model not found"

El modelo se descarga automáticamente la primera vez. Si falla:

```bash
pip install sentence-transformers --upgrade
```

### PDFs no se procesan

- Verifica que los PDFs estén en la carpeta `docs/`
- Asegúrate de que sean PDFs válidos (no escaneados sin OCR)
- Comprueba los permisos de lectura

## 🎨 Personalización

### Cambiar modelo de embeddings

En `.env`:
```bash
EMBEDDING_MODEL=sentence-transformers/all-mpnet-base-v2
```

Modelos disponibles: https://www.sbert.net/docs/pretrained_models.html

### Cambiar modelo de Gemini

En `.env`:
```bash
GEMINI_MODEL=gemini-1.5-pro
```

### Ajustar tamaño de chunks

En `rag.py`, modifica:
```python
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,      # Reduce para chunks más pequeños
    chunk_overlap=100,   # Ajusta el overlap
)
```

## 🔄 Actualización de PDFs

Para actualizar documentos:
1. Añade/reemplaza PDFs en `docs/`
2. Haz clic en "🔄 Procesar/Actualizar PDFs"

Para empezar de cero:
1. Haz clic en "🗑️ Limpiar Base de Datos"
2. Procesa los documentos de nuevo

## 📊 Monitoreo

Puedes ver los logs en la consola donde ejecutaste `streamlit run app.py`

## 🚀 Próximos Pasos

- [ ] Añadir más herramientas al agente
- [ ] Integrar MCP (Model Context Protocol)
- [ ] Añadir memoria persistente
- [ ] Implementar autenticación
- [ ] Desplegar en la nube

## 💡 Consejos

- Usa PDFs con texto extraíble (no imágenes sin OCR)
- Para documentos grandes, considera aumentar el `chunk_size`
- La primera ejecución será más lenta (descarga modelos)
- Tavily tiene límite de búsquedas gratuitas (1000/mes)

---

¿Necesitas ayuda? Revisa los logs o contacta con el desarrollador.