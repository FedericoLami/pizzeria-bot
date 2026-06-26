import redis
from dotenv import load_dotenv
import os
import random
import json

load_dotenv()

redisClient = redis.Redis(
    host = os.environ.get("REDIS_HOST"),
    port = os.environ.get("REDIS_PORT"),
    decode_responses=True
)

def create_session_id(nombre):
    return nombre + "_" + str(random.randint(100000,999999))


def guardar_historial(session_id,historial):
    historial_str = json.dumps(historial)
    redisClient.set("sesion:" + session_id, historial_str, ex = 300) 

def leer_historial(session_id):
    sesion = ("sesion:" + session_id)
    sesionRedis = redisClient.get(sesion)
    if sesionRedis:
        return json.loads(sesionRedis)
    else:
        return []   