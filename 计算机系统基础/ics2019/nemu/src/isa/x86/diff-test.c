#include "nemu.h"
#include "monitor/diff-test.h"



bool isa_difftest_checkregs(CPU_state *ref_r, vaddr_t pc) {
  bool same=true;
  uint32_t a,b;

  a = ref_r->eax;b=cpu.eax;
  if (a!=b){
    same = false;
    printf("eax,ref:%08x   dut:%08x\n",a,b);
  }

  a = ref_r->ecx;b=cpu.ecx;
  if (a!=b){
    same = false;
    printf("ecx,ref:%08x   dut:%08x\n",a,b);
  }

  a = ref_r->edx;b=cpu.edx;
  if (a!=b){
    same = false;
    printf("edx,ref:%08x   dut:%08x\n",a,b);
  }

  a = ref_r->ebx;b=cpu.ebx;
  if (a!=b){
    same = false;
    printf("ebx,ref:%08x   dut:%08x\n",a,b);
  }

  a = ref_r->esp;b=cpu.esp;
  if (a!=b){
    same = false;
    printf("esp,ref:%08x   dut:%08x\n",a,b);
  }

  a = ref_r->ebp;b=cpu.ebp;
  if (a!=b){
    same = false;
    printf("ebp,ref:%08x   dut:%08x\n",a,b);
  }

  a = ref_r->esi;b=cpu.esi;
  if (a!=b){
    same = false;
    printf("esi,ref:%08x   dut:%08x\n",a,b);
  }

  a = ref_r->edi;b=cpu.edi;
  if (a!=b){
    same = false;
    printf("edi,ref:%08x   dut:%08x\n",a,b);
  }

// pc
  a = ref_r->pc;b=cpu.pc;
  if (a!=b){
    same = false;
    printf("pc,ref:%08x   dut:%08x\n",a,b);
  }


// eflags
    a = ref_r->eflags.CF;b=cpu.eflags.CF;
    if (a!=b){
      // same = false;
      printf("CF,ref:%d   dut:%d\n",a,b);
    }

    a = ref_r->eflags.ZF;b=cpu.eflags.ZF;
    if (a!=b){
      // same = false;
      printf("ZF,ref:%d   dut:%d\n",a,b);
    }

    a = ref_r->eflags.SF;b=cpu.eflags.SF;
    if (a!=b){
      // same = false;
      printf("SF,ref:%d   dut:%d\n",a,b);
    }

    a = ref_r->eflags.OF;b=cpu.eflags.OF;
    if (a!=b){
      // same = false;
      printf("OF,ref:%d   dut:%d\n",a,b);
    }

  // printf("eflags,ref: %08x   dut: %08x\n",ref_r->eflags.val,cpu.eflags.val);
  // same = true;
  if (!same) printf("\n");
  return same;
}

void isa_difftest_attach(void) {
}
