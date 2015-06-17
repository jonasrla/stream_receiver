#!/bin/sh

echo "compiling library..."
gcc -Wall -c server_api.c
echo "Extracting library to libserver.a..."
ar rcs libserver.a server_api.o
echo "compiling test_server..."
gcc -static test_server.c -L. -lserver -o test_server