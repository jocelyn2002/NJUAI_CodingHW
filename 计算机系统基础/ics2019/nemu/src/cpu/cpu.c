#include "cpu/exec.h"

CPU_state cpu;

rtlreg_t s0, s1, s2,t0, t1, ir;

/* shared by all helper functions */
DecodeInfo decinfo;
bool isa_query_intr(void);

void decinfo_set_jmp(bool is_jmp) {
  // printf("你爷爷我马上就要跳到:%08x\n",decinfo.jmp_pc);
  decinfo.is_jmp = is_jmp;
}

void isa_exec(vaddr_t *pc);

vaddr_t exec_once(void) {
  decinfo.seq_pc = cpu.pc;
  isa_exec(&decinfo.seq_pc);
  update_pc();
  if (isa_query_intr()) update_pc();

  return decinfo.seq_pc;
}
