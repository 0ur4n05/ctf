#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void rstrip(char* buf, const size_t len) {
    for (int i = len - 1; i >= 0; i--)
        if (buf[i] == '\n') {
            buf[i] = '\0';
            break;
        }
}

const char suffix[] = "! Welcome to IrisCTF2024. If you have any questions you can contact us at test@example.com\0\0\0\0";

int main() {
    char message[128];
    char name[64];			// taking my name
    fgets(name, 64, stdin);		// fucking literally taking my name
    rstrip(name, 64);			// stripping the new lines

    strcpy(message, "Hi there, ");		// message
    strcpy(message + strlen(message), name);		
    memcpy(message + strlen(message), suffix, sizeof(suffix));

    printf("%s\n", message);
}

__attribute__((section(".flag")))
void win() {
    __asm__("pop %rdi");
    system("cat /flag");
}
