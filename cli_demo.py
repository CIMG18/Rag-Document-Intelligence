#!/usr/bin/env python3
"""
Demostración interactiva por consola del Motor RAG.
Permite probar la carga de documentos, chunking, búsqueda semántica y generación
directamente en la terminal con cero dependencias externas obligatorias.
"""

import os
import sys
from rag_engine import RAGEngine

def main():
    print("=" * 70)
    print("🧠 DEMOSTRACIÓN DE MOTOR RAG (SISTEMA DE PREGUNTAS SOBRE DOCUMENTOS)")
    print("=" * 70)

    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        print("ℹ️ Variable GEMINI_API_KEY no detectada.")
        key_input = input("¿Deseas ingresar una clave de API de Gemini? (Presiona Enter para omitir y usar modo local): ").strip()
        if key_input:
            api_key = key_input

    engine = RAGEngine(api_key=api_key)
    docs_folder = os.path.join(os.path.dirname(__file__), "documents")

    print(f"\n[1] Cargando documentos desde: {docs_folder}...")
    docs = engine.load_documents_from_directory(docs_folder)
    print(f"    -> Se cargaron {len(docs)} documentos exitosamente:")
    for d in docs:
        print(f"       • {d.name} ({len(d.content)} caracteres)")

    print("\n[2] Aplicando Chunking (tamaño: 450 caracteres, overlap: 70 caracteres)...")
    chunks = engine.create_chunks(chunk_size=450, chunk_overlap=70)
    print(f"    -> Se generaron {len(chunks)} fragmentos (chunks) en total.")

    print("\n[3] Construyendo base vectorial e indexando embeddings...")
    engine.build_vector_store(prefer_gemini=bool(api_key))
    modo = "Gemini API (text-embedding-004)" if engine.use_gemini_embeddings else "Vectorizador Semántico Local (TF-IDF + Coseno)"
    print(f"    -> Modo de embeddings activo: {modo}")

    print("\n" + "=" * 70)
    print("SISTEMA LISTO PARA RECIBIR PREGUNTAS")
    print("Escribe tus preguntas sobre los documentos cargados.")
    print("Escribe 'salir' para terminar la demostración.")
    print("=" * 70)

    ejemplos_sugeridos = [
        "¿Cuántos días de vacaciones me corresponden al año?",
        "¿Cuáles son las especificaciones de memoria y CPU del servidor Titan?",
        "¿Cuál es el tiempo máximo de mitigación para incidencias de Severidad 1?",
        "¿Qué algoritmo de cifrado se exige para datos en reposo?",
        "¿Cuál es la calificación mínima aprobatoria en el reglamento de posgrado?",
        "¿Cómo preparar un cóctel margarita? (Prueba de abstención fuera de dominio)"
    ]

    print("\nPreguntas sugeridas que puedes probar:")
    for i, ej in enumerate(ejemplos_sugeridos, 1):
        print(f"  {i}. {ej}")

    while True:
        print("\n" + "-" * 70)
        query = input("❓ Ingresa tu pregunta: ").strip()
        if not query:
            continue
        if query.lower() in ["salir", "exit", "quit"]:
            print("Cerrando sesión del sistema RAG. ¡Hasta pronto!")
            break

        print("\n🔍 Buscando información relevante...")
        res = engine.answer_query(query, top_k=3, min_similarity=0.08)

        print("\n💡 RESPUESTA:")
        print(res["answer"])

        if res["sources"]:
            print("\n📑 FUENTES RECUPERADAS (EVIDENCIA):")
            for i, src in enumerate(res["sources"], 1):
                print(f"  [{i}] Documento: {src['source']} | Similitud: {src['score']:.4f}")
                print(f"      Fragmento: \"{src['text'][:160].strip()}...\"")
        else:
            print("\nℹ️ No se encontraron fragmentos relevantes que superen el umbral.")

if __name__ == "__main__":
    main()
