# Usa una imagen base de Python
FROM python:3.12.1

# Establece el directorio de trabajo
WORKDIR /app

# Copia los archivos necesarios al contenedor
COPY . /app

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Instala la biblioteca PIL
RUN pip install Pillow

# Define el comando predeterminado que se ejecutará cuando el contenedor se inicie
CMD ["python", "main.py"]