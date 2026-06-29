import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic()

def nodo_clasificador(estado):
    estado["historial"].append({"role":"user","content":estado["consulta"]})
    mensajes = estado["historial"]

    answer = client.messages.create(
        model = "claude-haiku-4-5",
        max_tokens = 1024,
        system = """
                Sos un clasificador de consultas de atención al cliente.
                Respondé únicamente con una de estas categorías en texto plano, sin JSON ni explicaciones.

                Categorías y ejemplos:
                - reclamo: producto dañado, producto incorrecto, mal servicio recibido
                - consulta_producto: consulta de que se pidio con anterioridad 
                - modificar_pedido: modificar pedido realizado para agregar, eliminar o modificar productos
                - consulta_envio: dónde está mi pedido, demora en entrega
                - reembolso: quiero que me devuelvan el dinero, cancelar compra
                - spam: mensajes sin sentido, publicidad, texto aleatorio, consultas que no tienen relación con compras o productos de la pizzeria

                Respondé solo con la palabra de la categoría correspondiente.
                Si el mensaje contiene texto sin sentido, palabras aleatorias, o no tiene una consulta clara relacionada con compras o soporte, clasificalo como spam.
                - spam: texto sin sentido, palabras aleatorias, oraciones religiosas o poéticas sin relación con compras, lorem ipsum, mensajes que no son consultas de clientes.
             """,
        messages = mensajes
    )

    estado["categoria"] = answer.content[0].text
    return estado 
