#include <assert.h>
#include <stdio.h>
#include "../src/policy.h"
int main(void) {
    assert(!eligible(0,30,0,"s01a00l"));
    assert(eligible(1,50,0,"s01a00l"));
    assert(eligible(1,20,4,"s01a05l"));
    assert(eligible(2,35,17,"s01a10l"));
    assert(!eligible(1,30,18,"s01a10l"));
    assert(!eligible(1,30,19,"s01a10l"));
    assert(!eligible(1,30,291,"s01a10l"));
    assert(!eligible(1,30,0,"title\0\0"));
    assert(!eligible(1,30,0,"s02a10l"));
    assert(!eligible(1,99,0,"s01a00l"));
    puts("10 early equipment policy checks passed.");
    return 0;
}
