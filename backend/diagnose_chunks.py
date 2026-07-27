"""Diagnóstico: verificar que el nuevo ingest_chroma.py produce chunks correctos."""
import re
from pathlib import Path
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

base_dir = Path(__file__).resolve().parent.parent
md_path = base_dir / "backend" / "data" / "pep_sistemas.md"

with open(md_path, "r", encoding="utf-8") as f:
    text = f.read()

# Pre-procesamiento (mismo que ingest_chroma.py)
lines = text.split('\n')
processed_lines = []
for line in lines:
    match = re.match(
        r'^- \*\*(\d+\.\d+\.?\d*\.?)\*\*\s*\*\*_?(.+?)_?\*\*\s*(.*)',
        line
    )
    if match:
        section_num = match.group(1).strip('.')
        title = match.group(2).strip()
        rest = match.group(3).strip()
        processed_lines.append(f"### **{section_num}. {title}**")
        if rest:
            rest = rest.lstrip('. ')
            if rest:
                processed_lines.append("")
                processed_lines.append(rest)
        print(f"  CONVERTIDO: {line[:80]}...")
        print(f"  ->  ### **{section_num}. {title}**")
    else:
        processed_lines.append(line)

markdown_document = '\n'.join(processed_lines)
markdown_document = markdown_document.replace('<br>', ' ')

# Splitting
headers_to_split_on = [
    ("#", "Header 1"),
    ("##", "Header 2"),
    ("###", "Header 3"),
]

markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
md_header_splits = markdown_splitter.split_text(markdown_document)

print(f"\nTotal splits after MarkdownHeaderTextSplitter: {len(md_header_splits)}")

# Find the competencies split
for i, doc in enumerate(md_header_splits):
    if "CE1" in doc.page_content or "CE3" in doc.page_content:
        print(f"\n--- HEADER SPLIT #{i} (len={len(doc.page_content)}) ---")
        print(f"METADATA: {doc.metadata}")
        print(f"Contiene CE1: {'CE1' in doc.page_content}")
        print(f"Contiene CE2: {'CE2' in doc.page_content}")
        print(f"Contiene CE3: {'CE3' in doc.page_content}")
        print(f"CONTENIDO:\n{doc.page_content[:1500]}")
        if len(doc.page_content) > 1500:
            print("...")

# Secondary split
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=2000, chunk_overlap=300,
    separators=["\n\n", "\n", " ", ""],
    keep_separator=True
)
splits = text_splitter.split_documents(md_header_splits)
print(f"\nTotal after RecursiveCharacterTextSplitter: {len(splits)}")

print("\n" + "=" * 80)
print("CHUNKS FINALES con competencias específicas:")
print("=" * 80)

for i, doc in enumerate(splits):
    if "CE1" in doc.page_content or "CE3" in doc.page_content:
        print(f"\n--- FINAL CHUNK #{i} (len={len(doc.page_content)}) ---")
        print(f"METADATA: {doc.metadata}")
        print(f"Contiene CE1: {'CE1' in doc.page_content}")
        print(f"Contiene CE2: {'CE2' in doc.page_content}")
        print(f"Contiene CE3: {'CE3' in doc.page_content}")
        print(f"CONTENIDO:\n{doc.page_content[:1000]}")
        if len(doc.page_content) > 1000:
            print("...")
