#include "asm.h"
// #include <string.h>

int64_t asm_add(int64_t a, int64_t b) {
  asm volatile("add %[val1],%[val2];"
      :[val2]"+r"(b),[val1]"+r"(a)
      :
      :
      );
  return b;
}

int asm_popcnt(uint64_t n) {
  int r=0;
  asm volatile("xor %%edx,%%edx;"
      "xor %%ecx,%%ecx;"
      "mov %[ope],%%rsi;"
      "popD0:mov %%rsi,%%rax;"
      "shr %%cl,%%rax;"
      "add $0x1,%%ecx;"
      "and $0x1,%%eax;"
      "add %%eax,%%edx;"
      "mov %%edx,%[res];"
      "cmp $0x40,%%ecx;"
      "jne popD0;"
      :[res]"+r"(r)
      :[ope]"m"(n)
      :"%edx","%ecx","%esi","%rsi","%rax","%cl","%eax"
  );
  return r;
}

void *asm_memcpy(void *dest, const void *src, size_t n) {
  asm(// 准备形参
      "mov %[dest],%%rdi;"
      "mov %[src],%%rsi;"
      "mov %[n],%%rdx;"
      // 开始汇编
      "test %%rdx,%%rdx;"
      "mov %%rdi,%%rax;"
      "je cpyD1;"
      "xor %%ecx,%%ecx;"
      "cpyD0:movzbl (%%rsi,%%rcx,1),%%r8d;"
      "mov %%r8b,(%%rax,%%rcx,1);"
      "add $0x1,%%rcx;"
      "cmp %%rcx,%%rdx;"
      "jne cpyD0;"
      "cpyD1:;"
      :
      :[dest]"r"(dest),[src]"r"(src),[n]"r"(n)
      :
      );
  return dest;
}

int asm_setjmp(asm_jmp_buf env){
  asm volatile("mov %[env],%%rdi;"
      "pop %%rsi;"
      "movq %%rbx,(%%rdi);"
      "movq %%rsp,8(%%rdi);"
      "push %%rsi;"
      "movq %%rbp,16(%%rdi);"
      "movq %%r12,24(%%rdi);"
      "movq %%r13,32(%%rdi);"
      "movq %%r14,40(%%rdi);"
      "movq %%r15,48(%%rdi);"
      "movq %%rsi,56(%%rdi);"
      "xorl %%eax,%%eax;"
      :
      :[env]"r"(env)
      :"memory"
  );
  return 0;
}

void asm_longjmp(asm_jmp_buf env, int val) {
  asm volatile(
      "movl %[val],%%eax;"
      "mov %[env],%%rdi;"
      "movq (%%rdi),%%rbx;"
      "movq 8(%%rdi),%%rsp;"
      "movq 16(%%rdi),%%rbp;"
      "movq 24(%%rdi),%%r12;"
      "movq 32(%%rdi),%%r13;"
      "movq 40(%%rdi),%%r14;"
      "movq 48(%%rdi),%%r15;"
      "jmp *56(%%rdi);"
      :
      :[env]"r"(env),[val]"r"(val)
      :
  );
}
