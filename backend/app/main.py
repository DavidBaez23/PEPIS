from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
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

# Ruta absoluta a la carpeta dist del frontend
# __file__ = backend/app/main.py → .parent = backend/app → .parent = backend → .parent = raíz del proyecto
frontend_dist = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"

if frontend_dist.exists():
    app.mount("/assets", StaticFiles(directory=str(frontend_dist / "assets")), name="assets")
    
    @app.get("/")
    def serve_react_app():
        return FileResponse(str(frontend_dist / "index.html"))
    
    # Manejar rutas de React Router (opcional si luego se agregan)
    @app.get("/{catchall:path}")
    def serve_react_app_fallback(catchall: str):
        if not catchall.startswith("api/"):
            return FileResponse(str(frontend_dist / "index.html"))
else:
    @app.get("/")
    def read_root():
        return {"message": "Bienvenido a la API de PEPIS. Frontend no encontrado."}

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
