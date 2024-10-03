#include <stdio.h>

// Definición de los rangos de calificación
#define A 90
#define B 80
#define C 70
#define D 60

int main() {
    // Declaración de variables
    int calificacion = 0;

    // Entrada de datos
    printf("Escriba la calificación: ");
    scanf("%d", &calificacion);

    // Procesos y salida
    if (calificacion >= A) {
        printf("La calificación es: A\n");
    } else if (calificacion >= B) {
        printf("La calificación es: B\n");
    } else if (calificacion >= C) {
        printf("La calificación es: C\n");
    } else if (calificacion >= D) {
        printf("La calificación es: D\n");
    } else {
        printf("La calificación es: F\n");
    }

    return 0;
}

