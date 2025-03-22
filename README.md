# Enunciados
### Ejercicio N°1:
Definir un script de bash `generar-compose.sh` que permita crear una definición de Docker Compose con una cantidad configurable de clientes.  El nombre de los containers deberá seguir el formato propuesto: client1, client2, client3, etc. 

El script deberá ubicarse en la raíz del proyecto y recibirá por parámetro el nombre del archivo de salida y la cantidad de clientes esperados:

`./generar-compose.sh docker-compose-dev.yaml 5`

Considerar que en el contenido del script pueden invocar un subscript de Go o Python:

```
#!/bin/bash
echo "Nombre del archivo de salida: $1"
echo "Cantidad de clientes: $2"
python3 mi-generador.py $1 $2
```

En el archivo de Docker Compose de salida se pueden definir volúmenes, variables de entorno y redes con libertad, pero recordar actualizar este script cuando se modifiquen tales definiciones en los sucesivos ejercicios.

# Solución
Se creo un script de bash `generar-compose.sh` como lo pide el enunciado. Para ejecutarlo, correr
`./generar-compose.sh <output-file> <number-of-clients>`.

Internamente se llama a un script de python llamado `mi-generador.py` que dinámicamente crea el
texto del Compose file, agregando la cantidad de clientes especificada junto con el servidor y la
definición de la red en la que se encuentran.

**Obs**: el script sobreescribe el archivo `docker-compose-dev.yaml`.

Para ver la interacción entre el servidor y los clientes:

Si es la primera vez que se ejecuta:
1. `make build`
2. `make docker-image`

Luego:
1. `make docker-compose-up`
2. `make docker-compose-logs`
3. `make docker-compose-down`