# Pizzeria Bot — Motor Genérico de Atención al Cliente con IA

Sistema de atención al cliente construido con **LangGraph**, **Claude AI**, **Redis** y **PostgreSQL**, demostrado a través de un caso real: una pizzería ficticia llamada **La Bella Napoli**. El sistema está diseñado como un motor genérico reutilizable para cualquier PyME — la pizzería es el caso de demostración, no el único uso posible.

El bot mantiene **memoria de conversación** por cliente usando Redis, consulta datos reales de la base de datos, y procesa consultas en lenguaje natural a través de un pipeline de 4 agentes especializados.

---

## Demo

![Demo del sistema](demo.gif)

---

## Tecnologías utilizadas

| Capa | Tecnología |
|------|-----------|
| Orquestación de agentes | LangGraph |
| Modelo de lenguaje | Claude Haiku (Anthropic API) |
| Memoria de sesiones | Redis (Docker) |
| Base de datos | PostgreSQL (Docker) |
| Backend / API REST | FastAPI + Uvicorn |
| Frontend | HTML · CSS · JavaScript vanilla |
| Configuración | python-dotenv |
| Entorno | Python 3.11 + venv |

---

## Arquitectura del sistema

```
pizzeria-bot/
├── src/
│   ├── estado.py          # Estado compartido del grafo (TypedDict con historial y sesión)
│   ├── sesion.py          # Gestión de sesiones y historial en Redis
│   ├── postgres.py        # Conexión y consultas a PostgreSQL
│   ├── nodos.py           # Los 4 agentes del pipeline LangGraph
│   ├── agente.py          # Construcción y compilación del grafo
│   └── main_api.py        # API REST con FastAPI
├── database/
│   ├── schema.sql         # Definición de las 5 tablas de PostgreSQL
│   └── seed.sql           # Datos de prueba (4 pizzas del menú)
├── index.html             # Interfaz web del cliente
├── .env                   # Variables de entorno (no se sube a GitHub)
├── .gitignore
├── requirements.txt
└── README.md
```

---

## ¿Cómo funciona el pipeline?

```
mensaje del cliente
        ↓
[1. Clasificador] — determina la categoría de la consulta
        ↓
[2. Buscador] — consulta Redis o Postgres según la categoría
        ↓
[3. Redactor] — redacta la respuesta usando el historial completo
        ↓
[4. Revisor] — verifica calidad y coherencia antes de enviar
        ↓
respuesta al cliente + historial actualizado en Redis
```

**Estado compartido entre nodos:**

```python
class EstadoSesion(TypedDict):
    consulta: str          # mensaje actual del cliente
    categoria: str         # determinada por el clasificador
    informacion: str       # datos recuperados por el buscador
    respuesta: str         # redactada por el redactor
    idSesion: str          # identificador único de la sesión
    historial: List[dict]  # conversación completa en formato {role, content}
    respuesta_final: str   # aprobada por el revisor
```

---

## Categorías de consultas

| Categoría | Descripción |
|-----------|------------|
| `consulta_producto` | Preguntas sobre el menú, precios y disponibilidad |
| `consulta_envio` | Estado y seguimiento del pedido |
| `modificar_pedido` | Cambios a un pedido ya realizado |
| `reclamo` | Producto incorrecto, dañado o mal servicio |
| `reembolso` | Devoluciones y cancelaciones |
| `spam` | Mensajes no válidos o sin relación con el negocio |

---

## Memoria entre conversaciones

Cada cliente tiene su propia sesión identificada por `nombre_XXXXXX` (nombre + número aleatorio de 6 dígitos). El historial de la conversación se guarda en Redis con TTL de 5 minutos de inactividad — cuando expira, la sesión se cierra automáticamente y la próxima vez empieza desde cero.

---

## Esquema de base de datos (PostgreSQL)

```
productos       → idProducto, nombreProducto, monto, disponible, descripcion
pedido          → idPedido, sessionId, fecha, horaPedido, horaEstimada, horaEntrega
detallePedido   → idDetalle, idPedido, idProducto, cantidad
reclamos        → idReclamo, idPedido, idDetalle, motivo, fecha
reembolsos      → idReembolso, idPedido, idDetalle, monto, motivo, fecha
```

---

## Instalación y uso

### Requisitos previos

- Python 3.11
- Docker Desktop
- API Key de Anthropic ([console.anthropic.com](https://console.anthropic.com))

### Pasos

```bash
# 1. Clonar el repositorio
git clone https://github.com/FedericoLami/pizzeria-bot.git
cd pizzeria-bot

# 2. Crear y activar entorno virtual
py -3.11 -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS / Linux

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
# Crear archivo .env en la raíz del proyecto:
ANTHROPIC_API_KEY=tu-api-key
REDIS_HOST=localhost
REDIS_PORT=6379
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=pizzeria
POSTGRES_USER=postgres
POSTGRES_PASSWORD=tu-password

# 5. Levantar Redis y PostgreSQL con Docker
docker run -d --name redis-pizzeria -p 6379:6379 redis
docker run -d --name postgres-pizzeria -e POSTGRES_PASSWORD=tu-password -e POSTGRES_DB=pizzeria -p 5432:5432 postgres

# 6. Crear las tablas y cargar datos de prueba
docker cp database/schema.sql postgres-pizzeria:/schema.sql
docker exec -it postgres-pizzeria psql -U postgres -d pizzeria -f /schema.sql

docker cp database/seed.sql postgres-pizzeria:/seed.sql
docker exec -it postgres-pizzeria psql -U postgres -d pizzeria -f /seed.sql

# 7. Iniciar el servidor
uvicorn src.main_api:app --reload

# 8. Abrir en el navegador
# http://127.0.0.1:8000
```

### Documentación interactiva de la API

```
http://127.0.0.1:8000/docs
```

---

## Trabajo futuro

- **Panel de administración** — interfaz para que el dueño actualice la disponibilidad de productos sin tocar código
- **Seguimiento de pedidos en tiempo real** — integración con el sistema de gestión (POS) de la pizzería vía API. Actualmente el bot solicita el número de pedido y deriva al local
- **Rate limiting** — detección de spam por frecuencia de requests
- **WhatsApp / Instagram** — integración con la API de Meta para operar en los canales reales de la PyME
- **Multi-negocio** — parametrizar el motor para servir múltiples clientes desde una sola instancia

---

## Sobre el proyecto

Este sistema está pensado como un **motor genérico de atención al cliente para PyMEs argentinas**. La pizzería es el caso de demostración — las políticas de `conocimiento.py` y los datos de `seed.sql` son lo único que cambia de cliente a cliente.

---

## Autor

**Federico Lami**
[LinkedIn](https://www.linkedin.com/in/federicolami/) · [GitHub](https://github.com/FedericoLami/pizzeria-bot)