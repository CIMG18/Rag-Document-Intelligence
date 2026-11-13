# Sistema RAG: Búsqueda y Generación sobre Documentos

Aplicación funcional desarrollada para la práctica: **"Técnicas para ampliar el conocimiento de una Inteligencia Artificial"**.

Permite realizar preguntas sobre un conjunto de documentos corporativos y técnicos propios utilizando **RAG (Retrieval-Augmented Generation)**, recuperando fragmentos semánticamente relevantes, citando fuentes exactas y absteniéndose cuando no dispone de información.

---

## Arquitectura y Tecnologías Utilizadas

- **Lenguaje**: Python 3.9+
- **Interfaz de Usuario**: **Streamlit**
- **Extracción y Chunking**: Algoritmo recursivo con preservación de límites naturales de oraciones y solapamiento (*overlap*) configurable.
- **Base Vectorial y Búsqueda Semántica**: Búsqueda por similitud de coseno en espacio vectorial denso en memoria.
- **Modelos de IA**:
  - **Generación (LLM)**: Google Gemini 1.5 / 2.0 Flash (o fallback local interactivo).
  - **Embeddings**: Google Gemini `text-embedding-004` (o vectorizador TF-IDF con filtrado de stop-words en español en modo offline).

---

## Estructura del Proyecto

```text
código/
├── documents/                               
│   ├── 01_politicas_laborales_acme.md      # Políticas de trabajo remoto, vacaciones y gastos
│   ├── 02_especificaciones_servidor_titan.md # Hardware, memoria, procesadores EPYC
│   ├── 03_protocolo_gestion_incidencias.md # ITIL v4, SLAs, escalamiento L1/L2/L3
│   ├── 04_estandar_desarrollo_seguro.md    # Criptografía, SSDLC, OWASP, SonarQube
│   └── 05_reglamento_academico_posgrados.md # Calificaciones mínimas, tesis, plagio
├── app.py                                   
├── rag_engine.py                            
├── cli_demo.py                              
├── requirements.txt                         
├── .env.example                             
└── README.md                                
```

---

## Instalación y Ejecución

1. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

2. **(Opcional) Configurar clave de Gemini**:
   - Puedes exportar tu variable de entorno:
     ```bash
     export GEMINI_API_KEY="tu_clave_de_gemini"
     ```
   - O bien, puedes ingresarla directamente en el campo de texto de la barra lateral en la interfaz web.

3. **Ejecutar la aplicación**:
   ```bash
   streamlit run app.py
   ```
   *Se abrirá automáticamente en tu navegador en `http://localhost:8501`.*

---

