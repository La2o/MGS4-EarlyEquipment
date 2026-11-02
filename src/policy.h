#ifndef EARLY_EQUIPMENT_POLICY_H
#define EARLY_EQUIPMENT_POLICY_H
#include <stdint.h>
#include <string.h>
/* The game stores completed runs in a uint16, followed by another uint16. */
static int early_stage(const char *stage) {
    return !memcmp(stage,"s01a00l",7) || !memcmp(stage,"s01a05l",7) || !memcmp(stage,"s01a10l",7);
}
static int eligible(uint16_t clears, uint16_t difficulty, uint32_t progress, const char *stage) {
    return clears > 0 && progress < 18 && early_stage(stage) &&
        (difficulty==20 || difficulty==30 || difficulty==35 || difficulty==40 || difficulty==50);
}
#endif
