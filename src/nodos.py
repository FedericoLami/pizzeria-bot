import anthropic
from dotenv import load_dotenv
from src.postgres import obtener_pedido, obtener_productos
from src.sesion import leer_estado_pedido

load_dotenv()

client = anthropic.Anthropic()

def nodo_clasificador(estado):
    estado["historial"].append({"role": "user", "content": estado["consulta"]})
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

def nodo_buscador(estado):
    categoria = estado["categoria"]

    if categoria == "consulta_producto":
        estado["informacion"] = str(obtener_productos())
    elif categoria in ["reclamo","reembolso","modificar_pedido"]:
        estado["informacion"] = str(obtener_pedido(estado["consulta"]))
    elif categoria == "consulta_envio":
        estado["informacion"] = str(leer_estado_pedido(estado["consulta"]))
    else:
        estado["informacion"] = ""

    return estado


def nodo_redactor(estado):
    mensajes = estado["historial"] + [{"role": "user", "content": f"Categoría: {estado['categoria']}\nInformación disponible: {estado['informacion']}"}]

    answer = client.messages.create(
        model = "claude-haiku-4-5",
        max_tokens = 1024,
        system = """
                Sos un agente de atención al cliente de una pizzería. Tu tarea es redactar una respuesta profesional, empática y clara al cliente basándote en su consulta, la categoría detectada y la información disponible.
                Reglas importantes:
                - Respondé siempre en español
                - Sé empático y cordial, recordá que el cliente puede estar frustrado
                - Sé conciso y directo. Evitá adjetivos innecesarios como "deliciosa", "exquisita" o frases de relleno. El cliente quiere información, no publicidad.
                - Si la categoría es 'consulta_producto', usá la información del menú para responder con nombres, precios y disponibilidad. Si el producto que menciona el cliente no coincide exactamente con el menú, intentá matchearlo por similitud y confirmá con el cliente si es ese el producto que busca
                - Si la categoría es 'reclamo' o 'reembolso', pedile al cliente el número de pedido si no lo proporcionó
                - Si la categoría es 'consulta_envio' o 'modificar_pedido', informá el estado actual del pedido basándote en la información disponible
                - Si la categoría es 'spam', respondé brevemente que el mensaje no corresponde a una consulta válida
                - Para reclamos generales sin pedido vinculado, indicá al cliente que se comunique directamente con el local
                - Nunca inventes información que no esté en los datos provistos
                - No hagas preguntas de seguimiento al final de tu respuesta
             """,
        messages = mensajes
    )

    estado["respuesta"] = answer.content[0].text
    return estado

def nodo_revisor(estado):
    mensajes = [{"role": "user", "content": f"Consulta del cliente: {estado['consulta']}\nRespuesta: {estado['respuesta']}"}]
    answer = client.messages.create(
        model = "claude-haiku-4-5",
        max_tokens = 1024,
        system = """
                Sos un revisor de calidad de respuestas de atención al cliente de una pizzería.
                Recibís una consulta del cliente y la respuesta redactada por otro agente.
                Tu tarea es verificar que la respuesta sea:
                - Empática y cordial
                - Correcta según la consulta del cliente
                - Clara y sin información inventada
                - Sin preguntas de seguimiento al final

                Si la respuesta está bien, devolvela tal cual.
                Si necesita mejoras, corregila y devolvé la versión mejorada.
                Respondé únicamente con la respuesta final al cliente, sin explicaciones adicionales.
             """,
        messages = mensajes
    )

    estado["respuesta_final"] = answer.content[0].text
    estado["historial"].append({"role": "assistant", "content": estado["respuesta_final"]})
    return estado