# Etapa 1: Construcción del Frontend (React/Vite)
FROM node:20-slim AS frontend-builder
WORKDIR /app/frontend

# Copiamos package.json e instalamos dependencias
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

# Copiamos el resto del código fuente del frontend y construimos
COPY frontend/ ./
RUN npm run build

# Etapa 2: Construcción del Backend (FastAPI) y Ensamblaje
FROM python:3.11-slim
WORKDIR /app/backend

# Instalamos dependencias del sistema necesarias (ej. para compilar algunas librerías)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiamos requirements y los instalamos
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos todo el backend (esto incluirá chroma_db ya que no está en .dockerignore)
COPY backend/ ./

# Copiamos los archivos estáticos construidos del frontend hacia /app/frontend/dist
# FastAPI está configurado para buscar el frontend estático un directorio arriba: ../frontend/dist
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist

# Exponemos el puerto (Digital Ocean App Platform inyectará la variable $PORT)
ENV PORT=8000
EXPOSE $PORT

# Comando para correr la aplicación FastAPI, montando el frontend
CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT
