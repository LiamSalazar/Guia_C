#include <stdio.h>

int main() {
    // Declaración de variables
    double total = 0, propina = 0;
    int nivelServicio = 0;
    // Entrada de datos
    printf("Ingrese el total de la cuenta: ");
    scanf("%lf", &total);
    printf("Ingrese que tan bueno fue servicio: \n");
    printf("1-Excelente (20%% de propina)\n");
    printf("2-Bueno (15%% de propina)\n");
    printf("3-Regular (10%% de propina)\n");
    scanf("%d", &nivelServicio);
    // Proceso
    switch (nivelServicio) {
        case 1:
            propina = total * 0.20;
            break;
        case 2:
            propina = total * 0.15;
            break;
        case 3:
            propina = total * 0.10;
            break;
        default:
            break;
    }
    // Salida de datos
    printf("La propina es: %lf\n", propina);
    printf("El total a pagar es: %lf\n", total + propina);

    return 0;
}
