#include "cpu/exec.h"

make_EHelper(mov) {
  operand_write(id_dest, &id_src->val);
  print_asm_template2(mov);
}

make_EHelper(push) {
  if (id_dest->type==OP_TYPE_IMM)
    rtl_sext(&s0,&id_dest->val,id_dest->width);
  else
    s0 = id_dest->val;
  rtl_push(&s0);
  print_asm_template1(push);
}

make_EHelper(pop) {
  rtl_pop(&s0);
  operand_write(id_dest,&s0);
  print_asm_template1(pop);
}

make_EHelper(pusha) {
  if (decinfo.isa.is_operand_size_16){
    rtl_lr(&s0,R_SP,2);
    rtl_lr(&s1,R_AX,2);
    rtl_push(&s1);
    rtl_lr(&s1,R_CX,2);
    rtl_push(&s1);
    rtl_lr(&s1,R_DX,2);
    rtl_push(&s1);
    rtl_lr(&s1,R_BX,2);
    rtl_push(&s1);
    rtl_push(&s0);
    rtl_lr(&s1,R_BP,2);
    rtl_push(&s1);
    rtl_lr(&s1,R_SI,2);
    rtl_push(&s1);
    rtl_lr(&s1,R_DI,2);
    rtl_push(&s1);
  } else {
    rtl_lr(&s0,R_ESP,4);
    rtl_lr(&s1,R_EAX,4);
    rtl_push(&s1);
    rtl_lr(&s1,R_ECX,4);
    rtl_push(&s1);
    rtl_lr(&s1,R_EDX,4);
    rtl_push(&s1);
    rtl_lr(&s1,R_EBX,4);
    rtl_push(&s1);
    rtl_push(&s0);
    rtl_lr(&s1,R_EBP,4);
    rtl_push(&s1);
    rtl_lr(&s1,R_ESI,4);
    rtl_push(&s1);
    rtl_lr(&s1,R_EDI,4);
    rtl_push(&s1);
  }

  print_asm("pusha");
}

make_EHelper(popa) {
  if (decinfo.isa.is_operand_size_16){
    rtl_pop(&s0);
    s0 &= 0x0000ffff;
    cpu.edi &= 0xffff0000;
    cpu.edi += s0;
    rtl_pop(&s0);
    s0 &= 0x0000ffff;
    cpu.esi &= 0xffff0000;
    cpu.esi += s0;
    rtl_pop(&s0);
    s0 &= 0x0000ffff;
    cpu.ebp &= 0xffff0000;
    cpu.ebp += s0;
    rtl_pop(&s0); // skip sp
    rtl_pop(&s0);
    s0 &= 0x0000ffff;
    cpu.ebx &= 0xffff0000;
    cpu.ebx += s0;
    rtl_pop(&s0);
    s0 &= 0x0000ffff;
    cpu.edx &= 0xffff0000;
    cpu.edx += s0;
    rtl_pop(&s0);
    s0 &= 0x0000ffff;
    cpu.ecx &= 0xffff0000;
    cpu.ecx += s0;
    rtl_pop(&s0);
    s0 &= 0x0000ffff;
    cpu.eax &= 0xffff0000;
    cpu.eax += s0;
  }else{
    rtl_pop(&cpu.edi);
    rtl_pop(&cpu.esi);
    rtl_pop(&cpu.ebp);
    rtl_pop(&s0);   //skip esp
    rtl_pop(&cpu.ebx);
    rtl_pop(&cpu.edx);
    rtl_pop(&cpu.ecx);
    rtl_pop(&cpu.eax);
  }
  print_asm("popa");
}

make_EHelper(leave) {
  cpu.esp = cpu.ebp;
  rtl_pop(&s0);
  if (decinfo.isa.is_operand_size_16)
    rtl_sr(R_BP,&s0,2);
  else
    rtl_sr(R_EBP,&s0,4);

  print_asm("leave");
}

make_EHelper(cltd) {
  if (decinfo.isa.is_operand_size_16) {
    rtl_lr(&s0,R_AX,2);
    if ((int16_t)s0 < 0)
      s1 = 0xFFFF;
    else
      s1 = 0;
    rtl_sr(R_DX,&s1,2);
  }
  else{
    rtl_lr(&s0,R_EAX,4);
    if ((int32_t)s0 < 0)
      s1 = 0xFFFFFFFF;
    else
      s1 = 0;
    rtl_sr(R_EDX,&s1,4);
  }

  print_asm(decinfo.isa.is_operand_size_16 ? "cwtl" : "cltd");
}

make_EHelper(cwtl) {
  if (decinfo.isa.is_operand_size_16) {
    rtl_lr(&s0,R_AL,1);
    rtl_sext(&s0,&s0,1);
    rtl_sr(R_AX,&s0,2);
  }
  else {
    rtl_lr(&s0,R_AX,2);
    rtl_sext(&s0,&s0,2);
    rtl_sr(R_EAX,&s0,4);
  }

  print_asm(decinfo.isa.is_operand_size_16 ? "cbtw" : "cwtl");
}

make_EHelper(movsx) {
  id_dest->width = decinfo.isa.is_operand_size_16 ? 2 : 4;
  rtl_sext(&s0, &id_src->val, id_src->width);
  operand_write(id_dest, &s0);
  print_asm_template2(movsx);
}

make_EHelper(movzx) {
  id_dest->width = decinfo.isa.is_operand_size_16 ? 2 : 4;
  operand_write(id_dest, &id_src->val);
  print_asm_template2(movzx);
}

make_EHelper(lea) {
  operand_write(id_dest, &id_src->addr);
  print_asm_template2(lea);
}
