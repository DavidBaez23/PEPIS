from pathlib import Path
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from app.core.config import settings

class RAGService:
    def __init__(self):
        base_dir = Path(__file__).resolve().parent.parent.parent.parent
        chroma_dir = base_dir / "backend" / "chroma_db"
        
        # Usar el mismo modelo multilingüe para consistencia
        self.embeddings = HuggingFaceEmbeddings(model_name="paraphrase-multilingual-MiniLM-L12-v2")
        
        # Cargar la base de datos de manera dinámica (acepta que se hayan ingerido nuevos docs a futuro)
        self.vectorstore = Chroma(
            persist_directory=str(chroma_dir),
            embedding_function=self.embeddings
        )
        self.retriever = self.vectorstore.as_retriever(search_kwargs={"k": 6})
        
        # Configurar LLM a través de OpenRouter
        self.llm = ChatOpenAI(
            openai_api_base="https://openrouter.ai/api/v1",
            openai_api_key=settings.OPENROUTER_API_KEY,
            model_name=settings.LLM_MODEL,
            max_tokens=settings.MAX_TOKENS,
            temperature=0.0
        )
        
        # Prompt Estricto del Sistema
        system_template = """Eres PEPIS, el Asistente Virtual Oficial del programa de Ingeniería de Sistemas de la UFPS.
Tu única fuente de verdad es el siguiente contexto extraído de los documentos oficiales (como el PEP).
Debes responder OBLIGATORIAMENTE en ESPAÑOL.

INSTRUCCIONES CRÍTICAS:
- Si la pregunta pide listar elementos (competencias, asignaturas, etc.), lista TODOS los que aparezcan en el contexto sin omitir ninguno.
- El contexto puede incluir tablas en formato Markdown (filas delimitadas por |). Analiza cuidadosamente TODAS las filas y columnas.
- Si la información está en una tabla, extrae y presenta CADA fila como un elemento separado.
- No inventes información, no alucines.
- Si la pregunta no puede responderse con el contexto proporcionado, di amablemente que la información no se encuentra en la base de conocimientos actual.

Contexto:
{context}

Pregunta del usuario: {question}"""
        
        self.prompt = ChatPromptTemplate.from_template(system_template)
        
        # Pipeline RAG
        def format_docs(docs):
            """Formatea documentos incluyendo metadata de sección para dar contexto."""
            formatted = []
            for doc in docs:
                header_info = ""
                if doc.metadata:
                    headers = [v for k, v in sorted(doc.metadata.items()) if k.startswith("Header")]
                    if headers:
                        header_info = f"[Sección: {' > '.join(headers)}]\n"
                formatted.append(f"{header_info}{doc.page_content}")
            return "\n\n---\n\n".join(formatted)
            
        self.rag_chain = (
            {"context": self.retriever | format_docs, "question": RunnablePassthrough()}
            | self.prompt
            | self.llm
            | StrOutputParser()
        )

    def ask(self, query: str) -> dict:
        # Recuperar fuentes para devolverlas en la API
        docs = self.retriever.invoke(query)
        sources = [{"content": d.page_content[:200], "metadata": d.metadata} for d in docs]
        
        # Generar respuesta
        answer = self.rag_chain.invoke(query)
        
        return {
            "answer": answer,
            "sources": sources
        }

rag_service = RAGService()
