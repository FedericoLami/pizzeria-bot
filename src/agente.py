from langgraph.graph import StateGraph, END
from src.nodos import nodo_redactor, nodo_buscador, nodo_clasificador, nodo_revisor
from src.estado import EstadoSesion

grafo = StateGraph(EstadoSesion)
grafo.add_node("clasificador", nodo_clasificador)
grafo.add_node("buscador", nodo_buscador)
grafo.add_node("redactor", nodo_redactor)
grafo.add_node("revisor", nodo_revisor)

grafo.set_entry_point("clasificador")
grafo.add_edge("clasificador", "buscador")
grafo.add_edge("buscador","redactor")
grafo.add_edge("redactor","revisor")
grafo.add_edge("revisor", END)

grafo_app = grafo.compile()