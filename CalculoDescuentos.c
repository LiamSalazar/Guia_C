# include <stdio.h>

int main(){
    // Declaracion de variables
    int categoria = 0, descuento = 0;
    double precio = 0, resultado = 0;
    // Entrada de datos
    printf("Ingrese el precio del producto: \n");
    scanf("%lf",&precio);
    printf("Ingrese la categoria \n");
    printf("1-Electronica \n");
    printf("2-Ropa \n");
    printf("3-Comida \n");
    scanf("%d",&categoria);
    // Proceso
    switch (categoria)
    {
    case 1:
        resultado = precio * .90;
        descuento = 10;
        break;
    case 2:
        resultado = precio * .95;
        descuento = 5;
        break;
    case 3:
        resultado = precio * .80;
        descuento = 20;
        break;
    default:
        break;
    }
    // Salida de datos
    printf("Precio a pagar: %lf\n", resultado);
    printf("Descuento de: %d%%\n", descuento);
    return 0;
}