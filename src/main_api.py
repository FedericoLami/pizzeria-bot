from pydantic import BaseModel
from fastapi import FastAPI,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from src.agente import grafo_app
from fastapi.responses import HTMLResponse
from src.sesion import leer_historial, guardar_historial
from src.postgres import obtener_productos_admin, actualizar_disponibilidad

class MensajeRequest(BaseModel):
    mensaje: str
    session_id: str

class DisponibilidadRequest(BaseModel):
    disponible: bool

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
    
@app.get("/admin/productos")
def admin_obtener_productos():
    try:
        productos = obtener_productos_admin()
        return {"productos": productos}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.put("/admin/productos/{id_producto}")
def admin_actualizar_producto(id_producto: int, request: DisponibilidadRequest):
    try:
        actualizar_disponibilidad(id_producto, request.disponible)
        return {"mensaje": "Producto actualizado correctamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/admin")
def admin_frontend():
    with open("admin.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())