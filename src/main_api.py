from pydantic import BaseModel
from fastapi import FastAPI,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from src.agente import grafo_app
from fastapi.responses import HTMLResponse
from src.sesion import leer_historial, guardar_historial

class MensajeRequest(BaseModel):
    mensaje: str
    session_id: str

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analizar")
def analizar_mensaje(request: MensajeRequest):
    try:
        historial = leer_historial(request.session_id)
        resultado = grafo_app.invoke({"consulta": request.mensaje, "categoria": "", "informacion": "", "respuesta": "", "idSesion": request.session_id, "historial": historial, "respuesta_final": ""})
        guardar_historial(request.session_id, resultado["historial"])
        return {"respuesta": resultado["respuesta_final"]}
    except ValueError:
        raise HTTPException(status_code=500, detail="Error al procesar la respuesta de Claude")


@app.get("/")
def frontend():
    with open("index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())