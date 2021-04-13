#include <stdio.h>
#include <stdarg.h>


int __wrap_fprintf(FILE *stream, const char *format, ...)
{
    printf("daemon: ");
    char ch;
    char *pc;

    va_list arg;
    va_start(arg, format);

    while(*format) {
        char ret = *format;
        if (ret == '%') {
            switch (*++format) {
                case 'c':
                    ch = va_arg(arg, int);
                    putchar(ch);
                    break;
                case 's':
                    pc = va_arg(arg, char *);
                    while (*pc) {
                        putchar(*pc);
                        pc++;
                    }
                    break;
                default:
                    break;
            }
        } else {
            putchar(*format);
        }
        format++;
    }

    va_end(arg);
    return 0;
}