/* Test-only stand-in: proves the launcher does not start after backup failure. */
#include <stdio.h>
int main(void) {
    FILE *f=fopen("game-started.marker","wb");
    if(!f)return 1;
    fputs("started",f);fclose(f);return 0;
}
