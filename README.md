# Enunciado
### Ejercicio N°2:
Modificar el cliente y el servidor para lograr que realizar cambios en el archivo de configuración no requiera reconstruír las imágenes de Docker para que los mismos sean efectivos. La configuración a través del archivo correspondiente (`config.ini` y `config.yaml`, dependiendo de la aplicación) debe ser inyectada en el container y persistida por fuera de la imagen (hint: `docker volumes`).

# Solución
Se modificó el compose file generado para utilizar un `bind mount`, permitiendo así que cambios en los archivos de configuración no requieran reconstruir las imágenes.
Esto se puede ver en el archivo `mi-generador.py` en el uso de `volume`.

Dado que la configuración de los contenedores se realiza mediante un único archivo, resultó más práctico usar un `bind mount` antes que usar un `docker volumes`.

Parte de la solución consistió en eliminar las variables de entorno relacionadas al logging del compose file.
Esto fue necesario porque las variables de entorno tienen precedencia sobre las de configuración.
