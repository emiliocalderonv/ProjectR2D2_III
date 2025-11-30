# Paso 1: Usar una imagen base oficial de Python. 
# '3.11-slim' es ligera y perfecta para producción.
FROM python:3.11-slim

# Paso 2: Establecer el directorio de trabajo dentro del contenedor.
# Todos los comandos siguientes se ejecutarán desde /app.
WORKDIR /app

# Paso 3: Copiar el archivo de requerimientos primero.
# Esto aprovecha el sistema de caché de Docker: si no cambias los requerimientos,
# no se volverán a instalar, haciendo las construcciones futuras más rápidas.
COPY requirements.txt .

# Paso 4: Instalar las dependencias de Python.
# '--no-cache-dir' reduce el tamaño final de la imagen.
RUN pip install --no-cache-dir -r requirements.txt

# Paso 5: Copiar el resto de los archivos de la aplicación al contenedor.
# El '.' significa "todo lo que está en la carpeta actual".
COPY . .

# Paso 6: Exponer el puerto en el que correrá la aplicación.
# Le decimos a Docker que el contenedor escuchará en el puerto 8000.
EXPOSE 8000

# Paso 7: El comando para iniciar la aplicación cuando el contenedor se ejecute.
# Esto le dice a Uvicorn que inicie el objeto 'app' desde el archivo 'main.py',
# que escuche en todas las interfaces de red ('0.0.0.0') y en el puerto 8000.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]