#include "../include/common.h"

// 真取模
int mod(int i, int b) {
  while (i>=b) i-=b;
  while (i<0) i+=b;
  return i;
}

// debug用printf
int dprintf(const char * fmt,...) {
#ifdef DHDEBUG
    va_list mark;    
    va_start(mark, fmt);
    char buf[256];
    memset(buf,0,256);
    int i = vsprintf(buf,fmt, mark);
    va_end(mark);
    printf(buf);
    return i;
#else
  return 0;
#endif
}

