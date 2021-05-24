#ifndef __COMMON_H__
#define __COMMON_H__

/* Uncomment these macros to enable corresponding functionality. */
#define HAS_CTE
#define HAS_VME

#include <am.h>
#include <klib.h>
#include "debug.h"

typedef char bool;
#define true 1
#define false 0

#define min(x, y)         ((x) < (y) ? (x) : (y))
#define max(x, y)         ((x) < (y) ? (y) : (x))       

#endif
