# Qué hace: guarda todos los ajustes del proyecto (rutas, modelos, tamaño de los fragmentos). No ejecuta nada. Los demás archivos lo importan.

# Por qué existe: si mañana quieres probar otro modelo o fragmentos más grandes, cambias una línea aquí y no tocas el resto del código. En la entrevista lo puedes explicar como «separar la configuración de la lógica».

# Estructura:

# Rutas de carpetas
# Modelos de Ollama
# Parámetros del RAG

#forma moderna de trabajar con rutas en py
from pathlib import Path
# Rutas de carpetas 
#Carpeta raiz del proyecto + el archivo + resolve que lo convierte en ruta absoluta y sube dos puestos
BASE_DIR = Path(__file__).resolve().parent.parent
#carpeta de los pdfs 
DOCS_DIR = BASE_DIR / "data" / "docs"
# chroma DB 
DB_DIR = BASE_DIR / "vector_db"
#organizacion de tablas de la DB 
COLLECTION_NAME = "docs"


#Modelos 
LLM_MODEL = "qwen2.5:7b"
#Modelo que convierte texto en vectores
EMBED_MODEL = "bge-m3"

#RAG parameters (chars)
CHUNK_SIZE = 800
#Solapamiento
CHUNK_OVERLAP = 150
#parametros de recuperacion de cada pregunta
TOP_K = 4
#Separacion entre pregunta es mayor a 0.5 devuelve un no lo se porque da por hecho que la respuesta no esta en los documentos.
MIN_SCORE = 0.5