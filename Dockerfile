#Imagen base con python
FROM python:3.12-slim

#Carpeta de trabajo dentro del contenedor 
WORKDIR /app

#No crea archivos .pyc y los logs salen al momento
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

#Instala las librerias 
COPY requirements.txt . 

RUN pip install --no-cache-dir -r requirements.txt

#Copia mi codigo
COPY src/ ./src/

#Ejecuta la app sin ser root
RUN useradd --create-home appuser

USER appuser

#Documenta el puerto de la app 
EXPOSE 8000

# Arranca uvicorn
CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]