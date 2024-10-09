#include <stdio.h>

int main(){
    // Declaracion de variables
    double metros = 0, resultado = 0;
    int opcion = 0;
    // Entrada de datos 
    printf("Introduzca la cantidad en metros a convertir \n");
    scanf("%lf", &metros);
    printf("Escoja una opcion: \n");
    printf("1-Centimetros \n");
    printf("2-Milimetros \n");
    printf("3-Kilometros \n");
    scanf("%d", &opcion);
    // Proceso
    switch (opcion){
    case 1:
        resultado = metros * 100;
        break;
    case 2:
        resultado = metros * 1000;
        break;
    case 3:
        resultado = metros / 1000;
        break;
    default:
        break;
    }
    // Salida de datos
    printf("La conversion es: %lf\n", resultado);
    return 0;
}