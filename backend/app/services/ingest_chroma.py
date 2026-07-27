import os
import re
from pathlib import Path
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

def preprocess_markdown(text: str) -> str:
    """
    Pre-procesa el markdown extraído del PEP para corregir problemas estructurales.
    
    El PDF extraído tiene sub-secciones como '- **2.8.2.** **_Título_**' que son
    ítems de lista en vez de headers markdown. Esto provoca que el
    MarkdownHeaderTextSplitter no los reconozca y genere chunks enormes
    donde la información relevante queda diluida o cortada.
    
    Esta función convierte esos patrones a headers `###` reales.
    """
    lines = text.split('\n')
    processed_lines = []
    
    for line in lines:
        # Patrón: líneas que empiezan con "- **X.Y.Z.**" seguido de título
        # Ejemplo: - **2.8.2.** **_Competencias Específicas del Programa_** . Son aquellas...
        match = re.match(
            r'^- \*\*(\d+\.\d+\.?\d*\.?)\*\*\s*\*\*_?(.+?)_?\*\*\s*(.*)',
            line
        )
        if match:
            section_num = match.group(1).strip('.')
            title = match.group(2).strip()
            rest = match.group(3).strip()
            # Convertir a header ### con el contenido restante como párrafo aparte
            processed_lines.append(f"### **{section_num}. {title}**")
            if rest:
                # Quitar punto inicial si existe
                rest = rest.lstrip('. ')
                if rest:
                    processed_lines.append("")
                    processed_lines.append(rest)
        else:
            processed_lines.append(line)
    
    result = '\n'.join(processed_lines)
    
    # Limpiar etiquetas <br> en tablas para mejorar legibilidad y búsqueda semántica
    # Reemplazar <br> por espacio para que las celdas sean texto continuo
    result = result.replace('<br>', ' ')
    
    return result


def ingest_to_chroma():
    base_dir = Path(__file__).resolve().parent.parent.parent.parent
    md_path = base_dir / "backend" / "data" / "pep_sistemas.md"
    chroma_dir = base_dir / "backend" / "chroma_db"
    
    print(f"Cargando archivo: {md_path}")
    with open(md_path, "r", encoding="utf-8") as f:
        markdown_document = f.read()

    # Pre-procesar para convertir sub-secciones de lista a headers reales
    print("Pre-procesando markdown (convirtiendo sub-secciones a headers)...")
    markdown_document = preprocess_markdown(markdown_document)
    
    # Verificar que el pre-procesamiento funcionó
    if "### **2.8.2" in markdown_document:
        print("  ✓ Sección 2.8.2 (Competencias Específicas) convertida a header ###")
    if "### **2.8.1" in markdown_document:
        print("  ✓ Sección 2.8.1 (Competencias Genéricas) convertida a header ###")

    # Los headers en el markdown extraído tienen formatos como ## **1.1...** 
    # El splitter de markdown usa el número de #.
    headers_to_split_on = [
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
    ]
    
    print("Iniciando partición semántica (MarkdownHeaderTextSplitter)...")
    markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
    md_header_splits = markdown_splitter.split_text(markdown_document)
    
    # En caso de que algunos bloques sean demasiado grandes, aplicamos un Recursive secundario.
    # Usamos separadores que respetan tablas markdown: primero doble salto de línea,
    # luego salto de línea simple (pero no entre filas de tabla).
    chunk_size = 2000
    chunk_overlap = 300
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""],
        # No cortar en medio de una línea de tabla
        keep_separator=True
    )
    
    splits = text_splitter.split_documents(md_header_splits)
    print(f"Total de fragmentos generados: {len(splits)}")
    
    # Mostrar algunos chunks clave para verificación
    for i, doc in enumerate(splits):
        if "CE1" in doc.page_content and "CE3" in doc.page_content:
            print(f"\n  ✓ Chunk #{i} contiene CE1 + CE3 juntos (len={len(doc.page_content)})")
            print(f"    Metadata: {doc.metadata}")
            print(f"    Preview: {doc.page_content[:150]}...")
            break
    else:
        # Si no están juntos, buscar por separado
        for i, doc in enumerate(splits):
            if "CE1" in doc.page_content or "CE3" in doc.page_content:
                print(f"\n  → Chunk #{i}: {'CE1' if 'CE1' in doc.page_content else ''} {'CE3' if 'CE3' in doc.page_content else ''} (len={len(doc.page_content)})")
                print(f"    Metadata: {doc.metadata}")
    
    print("\nInicializando modelo de Embeddings (sentence-transformers)...")
    # Usamos un modelo ligero, rápido y en español/multilenguaje si es posible. 
    embeddings = HuggingFaceEmbeddings(model_name="paraphrase-multilingual-MiniLM-L12-v2")
    
    print(f"Ingestando a ChromaDB en: {chroma_dir}")
    vectorstore = Chroma.from_documents(
        documents=splits, 
        embedding=embeddings, 
        persist_directory=str(chroma_dir)
    )
    
    print("¡Ingesta completada correctamente!")

if __name__ == "__main__":
    ingest_to_chroma()
