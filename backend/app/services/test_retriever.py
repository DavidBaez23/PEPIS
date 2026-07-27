import sys
from pathlib import Path
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

def test_retrieval():
    base_dir = Path(__file__).resolve().parent.parent.parent.parent
    chroma_dir = base_dir / "backend" / "chroma_db"
    
    if not chroma_dir.exists():
        print("La base de datos vectorial no existe. Ejecuta ingest_chroma.py primero.")
        return

    print("Inicializando modelo de Embeddings...")
    embeddings = HuggingFaceEmbeddings(model_name="paraphrase-multilingual-MiniLM-L12-v2")
    
    print("Cargando ChromaDB...")
    vectorstore = Chroma(
        persist_directory=str(chroma_dir),
        embedding_function=embeddings
    )
    
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    
    queries = [
        "¿ Cuantas electivas profesionales debo realizar para graduarme ?",
        "¿ Cuales son las competencias especificas del programa ?"
    ]
    
    for query in queries:
        print("\n" + "="*50)
        print(f"Buscando: '{query}'")
        print("="*50)
        
        docs = retriever.invoke(query)
        
        if not docs:
            print("No se encontraron fragmentos relevantes.")
        
        for i, doc in enumerate(docs):
            print(f"\n[Fragmento {i+1}]")
            print(f"Metadata: {doc.metadata}")
            print("-" * 20)
            # Imprimir solo los primeros 300 caracteres para no saturar la consola
            print(doc.page_content[:300] + "...")

if __name__ == "__main__":
    test_retrieval()
