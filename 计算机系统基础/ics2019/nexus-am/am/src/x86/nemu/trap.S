#----|------------entry------------|---irq id---|-----handler-----|
.globl __am_vecsys;    __am_vecsys: pushl $0x80; jmp __am_asm_trap
.globl __am_vectrap;  __am_vectrap: pushl $0x81; jmp __am_asm_trap
.globl __am_irq0;        __am_irq0: pushl   $32; jmp __am_asm_trap
.globl __am_vecnull;  __am_vecnull: pushl   $-1; jmp __am_asm_trap

__am_asm_trap:
  pushal

  pushl $0

  pushl %esp
  call __am_irq_handle

  addl $4, %esp

  movl %eax, %esp # 把栈顶指针切换到新进程的上下文
                  # call __am_irq_handle后eax里有返回值

  addl $4, %esp
  popal
  addl $4, %esp

  iret
