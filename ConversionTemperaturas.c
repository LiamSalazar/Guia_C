# include <stdio.h>

int main(){
    // Declaracion de variables
    double temperatura = 0, resultado = 0;
    int opcion = 0;
    // Entrada de datos
    printf("Ingrese la temperatura: \n");
    scanf("%lf",&temperatura);
    printf("Ingrese la opcion \n");
    printf("1-Celsius a Farenheit \n");
    printf("2-Farenheit a Celsius \n");
    scanf("%d",&opcion);
    // Proceso
    if (opcion == 2){
        resultado = (temperatura - 32) * 5/9;
    }else {
        resultado = (temperatura * 9/5) + 32;
    }
    // Salida de datos
    printf("Resultado: %lf\n", resultado);
    return 0;
}