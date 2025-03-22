#!/bin/bash

# $# is the number of arguments received
if [ $# -ne 2 ]; then
    # $0 is the name of the script
    echo "Usage: $0 <output-file> <number-of-clients>"
    exit 1
fi

# Parameters
OUTPUT_FILE=$1
NUM_CLIENTS=$2

echo "Nombre del archivo de salida: $OUTPUT_FILE"
echo "Cantidad de clientes: $NUM_CLIENTS"

python3 mi-generador.py "$OUTPUT_FILE" "$NUM_CLIENTS"