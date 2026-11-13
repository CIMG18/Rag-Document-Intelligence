"""
Módulo de Motor RAG (Retrieval-Augmented Generation)
Desarrollado para la práctica: Técnicas para ampliar el conocimiento de una IA.
"""

import os
import math
import json
import re
import urllib.request
import urllib.error
from typing import List, Dict, Any, Tuple, Optional


class Document:
    def __init__(self, name: str, content: str, filepath: str):
        self.name = name
        self.content = content
        self.filepath = filepath


class Chunk:
    def __init__(self, chunk_id: str, text: str, source: str, start_char: int, end_char: int):
        self.chunk_id = chunk_id
        self.text = text
        self.source = source
        self.start_char = start_char
        self.end_char = end_char
        self.embedding: Optional[List[float]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "text": self.text,
            "source": self.source,
            "start_char": self.start_char,
            "end_char": self.end_char,
        }


class LocalTFIDFVectorizer:
    """
    Vectorizador local basado en TF-IDF con filtrado de stop-words en español para modo offline o fallback.
    No requiere dependencias pesadas y permite demostrar la búsqueda vectorial de inmediato.
    """
    STOP_WORDS = {
        "de", "la", "que", "el", "en", "y", "a", "los", "del", "se", "las", "por", "un", "para",
        "con", "no", "una", "su", "al", "lo", "como", "más", "pero", "sus", "le", "ya", "o", "este",
        "sí", "porque", "esta", "entre", "cuando", "muy", "sin", "sobre", "también", "me", "hasta",
        "hay", "donde", "quien", "desde", "todo", "nos", "durante", "todos", "uno", "les", "ni",
        "contra", "otros", "ese", "eso", "ante", "ellos", "e", "esto", "mí", "antes", "algunos",
        "qué", "cuál", "cuáles", "cómo", "dónde", "cuándo", "cuánto", "cuántos", "cuánta", "cuántas",
        "es", "son", "fue", "era", "ser", "estar", "tiene", "tienen", "tengo", "hay"
    }

    def __init__(self):
        self.vocabulary = {}
        self.idf = {}
        self.is_fitted = False

    def _tokenize(self, text: str) -> List[str]:
        words = re.findall(r'\b[a-záéíóúüñA-ZÁÉÍÓÚÜÑ0-9_-]{2,}\b', text.lower())
        # Filtrar stop words
        return [w for w in words if w not in self.STOP_WORDS]

    def fit_transform(self, texts: List[str]) -> List[List[float]]:
        doc_tokens = [self._tokenize(t) for t in texts]
        df = {}
        n_docs = len(texts)

        # Construir vocabulario y Document Frequency (DF)
        for tokens in doc_tokens:
            unique_tokens = set(tokens)
            for token in unique_tokens:
                df[token] = df.get(token, 0) + 1

        self.vocabulary = {token: idx for idx, token in enumerate(df.keys())}
        self.idf = {token: math.log((1 + n_docs) / (1 + count)) + 1.0 for token, count in df.items()}
        self.is_fitted = True

        vectors = []
        for tokens in doc_tokens:
            vec = self._vectorize_tokens(tokens)
            vectors.append(vec)
        return vectors

    def transform(self, texts: List[str]) -> List[List[float]]:
        if not self.is_fitted:
            raise ValueError("El vectorizador debe entrenarse primero con fit_transform().")
        vectors = []
        for text in texts:
            tokens = self._tokenize(text)
            vec = self._vectorize_tokens(tokens)
            vectors.append(vec)
        return vectors

    def _vectorize_tokens(self, tokens: List[str]) -> List[float]:
        vec = [0.0] * len(self.vocabulary)
        tf = {}
        for token in tokens:
            tf[token] = tf.get(token, 0) + 1

        for token, count in tf.items():
            if token in self.vocabulary:
                idx = self.vocabulary[token]
                term_tf = count / max(1, len(tokens))
                vec[idx] = term_tf * self.idf.get(token, 1.0)

        # Normalización L2
        norm = math.sqrt(sum(x * x for x in vec))
        if norm > 0:
            vec = [x / norm for x in vec]
        return vec


def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """Calcula la similitud de coseno entre dos vectores numéricos."""
    if not vec_a or not vec_b or len(vec_a) != len(vec_b):
        return 0.0
    dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot_product / (norm_a * norm_b)


class RAGEngine:
    """
    Motor RAG completo y modular:
    1. Carga de documentos (TXT, MD, PDF).
    2. Fragmentación (Chunking) con tamaño y overlap configurables.
    3. Generación de Embeddings (Gemini text-embedding-004 o Local TF-IDF).
    4. Base de datos vectorial en memoria y búsqueda semántica por similitud de coseno.
    5. Aumentación de contexto y generación con LLM (Gemini 1.5/2.5/2.0 Flash o Local).
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY", "")
        self.documents: List[Document] = []
        self.chunks: List[Chunk] = []
        self.local_vectorizer = LocalTFIDFVectorizer()
        self.use_gemini_embeddings = bool(self.api_key)

    def load_documents_from_directory(self, directory_path: str) -> List[Document]:
        """Lee todos los archivos .md, .txt y .pdf de un directorio."""
        self.documents = []
        if not os.path.exists(directory_path):
            raise FileNotFoundError(f"El directorio '{directory_path}' no existe.")

        for filename in sorted(os.listdir(directory_path)):
            filepath = os.path.join(directory_path, filename)
            if os.path.isdir(filepath):
                continue

            content = ""
            ext = os.path.splitext(filename)[1].lower()

            if ext in [".txt", ".md"]:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
            elif ext == ".pdf":
                try:
                    import pypdf
                    reader = pypdf.PdfReader(filepath)
                    for page in reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            content += page_text + "\n"
                except ImportError:
                    content = f"[Aviso: Instale 'pypdf' para extraer texto de {filename}]"
            else:
                continue

            if content.strip():
                self.documents.append(Document(name=filename, content=content, filepath=filepath))

        return self.documents

    def create_chunks(self, chunk_size: int = 500, chunk_overlap: int = 80) -> List[Chunk]:
        """
        Divide los documentos cargados en fragmentos (chunks) respetando tamaño y solapamiento (overlap).
        """
        self.chunks = []
        if chunk_size <= chunk_overlap:
            chunk_overlap = max(0, chunk_size // 4)

        for doc in self.documents:
            text = doc.content.strip()
            if not text:
                continue

            start = 0
            chunk_idx = 0
            text_len = len(text)

            while start < text_len:
                end = min(start + chunk_size, text_len)

                # Intentar cortar en límite natural de párrafo o punto si es posible
                if end < text_len:
                    boundary = text.rfind("\n", start, end)
                    if boundary != -1 and boundary > start + (chunk_size // 2):
                        end = boundary + 1
                    else:
                        boundary_period = text.rfind(". ", start, end)
                        if boundary_period != -1 and boundary_period > start + (chunk_size // 2):
                            end = boundary_period + 1

                chunk_text = text[start:end].strip()
                if chunk_text:
                    c = Chunk(
                        chunk_id=f"{doc.name}#chunk_{chunk_idx}",
                        text=chunk_text,
                        source=doc.name,
                        start_char=start,
                        end_char=end,
                    )
                    self.chunks.append(c)
                    chunk_idx += 1

                if end >= text_len:
                    break
                start = end - chunk_overlap

        return self.chunks

    def _get_gemini_embedding(self, text: str) -> Optional[List[float]]:
        """Llama a la API de Google Gemini para obtener embeddings de texto."""
        if not self.api_key:
            return None

        url = f"https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:embedContent?key={self.api_key}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "model": "models/text-embedding-004",
            "content": {
                "parts": [{"text": text}]
            }
        }

        try:
            req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=10) as response:
                result = json.loads(response.read().decode("utf-8"))
                return result.get("embedding", {}).get("values", [])
        except Exception as e:
            # Si falla la llamada remota, reportamos el error
            print(f"[Aviso Embeddings] Falló llamada a Gemini: {e}")
            return None

    def build_vector_store(self, prefer_gemini: bool = True) -> int:
        """
        Genera y asocia embeddings para todos los fragmentos creados.
        Si hay API Key de Gemini y prefer_gemini=True, intenta usar text-embedding-004.
        En caso contrario o si falla, usa el vectorizador semántico local.
        """
        if not self.chunks:
            return 0

        self.use_gemini_embeddings = False
        texts = [c.text for c in self.chunks]

        if prefer_gemini and self.api_key:
            try:
                # Probar con el primer chunk para verificar conectividad
                test_emb = self._get_gemini_embedding(texts[0][:200])
                if test_emb and len(test_emb) > 0:
                    self.chunks[0].embedding = test_emb
                    for i in range(1, len(self.chunks)):
                        emb = self._get_gemini_embedding(self.chunks[i].text)
                        self.chunks[i].embedding = emb
                    self.use_gemini_embeddings = True
                    return len(self.chunks)
            except Exception as e:
                print(f"[Fallback] Conmutando a vectorizador local: {e}")

        # Vectorizador local como fallback robusto
        vectors = self.local_vectorizer.fit_transform(texts)
        for i, chunk in enumerate(self.chunks):
            chunk.embedding = vectors[i]
        self.use_gemini_embeddings = False
        return len(self.chunks)

    def search(self, query: str, top_k: int = 3, min_similarity: float = 0.05) -> List[Tuple[Chunk, float]]:
        """
        Realiza búsqueda semántica: vectoriza la consulta y calcula la similitud con cada fragmento.
        Retorna una lista ordenada de (Chunk, score) con los mejores candidatos.
        """
        if not self.chunks or not query.strip():
            return []

        if self.use_gemini_embeddings and self.api_key:
            query_vec = self._get_gemini_embedding(query)
            if not query_vec:
                query_vec = self.local_vectorizer.transform([query])[0]
        else:
            query_vec = self.local_vectorizer.transform([query])[0]

        scored_chunks: List[Tuple[Chunk, float]] = []
        for chunk in self.chunks:
            if chunk.embedding is not None:
                score = cosine_similarity(query_vec, chunk.embedding)
                if score >= min_similarity:
                    scored_chunks.append((chunk, score))

        # Ordenar de mayor a menor similitud
        scored_chunks.sort(key=lambda x: x[1], reverse=True)
        return scored_chunks[:top_k]

    def _call_gemini_llm(self, prompt: str) -> str:
        """Llama a Gemini 1.5 Flash (o 2.0 / 2.5 Flash) para generar la respuesta."""
        if not self.api_key:
            return ""

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.api_key}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ],
            "generationConfig": {
                "temperature": 0.1,
                "maxOutputTokens": 800,
            }
        }

        try:
            req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=15) as response:
                result = json.loads(response.read().decode("utf-8"))
                candidates = result.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts:
                        return parts[0].get("text", "").strip()
        except Exception as e:
            # Probar modelo gemini-2.0-flash o reportar error
            try:
                url_fallback = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={self.api_key}"
                req = urllib.request.Request(url_fallback, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
                with urllib.request.urlopen(req, timeout=15) as response:
                    result = json.loads(response.read().decode("utf-8"))
                    candidates = result.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts:
                            return parts[0].get("text", "").strip()
            except Exception as e2:
                return f"[Error llamando al API de Gemini: {e2}]"

        return "No fue posible generar una respuesta con el modelo."

    def answer_query(self, query: str, top_k: int = 3, min_similarity: float = 0.08) -> Dict[str, Any]:
        """
        Pipeline RAG completo:
        1. Recuperación de fragmentos relevantes (Retrieval).
        2. Construcción de Prompt Aumentado (Augmentation).
        3. Generación condicionada de respuesta con detección de abstención (Generation).
        """
        results = self.search(query, top_k=top_k, min_similarity=min_similarity)

        # Si ningún fragmento superó el umbral de similitud
        if not results:
            return {
                "answer": "No dispongo de información suficiente en los documentos para responder a esta pregunta.",
                "sources": [],
                "has_context": False,
                "mode": "Sin coincidencias semánticas relevantes"
            }

        # Construir el bloque de contexto numerado con sus fuentes
        context_blocks = []
        sources = []
        for i, (chunk, score) in enumerate(results, start=1):
            context_blocks.append(f"--- FRAGMENTO {i} [Fuente: {chunk.source} | Score: {score:.3f}] ---\n{chunk.text}")
            sources.append({
                "source": chunk.source,
                "score": round(score, 4),
                "text": chunk.text,
                "chunk_id": chunk.chunk_id
            })

        context_str = "\n\n".join(context_blocks)

        system_instructions = (
            "Eres un asistente de Inteligencia Artificial especializado en responder preguntas con base EXCLUSIVA en los fragmentos de contexto proporcionados.\n\n"
            "REGLAS OBLIGATORIAS:\n"
            "1. Responde de forma clara, directa y estructurada utilizando ÚNICAMENTE la información explícita de los fragmentos de contexto.\n"
            "2. Si la información necesaria para responder la pregunta NO está presente en los fragmentos, responde EXACTAMENTE: "
            "'No dispongo de información suficiente en los documentos para responder a esta pregunta.' (No intentes inventar ni especular).\n"
            "3. Siempre cita el nombre del documento fuente de donde obtuviste los datos.\n"
            "4. Sé profesional, conciso y preciso."
        )

        user_prompt = (
            f"{system_instructions}\n\n"
            f"CONTEXTO RECUPERADO:\n{context_str}\n\n"
            f"PREGUNTA DEL USUARIO:\n{query}\n\n"
            f"RESPUESTA:"
        )

        if self.api_key:
            answer = self._call_gemini_llm(user_prompt)
            mode = "Gemini LLM (Online)"
        else:
            # Modo explicativo local / demostración
            best_chunk, best_score = results[0]
            answer = (
                f"[Modo Local / Demostración]: Se recuperaron {len(results)} fragmentos relevantes.\n\n"
                f"Mejor coincidencia ({best_chunk.source}, relevancia: {best_score:.2%}):\n"
                f"> \"{best_chunk.text[:220]}...\"\n\n"
                f"ℹ️ Ingrese su clave de API de Gemini en la barra lateral para generar la respuesta sintética completa con el LLM."
            )
            mode = "Local / Extractive Fallback"

        return {
            "answer": answer,
            "sources": sources,
            "has_context": True,
            "mode": mode,
            "prompt_used": user_prompt
        }
