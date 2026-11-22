#Patron factory. Funcion que decide que objeto crear segun la configuracion. Si es local o en servidor esta fucion decide que cliente crear

from qdrant_client import QdrantClient
from src.config import QDRANT_URL, DB_DIR

def get_qdrant_client():
    if QDRANT_URL:
        return QdrantClient(url=QDRANT_URL)
    #Si no hay variable de entorno no entra en la anterior y se crea el cliente local.
    return QdrantClient(path=str(DB_DIR))