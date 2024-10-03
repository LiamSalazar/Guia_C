#include <stdio.h>

int main() {
    // Declaración de variables
    double peso = 0, costo = 0;
    int tipo = 0;
    // Entrada de datos
    printf("Ingrese el peso del paquete: \n");
    scanf("%lf", &peso);
    printf("Seleccione el tipo de envio: \n");
    printf("1-Local\n");
    printf("2-Nacional\n");
    printf("3-Internacional\n");
    scanf("%d", &tipo);
    // Procesos
    switch (tipo) {
        case 1:
            costo = peso * 10;  
            break;
        case 2:
            costo = peso * 20; 
            break;
        case 3:
            costo = peso * 30; 
            break;
        default:
            break;
    }
    // Salida de datos
    printf("El costo total es: %lf\n", costo);
    return 0;
}
