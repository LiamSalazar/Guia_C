#include <stdio.h>

int main() {
    // Declaración de variablkes
    double peso = 0, altura = 0, imc = 0;
    // Entrada de datos
    printf("Ingrese su peso: ");
    scanf("%lf", &peso);
    printf("Ingrese su altura: ");
    scanf("%lf", &altura);
    // Proceso: cálculo del IMC
    imc = peso / (altura * altura);
    printf("Su IMC es: %.2lf\n", imc);
    printf("Su tipo de peso es: \n");
    if (imc < 18.5) {
        printf("Bajo peso\n");
    } else if (imc >= 18.5 && imc < 24.9) {
        printf("Peso normal\n");
    } else if (imc >= 25.0 && imc < 29.9) {
        printf("Sobrepeso\n");
    } else {
        printf("Obesidad\n");
    }
    return 0;
}
