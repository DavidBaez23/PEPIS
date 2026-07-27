import os
from pathlib import Path
import pymupdf4llm

def extract_pdf_to_markdown():
    # Rutas absolutas o relativas al directorio principal
    base_dir = Path(__file__).resolve().parent.parent.parent.parent
    pdf_path = base_dir / "pdfs" / "Proyecto Educativo del Programa (PEP) de Ingenieria de Sistemas - UFPS.pdf"
    output_dir = base_dir / "backend" / "data"
    output_path = output_dir / "pep_sistemas.md"
    
    # Crear directorio si no existe
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Buscando PDF en: {pdf_path}")
    if not pdf_path.exists():
        print("Error: El archivo PDF no existe en la ruta especificada.")
        return
    
    print("Iniciando extracción con pymupdf4llm...")
    # Convertir el PDF a Markdown estructurado
    # pymupdf4llm maneja internamente las tablas de forma óptima
    md_text = pymupdf4llm.to_markdown(str(pdf_path))
    
    print(f"Guardando archivo Markdown en: {output_path}")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(md_text)
        
    print("¡Extracción exitosa!")
    print(f"El archivo markdown se encuentra en: {output_path}")

if __name__ == "__main__":
    extract_pdf_to_markdown()
