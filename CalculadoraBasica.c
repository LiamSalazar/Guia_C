# include <stdio.h>

int main(){
    // Delaración de variables
    float num1 = 0, num2 = 0, resultado = 0;
    int opcion = 0;
    // Entrada de datos
    printf("Escriba los dos numeros a operar: \n");
    scanf("%f %f", &num1, &num2);
    printf("Seleccione la operación: \n");
    printf("1-Suma\n");    
    printf("2-Resta\n");    
    printf("3-Multiplicacion\n");    
    printf("4-Division\n");
    scanf("%d", &opcion);
    // Procesos
    switch (opcion){
        case 1:
            resultado = num1 + num2;
            break;
        case 2:
            resultado = num1 - num2;
            break;
        case 3:
            resultado = num1 * num2;
            break;
        case 4:
            resultado = num1 / num2;
            break;
        default:
            break;
    }
    // Salida de datos
    printf("El resultado de la operacion es: %.2f\n", resultado);
    return 0;
}