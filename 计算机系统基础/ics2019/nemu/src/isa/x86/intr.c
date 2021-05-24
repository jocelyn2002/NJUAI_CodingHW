#include "rtl/rtl.h"

void raise_intr(uint32_t NO, vaddr_t ret_addr) {
  /* TODO: Trigger an interrupt/exception with ``NO''.
   * That is, use ``NO'' to index the IDT.
   */
  
  // 压栈eflags,cs,eip
  s0=cpu.cs;
  rtl_push(&cpu.eflags.val);
  rtl_push(&s0);
  rtl_push(&ret_addr); // 返回地址

  // pa4.3
  cpu.eflags.IF = 0;

  // 读IDTR
  s0 = vaddr_read(cpu.idt_base+NO*8,4);
  s1 = vaddr_read(cpu.idt_base+NO*8+4,4);
  s2 = 0xffff0000 & s0;// selector
  cpu.cs = s2>>16;
  s0 = 0x0000ffff & s0;
  s1 = 0xffff0000 & s1;
  rtl_j(s0 | s1);
  // printf("即将跳转到：%08x\n",cpu.idt_base);

}

bool isa_query_intr(void) {
  if (cpu.eflags.IF && cpu.INTR) {
    cpu.INTR = false;
    raise_intr(32, cpu.pc);
    return true;
  }
  return false;
}
