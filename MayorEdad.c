#include <stdio.h>
# define PARAMETRO 18
int main(){
    // Declaracion de variables
    int edad = 0;
    // Entrada de datos
    printf("Ingrese su edad: \n");
    scanf("%d", &edad);
    // Procesos
    if (edad >= PARAMETRO){
        printf("MAYOR DE EDAD \n");
    }
    else{
        printf("MENOR DE EDAD \n");
    }
    return 0;
}