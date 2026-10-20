# pregunta --> vector --> buscar en Qdrant los fragmentos más parecidos --> descartar los poco parecidos --> si no queda ninguno, «no lo sé» --> si quedan, montar el prompt --> el LLM responde --> respuesta + fuentes

import ollama
from qdrant_client import QdrantClient

from src.config import DB_DIR, COLLECTION_NAME, LLM_MODEL, TOP_K, MIN_SCORE
from src.ingest import embed

NOT_FOUND = "I could not find this information in the documentation."
SYSTEM_PROMPT = """You are an assistant for the technical documentation of a manufacturing plant.
Answer ONLY using the context provided below.
If the answer is not in the context, reply exactly: "I could not find this information in the documentation."
Answer briefly, in the same language as the question."""

client = QdrantClient(path=str(DB_DIR))

def search(question):
    # le pasasmos una lista con una sola pregunta, y nos quedamos con el primer vector
    vector = embed([question])[0]
    #compara el vector con la lisra de vectores que hay en l a DB
    result = client.query_points(
        collection_name=COLLECTION_NAME,
        query=vector,
        limit=TOP_K,
    )
    hits= []
    for point in result.points:
        #nos quedamos solo con lo que tenga un score mayor o igual al mínimo
        if point.score >=MIN_SCORE:
            hits.append({
                "text": point.payload["text"],
                "source": point.payload["source"],
                "page": point.payload["page"],
                #redondeamos el score a 3 decimales para que sea más legible
                "score": round(point.score, 3),
        })
    return hits

#? Montamos el prompr para el LLM
def build_prompt(question, hits):
    #une todos los bloques con una linea en blanco entre ellos
    context= "\n\n".join(
        f"[{i}] ({h['source']}, page {h['page']})\n{h['text']}"
        for i, h in enumerate(hits, start=1)
    )
    #Primero devuelve el texto y luego la pregunta
    return f"Context: \n{context}\n\nQuestion: {question}"

#? Responder 
def answer(question):
    hits= search(question)
    if not hits:
        # Si no supera el umbrall niungun fragmento devolvemos no se sin usar el LLM
        return {"answer":  NOT_FOUND, "sources": []}

    response = ollama.chat(
        model= LLM_MODEL,
        messages=[
            #Instucciones fijas definidas antes
            {"role": "system", "content": SYSTEM_PROMPT},
            #Contexto con la pregunta
            {"role": "user", "content": build_prompt(question, hits)},
        ],
        # El modelo elije siempre la palabra mas probable.
        options= {"temperature": 0},
    )
    #Lista de fuentes que devolve,mos junto a la respuesta
    sources=[{"source": h["source"], "page": h["page"], "score": h["score"]} for h in hits]
    return {"answer": response["message"]["content"], "sources": sources}


if __name__ == "__main__": 
    while True:
        #Escribe la pregunta
        question= input("\nPregunta: ")
        # Si se queda en blanco pues sale del bucle
        if not question:
            break
        #Imprime la respuesta junto con la puntuacion
        result= answer(question)
        print("\n" + result["answer"])
        for s in result["sources"]:
            print(f" - {s['source']}, página {s['page']} (score {s['score']})")

    client.close()