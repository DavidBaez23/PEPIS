from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.models.chat import ChatRequest, ChatResponse
from app.services.rag_service import rag_service

app = FastAPI(
    title="PEPIS API",
    description="API para el Asistente Virtual del PEP de Ingeniería de Sistemas UFPS",
    version="1.0.0"
)

# Configurar CORS para permitir que el Frontend (React) se comunique
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # En producción se debe limitar a la URL del frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Bienvenido a la API de PEPIS. Usa /docs para ver la documentación."}

@app.post("/api/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    try:
        if not request.query.strip():
            raise HTTPException(status_code=400, detail="La consulta no puede estar vacía")
            
        result = rag_service.ask(request.query, request.history)
        return ChatResponse(
            answer=result["answer"],
            sources=result["sources"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")
