#include "proc.h"

#define MAX_NR_PROC 4

static PCB pcb[MAX_NR_PROC] __attribute__((used)) = {};
static PCB pcb_boot = {};
PCB *current = NULL;


// 用到的函数申明
void naive_uload(PCB *pcb, const char *filename);
void context_kload(PCB *pcb, void *entry);
void context_uload(PCB *pcb, const char *filename);


void switch_boot_pcb() {
  current = &pcb_boot;
}

void hello_fun(void *arg) {
  int j = 1;
  while (1) {
    Log("Hello World from Nanos-lite for the %dth time!", j);
    j ++;
    _yield();
  }
}

int fg_pcb=1;

void init_proc() {
  Log("Initializing processes...");
  context_uload(&pcb[0], "/bin/hello"); 
  context_uload(&pcb[1], "/bin/pal");
  context_uload(&pcb[2], "/bin/pal");
  context_uload(&pcb[3], "/bin/pal");
  switch_boot_pcb();
}

static int sss = 0; // 用来不同规模划分时间
_Context* schedule(_Context *prev) {
  current->cp = prev; 
  sss+=1;
  sss%=256;
  if (sss==0) current = &pcb[0];
  else current = &pcb[fg_pcb];
  return current->cp;
}
