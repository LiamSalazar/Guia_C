#include <stdio.h>

int main() {
    // Declaración de variables
    int anio;
    // Entrada de datos
    printf("Ingrese un año: ");
    scanf("%d", &anio);
    // Proceso
    if ((anio % 4 == 0 && anio % 100 != 0) || (anio % 400 == 0)) {
        printf("Bisiesto\n");
    } else {
        printf("No Bisiesto\n");
    }

    return 0;
}
