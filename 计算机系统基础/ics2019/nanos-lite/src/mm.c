#include "memory.h"
#include "proc.h"

static void *pf = NULL;

void* new_page(size_t nr_page) {
  void *p = pf;
  pf += PGSIZE * nr_page;
  assert(pf < (void *)_heap.end);
  return p;
}

void free_page(void *p) {
  panic("not implement yet");
}

/* The brk() system call handler. */
int mm_brk(uintptr_t brk, intptr_t increment) {
  uintptr_t new_brk = brk + increment;
  if (new_brk > current->max_brk && current->max_brk!=0) {
    // 老、新　最终页起始地址
    uintptr_t old_pe = PGROUNDUP(current->max_brk);
    uintptr_t new_pe = PGROUNDUP(new_brk)-PGSIZE;
    for (; old_pe <= new_pe; old_pe += PGSIZE)
      _map(&current->as, (void *)old_pe, new_page(1), 0);
  }
  current->max_brk = max(current->max_brk,new_brk);
  return 0; 
}

void init_mm() {
  pf = (void *)PGROUNDUP((uintptr_t)_heap.start);
  Log("free physical pages starting from %p", pf);

  _vme_init(new_page, free_page);
}
