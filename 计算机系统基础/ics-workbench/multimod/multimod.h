#include <stdint.h>

typedef int64_t (*multimod_t)(int64_t, int64_t, int64_t);
#define LENGTH(arr) (sizeof(arr) / sizeof(arr[0]))

int64_t multimod_p1(int64_t a, int64_t b, int64_t m);
int64_t multimod_p2(int64_t a, int64_t b, int64_t m);
int64_t multimod_p3(int64_t a, int64_t b, int64_t m);

extern multimod_t multimod_tab[];
