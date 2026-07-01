import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

pgConnection = psycopg2.connect(
    host = os.environ.get("POSTGRES_HOST"),
    port = os.environ.get("POSTGRES_PORT"),
    dbname = os.environ.get("POSTGRES_DB"),
    user = os.environ.get("POSTGRES_USER"),
    password = os.environ.get("POSTGRES_PASSWORD"),
)

pgCursor = pgConnection.cursor()

def obtener_productos():
    pgCursor.execute("SELECT nombreProducto, disponible, monto, descripcion FROM productos")
    resultados = pgCursor.fetchall()
    return resultados

def obtener_pedido(id_pedido):
    pgCursor.execute("""
                    SELECT pedido.idPedido, pedido.fecha, detallePedido.idProducto, detallePedido.cantidad
                    FROM pedido
                    JOIN detallePedido ON pedido.idPedido = detallePedido.idPedido
                    WHERE pedido.idPedido = %s
                    """,(id_pedido,))
    resultados = pgCursor.fetchall()
    return resultados