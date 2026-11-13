import os
import streamlit as st
from rag_engine import RAGEngine

# Configuración de página
st.set_page_config(
    page_title="RAG Explorer - Práctica de Conocimiento en IA",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos personalizados sutiles
st.markdown("""
<style>
    .main-header {
        font-size: 2.1rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
    .badge-source {
        background-color: #E0E7FF;
        color: #3730A3;
        padding: 0.2rem 0.6rem;
        border-radius: 9999px;
        font-size: 0.82rem;
        font-weight: 600;
    }
    .score-badge {
        background-color: #D1FAE5;
        color: #065F46;
        padding: 0.2rem 0.5rem;
        border-radius: 6px;
        font-size: 0.8rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Inicialización en st.session_state
if "engine" not in st.session_state:
    st.session_state.engine = RAGEngine()
    st.session_state.is_indexed = False
    st.session_state.chat_history = []

# Sidebar de Configuración
with st.sidebar:
    st.title("⚙️ Configuración del RAG")
    
    st.subheader("1. Conexión con LLM")
    api_key_input = st.text_input(
        "Google Gemini API Key",
        value=os.environ.get("GEMINI_API_KEY", ""),
        type="password",
        help="Obtén tu API key gratuita en Google AI Studio (aistudio.google.com). Si se deja vacía, el sistema funciona en modo demostración local."
    )
    
    if api_key_input != st.session_state.engine.api_key:
        st.session_state.engine.api_key = api_key_input
        st.session_state.engine.use_gemini_embeddings = bool(api_key_input)
    
    if st.session_state.engine.api_key:
        st.success("🟢 Modo En Línea: Gemini LLM Activo")
    else:
        st.info("🟡 Modo Demostración Local (Sin API Key)")
        st.caption("Recupera fragmentos semánticos reales y simula la respuesta para demostraciones sin conexión.")

    st.markdown("---")
    st.subheader("2. Parámetros de Fragmentación")
    chunk_size = st.slider("Tamaño de Chunk (caracteres)", min_value=200, max_value=1000, value=450, step=50)
    chunk_overlap = st.slider("Solapamiento / Overlap (caracteres)", min_value=20, max_value=200, value=70, step=10)
    top_k = st.slider("Top-K Fragmentos a Recuperar", min_value=1, max_value=5, value=3)
    min_similarity = st.slider("Umbral de Similitud Mínima", min_value=0.0, max_value=0.5, value=0.08, step=0.02)

    st.markdown("---")
    st.subheader("3. Indexación")
    docs_folder = os.path.join(os.path.dirname(__file__), "documents")
    
    if st.button("🔄 Cargar e Indexar Documentos", use_container_width=True) or not st.session_state.is_indexed:
        with st.spinner("Procesando documentos y calculando vectores..."):
            docs = st.session_state.engine.load_documents_from_directory(docs_folder)
            chunks = st.session_state.engine.create_chunks(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
            st.session_state.engine.build_vector_store(prefer_gemini=bool(st.session_state.engine.api_key))
            st.session_state.is_indexed = True
            st.success(f"Indexados: {len(docs)} documentos en {len(chunks)} chunks.")

    if st.session_state.is_indexed:
        st.caption(f"📁 Documentos activos: {len(st.session_state.engine.documents)}")
        st.caption(f"🧩 Chunks generados: {len(st.session_state.engine.chunks)}")

# Encabezado Principal
st.markdown('<div class="main-header">🧠 Sistema RAG: Búsqueda y Generación sobre Documentos</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Demostración práctica de Recuperación de Información Aumentada con IA sobre base documental propia.</div>', unsafe_allow_html=True)

tab_chat, tab_docs, tab_arch = st.tabs(["💬 Consultas y Preguntas", "📑 Explorador de Chunks", "🏛️ Arquitectura y Funcionamiento"])

# PESTAÑA 1: CHAT Y CONSULTAS
with tab_chat:
    col_preguntas, col_resultados = st.columns([1, 1.3], gap="medium")
    
    with col_preguntas:
        st.subheader("Haz una pregunta al sistema")
        st.markdown("Selecciona una pregunta de prueba o escribe una personalizada:")
        
        # Preguntas sugeridas para la exposición
        ejemplos = [
            "¿Cuántos días de vacaciones tengo al cumplir un año en Acme?",
            "¿Qué modelo de procesador y cuánta RAM tiene el servidor Titan?",
            "¿Cuál es el SLA y tiempo máximo de mitigación para incidencias Severidad 1?",
            "¿Qué algoritmo de cifrado se exige para datos en reposo?",
            "¿Cuál es la calificación mínima aprobatoria en el posgrado?",
            "¿Cómo se prepara una paella valenciana tradicional? (Pregunta trampa)"
        ]
        
        pregunta_seleccionada = None
        for i, ej in enumerate(ejemplos):
            if st.button(f"📌 {ej}", key=f"btn_ej_{i}", use_container_width=True):
                pregunta_seleccionada = ej

        query_text = st.text_area(
            "O escribe tu propia pregunta:",
            value=pregunta_seleccionada if pregunta_seleccionada else "",
            placeholder="Ejemplo: ¿Qué requisitos se piden para la tesis doctoral?",
            height=90
        )
        
        btn_consultar = st.button("🚀 Enviar Consulta", type="primary", use_container_width=True)

    with col_resultados:
        st.subheader("Respuesta y Evidencia Documental")
        
        if btn_consultar and query_text.strip():
            with st.spinner("Buscando en la base vectorial y generando respuesta..."):
                resultado = st.session_state.engine.answer_query(
                    query=query_text.strip(),
                    top_k=top_k,
                    min_similarity=min_similarity
                )
            
            # Mostrar Respuesta
            st.markdown("#### 💡 Respuesta Generada:")
            if "No dispongo de información suficiente" in resultado["answer"]:
                st.warning(f"⚠️ **{resultado['answer']}**")
                st.info("ℹ️ *El sistema detectó que la consulta está fuera del conocimiento presente en los documentos y se abstuvo de alucinar.*")
            else:
                st.markdown(f"> {resultado['answer']}")
                st.caption(f"Modo de ejecución: `{resultado['mode']}`")

            st.markdown("---")
            st.markdown("#### 🔍 Fragmentos Recuperados (Evidencia / Fuentes):")
            
            if not resultado["sources"]:
                st.write("No se encontraron fragmentos que superen el umbral de similitud.")
            else:
                for idx, src in enumerate(resultado["sources"], start=1):
                    relevancia_pct = src["score"] * 100
                    with st.expander(f"Fuente #{idx}: {src['source']} (Similitud: {relevancia_pct:.1f}%)", expanded=(idx == 1)):
                        st.markdown(f"**ID de Fragmento:** `{src['chunk_id']}`")
                        st.markdown(f"**Relevancia Coseno:** `{src['score']:.4f}`")
                        st.markdown(f"**Texto Recuperado:**")
                        st.info(src["text"])

# PESTAÑA 2: EXPLORADOR DE DOCUMENTOS Y CHUNKS
with tab_docs:
    st.subheader("📑 Documentos Cargados en el Sistema")
    if not st.session_state.engine.documents:
        st.warning("No hay documentos cargados. Haz clic en 'Cargar e Indexar Documentos' en la barra lateral.")
    else:
        st.write(f"Total de documentos en la carpeta `documents/`: **{len(st.session_state.engine.documents)}**")
        doc_names = [d.name for d in st.session_state.engine.documents]
        selected_doc_name = st.selectbox("Selecciona un documento para inspeccionar su fragmentación:", doc_names)
        
        doc_obj = next(d for d in st.session_state.engine.documents if d.name == selected_doc_name)
        chunks_doc = [c for c in st.session_state.engine.chunks if c.source == selected_doc_name]
        
        col_doc_orig, col_doc_chunks = st.columns([1, 1], gap="medium")
        
        with col_doc_orig:
            st.markdown(f"**Contenido Original Completo** ({len(doc_obj.content)} caracteres):")
            st.text_area("Texto original", doc_obj.content, height=450, disabled=True)
            
        with col_doc_chunks:
            st.markdown(f"**Fragmentos Generados (Chunks)**: {len(chunks_doc)} fragmentos")
            for c in chunks_doc:
                with st.expander(f"🧩 {c.chunk_id} ({c.end_char - c.start_char} car.)"):
                    st.code(c.text, language="markdown")

# PESTAÑA 3: ARQUITECTURA Y EXPLICACIÓN
with tab_arch:
    st.subheader("🏛️ Arquitectura del Sistema RAG Implementado")
    
    st.markdown("""
    El patrón **RAG (Retrieval-Augmented Generation)** amplía el conocimiento de un modelo de IA sin alterar sus pesos internos, combinando un recuperador de información y un modelo generativo.
    """)
    
    st.markdown("""
    ```mermaid
    flowchart TD
        subgraph FASE_1["1. Indexación (Offline / Ingesta)"]
            D["Documentos Corporativos (MD, TXT, PDF)"] --> CH["Chunking (División en fragmentos con solapamiento)"]
            CH --> EMB["Modelo de Embeddings (Vectorización Semántica)"]
            EMB --> VDB[("Base de Datos Vectorial")]
        end

        subgraph FASE_2["2. Recuperación y Generación (Online / Consulta)"]
            Q["Pregunta del Usuario"] --> Q_EMB["Vectorizar Pregunta (Embedding)"]
            Q_EMB --> VSEARCH["Búsqueda de Similitud Coseno"]
            VDB -.-> VSEARCH
            VSEARCH --> TOPK["Top-K Fragmentos Relevantes"]
            TOPK --> PROMPT["Construcción del Prompt con Contexto y Reglas de Abstención"]
            Q --> PROMPT
            PROMPT --> LLM["LLM (Gemini 1.5 / 2.0 Flash)"]
            LLM --> ANS["Respuesta Verificable + Cita de Fuentes"]
        end
    ```
    """)
    
    col_t1, col_t2, col_t3 = st.columns(3)
    with col_t1:
        st.markdown("### 1. Chunking")
        st.write("Consiste en dividir textos extensos en bloques manejables. Un tamaño adecuado (`chunk_size`) y un solapamiento (`chunk_overlap`) evitan perder contexto entre oraciones consecutivas.")
    with col_t2:
        st.markdown("### 2. Embeddings")
        st.write("Transforman texto en vectores densos de números reales en un espacio multidimensional donde textos con significado semántico afín quedan geométricamente cercanos.")
    with col_t3:
        st.markdown("### 3. Búsqueda Semántica")
        st.write("Calcula el ángulo entre el vector de la pregunta y los vectores de los chunks mediante la **similitud de coseno**, permitiendo encontrar respuestas aunque no compartan exactamente las mismas palabras.")
