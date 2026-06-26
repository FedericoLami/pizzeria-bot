from typing import TypedDict,List


class EstadoSesion(TypedDict):
    consulta: str
    categoria: str
    informacion: str
    respuesta: str
    idSesion: str
    historial: List[dict]
    respuesta_final:str