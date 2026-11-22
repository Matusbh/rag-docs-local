# prepara los documentos para poder buscar en ellos. Se ejecuta una vez y otra cada vez que añadas o cambies un PDF

# Pdfs --> texto por página --> fragmentos (chunks) --> vectores (embeddings) --> guardado en Chroma

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams
import ollama
from pypdf import PdfReader
from src.config import (
    DOCS_DIR, DB_DIR, COLLECTION_NAME, EMBED_MODEL, CHUNK_SIZE, CHUNK_OVERLAP
)
from src.db import get_qdrant_client

#? Lee los pdfs
def load_pages():
    pages = []
    #recorre los pdf de la carpeta y los ordena con sorted para que sea siempre el mismo resultado 
    for pdf_path in sorted(DOCS_DIR.glob("*.pdf")):
        reader = PdfReader(pdf_path) # abre los pdfs
        # recorre los pdfs y da a la vez numero a las paginas
        for pages_number, page in enumerate(reader.pages, start=1):
            # si un apag no tiene texto devuelve none o texto vacio
            text = page.extract_text() or ""
            #limpia el t4exto
            text = " ".join(text.split())
            #salta las paginas vacias
            if text:
                # diccopnario
                pages.append({
                "text": text,
                "source": pdf_path.name,
                "page": pages_number,
            })
    return pages

#? Cortar en fragmentos
def split_text(text):
    chunks = []
    # donde empieza el fragmento actual 
    start = 0
    #repite mientras quede texto
    while start < len(text):
        # acaba en 800 chars
        end = start + CHUNK_SIZE
        #añade a los chunks el texto desde start hasta end
        chunks.append(text[start:end])
        if end >= len(text):
            break
        # el siguiente fragmento empieza 150 chars antes de donde acabo 
        start = end - CHUNK_OVERLAP
    return chunks


#? Recorrer pagina y recortar
def build_chunks(pages):
    chunks = []
    for page in pages:
        for i, piece in enumerate(split_text(page["text"])):
            chunks.append({
                #Identificador contruido con el archivo, la pagina y el numero de fragmento
                "id":f"{page['source']}-p{page['page']}-c{i}",
                "text": piece,
                "source": page['source'],
                "page": page['page']
            })
    return chunks

#? Envia textos al modelo y recibe vectores por cada texto
def embed(text):
    response = ollama.embed(model=EMBED_MODEL, input=text)
    return response['embeddings']

#? Guardamos en la base de datos
def save(chunks, embeddings):
    #Abre DB de la carpeta qdrant y la crea si no existe
    #es persistente por lo que se guarda en el disco y no se pierde si se cierra
    client = get_qdrant_client()
    if client.collection_exists(collection_name=COLLECTION_NAME):
    #borra la coleccion anterior para desde cero asi evitamos duplicados 
        client.delete_collection(COLLECTION_NAME)
        #declaramos la base de datos con nombre y vector usado
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=len(embeddings[0]), distance=Distance.COSINE)
    )

    points = [
        PointStruct(
            id=i,
            #vector de ese fragmento
            vector=embeddings[i],
            #datos que acompañan al vector(documents y metadata de chromadb)
            payload={"text": c["text"], "source": c["source"], "page": c["page"]},
        )
        #obtenemos posicion y fragmento
        for i, c in enumerate(chunks)
    ]
    client.upsert(collection_name=COLLECTION_NAME, points=points)
    print(f"Puntos en la coleccion: {client.count(COLLECTION_NAME).count}")
    client.close()


def main():
    pages = load_pages()
    print(f"Paginas leidas: {len(pages)}")
    chunks = build_chunks(pages)
    print(f"Fragmentos creados: {len(chunks)}")
    embeddings = embed([c["text"] for c in chunks])
    print(f"Embeddings: {len(embeddings)} vectores de {len(embeddings[0])} numeros")
    save(chunks, embeddings)
    print(f"Guardado en {DB_DIR}")

if __name__ == "__main__":
        main()
