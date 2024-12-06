// echo.c
#include <stdio.h>

int main() {
    char buffer[100];
    printf("Please enter some text: ");
    fgets(buffer, sizeof(buffer), stdin);
    printf("You entered: %s", buffer);
    return 0;
}
