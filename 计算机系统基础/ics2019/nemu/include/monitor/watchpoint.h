#ifndef __WATCHPOINT_H__
#define __WATCHPOINT_H__

#include "common.h"

typedef struct watchpoint {
  int NO;
  bool used;
  char watch_expression[200];
  uint32_t pre_value;
} WP;

#endif
