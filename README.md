# PEPIS - Asistente Virtual del Programa de Ingenieria de Sistemas (UFPS)

PEPIS es un asistente virtual basado en Inteligencia Artificial que responde preguntas sobre el Proyecto Educativo del Programa (PEP) de Ingenieria de Sistemas de la Universidad Francisco de Paula Santander (UFPS). Utiliza una arquitectura RAG (Retrieval-Augmented Generation) para consultar una base de conocimiento vectorizada y generar respuestas precisas fundamentadas exclusivamente en los documentos oficiales del programa.

---

## Tabla de Contenidos

1. [Descripcion del Proyecto](#descripcion-del-proyecto)
2. [Publico Objetivo](#publico-objetivo)
3. [Arquitectura del Sistema](#arquitectura-del-sistema)
4. [Tipo de Preguntas que Responde](#tipo-de-preguntas-que-responde)
5. [Ejecucion en Local](#ejecucion-en-local)
6. [Despliegue](#despliegue)

---

## Descripcion del Proyecto

PEPIS nace como respuesta a la necesidad de facilitar el acceso a la informacion contenida en el Proyecto Educativo del Programa (PEP) de Ingenieria de Sistemas de la UFPS. Este documento, extenso y tecnico, contiene toda la informacion curricular, normativa y estrategica del programa academico. PEPIS permite a los usuarios realizar consultas en lenguaje natural y obtener respuestas contextualizadas, eliminando la necesidad de buscar manualmente dentro del documento.

El sistema se compone de dos partes principales:

- **Backend (FastAPI + LangChain):** Un servidor que recibe las preguntas del usuario, busca los fragmentos mas relevantes del PEP en una base de datos vectorial (ChromaDB) y los envia a un modelo de lenguaje (LLM) a traves de OpenRouter para generar una respuesta coherente.
- **Frontend (React + Vite):** Una interfaz de chat limpia y funcional donde el usuario escribe sus preguntas y recibe las respuestas del asistente en tiempo real.

---

## Publico Objetivo

PEPIS esta dirigido a:

- **Estudiantes activos** del programa de Ingenieria de Sistemas que deseen consultar informacion sobre el plan de estudios, competencias, perfiles de egreso, entre otros.
- **Aspirantes** que quieran conocer los detalles del programa antes de inscribirse.
- **Docentes y directivos** del programa que necesiten acceder rapidamente a informacion normativa o curricular contenida en el PEP.
- **Personal administrativo** de la facultad que requiera consultar datos especificos del documento de manera agil.

---

## Arquitectura del Sistema

El proyecto sigue una arquitectura RAG (Retrieval-Augmented Generation) compuesta por las siguientes capas:

```
+---------------------+          +-------------------------+          +------------------+
|                     |   POST   |                         |  Query   |                  |
|   Frontend (React)  +--------->+   Backend (FastAPI)     +--------->+   ChromaDB       |
|   Puerto: 5173 (dev)|  /api/   |   Puerto: 8000          |          |   (Base Vectorial)|
|                     |  chat    |                         |<---------+                  |
+---------------------+          +----------+--------------+  Docs    +------------------+
                                            |
                                            | Contexto + Pregunta
                                            v
                                 +----------+--------------+
                                 |                         |
                                 |   LLM via OpenRouter    |
                                 |   (Gemini 2.5 Flash)    |
                                 |                         |
                                 +-------------------------+
```

### Stack Tecnologico

| Componente         | Tecnologia                                      |
|--------------------|--------------------------------------------------|
| Frontend           | React 19, Vite, Vanilla CSS                      |
| Backend            | Python 3.11, FastAPI, Uvicorn                    |
| Orquestacion RAG   | LangChain, LangChain-Chroma, LangChain-OpenAI   |
| Base Vectorial     | ChromaDB con embeddings multilinguees (MiniLM)   |
| Modelo de Lenguaje | Google Gemini 2.5 Flash (via OpenRouter)          |
| Contenedorizacion  | Docker (multi-stage build)                       |

### Flujo de una Consulta

1. El usuario escribe una pregunta en la interfaz del chat.
2. El frontend envia la pregunta junto con el historial de la conversacion actual al endpoint `/api/chat`.
3. El backend busca en ChromaDB los 6 fragmentos del PEP mas relevantes semanticamente.
4. Los fragmentos recuperados se formatean e inyectan como contexto en el prompt del sistema.
5. El prompt completo (contexto + historial + pregunta) se envia al LLM a traves de OpenRouter.
6. El LLM genera una respuesta basada exclusivamente en el contexto proporcionado.
7. La respuesta se devuelve al frontend y se renderiza en formato Markdown.

---

## Tipo de Preguntas que Responde

PEPIS puede responder preguntas relacionadas con el contenido del PEP de Ingenieria de Sistemas, entre ellas:

- Competencias generales y especificas del programa.
- Perfil de ingreso y perfil de egreso del estudiante.
- Plan de estudios, asignaturas y creditos academicos.
- Mision, vision y objetivos del programa.
- Estrategias pedagogicas y metodologicas.
- Estructura curricular y areas de formacion.
- Informacion sobre acreditacion y autoevaluacion.
- Relacion con el sector productivo y las tendencias del mercado.

**Nota:** PEPIS solo responde con informacion que se encuentre en los documentos oficiales indexados. Si la informacion solicitada no esta en la base de conocimiento, el asistente lo indicara de manera explicita.

---

## Ejecucion en Local

### Requisitos Previos

- Python 3.11 o superior
- Node.js 18 o superior
- Git
- Una clave de API de [OpenRouter](https://openrouter.ai/)

### 1. Clonar el Repositorio

```bash
git clone <URL_DEL_REPOSITORIO>
cd PEPIS
```

### 2. Configurar el Backend

```bash
# Crear y activar el entorno virtual
python -m venv venv

# Windows
venv\Scripts\Activate.ps1

# Linux/Mac
source venv/bin/activate

# Instalar las dependencias
cd backend
pip install -r requirements.txt
```

Crear el archivo `.env` dentro de la carpeta `backend/` con el siguiente contenido:

```
OPENROUTER_API_KEY=tu_clave_de_openrouter_aqui
```

### 3. Iniciar el Backend

```bash
cd backend
uvicorn app.main:app --reload
```

El servidor estara disponible en `http://localhost:8000`. La documentacion interactiva de la API estara en `http://localhost:8000/docs`.

### 4. Configurar e Iniciar el Frontend

En una terminal separada:

```bash
cd frontend
npm install
npm run dev
```

El frontend estara disponible en `http://localhost:5173`.

### 5. Uso

Abre `http://localhost:5173` en tu navegador y comienza a hacer preguntas sobre el PEP de Ingenieria de Sistemas.

---

## Despliegue

### Plataforma Actual

El despliegue en produccion se realizo utilizando **App Platform de Digital Ocean**. Esta plataforma permite el despliegue automatizado desde un repositorio de GitHub mediante la deteccion del archivo `Dockerfile` incluido en la raiz del proyecto. El contenedor resultante empaqueta tanto el frontend compilado como el backend de FastAPI en un unico servicio web.

### Nota sobre Oracle Cloud Infrastructure (OCI)

Inicialmente, se planeo realizar el despliegue en la capa gratuita de **Oracle Cloud Infrastructure (OCI)**, aprovechando sus instancias de computo Always Free. Sin embargo, durante la implementacion se presentaron limitaciones tecnicas y restricciones de la plataforma que impidieron completar el proceso de forma satisfactoria. Como alternativa, se opto por App Platform de Digital Ocean, que ofrecio un flujo de despliegue mas directo y compatible con la arquitectura del proyecto.


A futuro, se contempla migrar el despliegue a Oracle OCI una vez se resuelvan las limitaciones encontradas, con el objetivo de aprovechar los recursos gratuitos de la plataforma para mantener la operacion del servicio sin costo recurrente.

---

## Licencia

Este proyecto fue desarrollado como parte de un ejercicio academico para la Universidad Francisco de Paula Santander (UFPS). Su uso esta destinado exclusivamente a fines educativos e informativos.
