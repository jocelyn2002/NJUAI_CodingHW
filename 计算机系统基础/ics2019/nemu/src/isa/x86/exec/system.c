#include "cpu/exec.h"

void raise_intr(uint32_t NO, vaddr_t ret_addr); 

make_EHelper(lidt) {
  if (decinfo.isa.is_operand_size_16){
    TODO();
  }else{
  cpu.idt_limit = vaddr_read(id_dest->addr,2);
  cpu.idt_base = vaddr_read(id_dest->addr+2,4);
  }

  print_asm_template1(lidt);
}

make_EHelper(mov_r2cr) {
  // 不能直接operand_write !! reg找不到cr0 cr3
  switch (id_dest->reg) {
    case 0: cpu.cr0.val = id_src->val; break;
    case 3: cpu.cr3.val = id_src->val; break;
    default:;
  }

  print_asm("movl %%%s,%%cr%d", reg_name(id_src->reg, 4), id_dest->reg);
}

make_EHelper(mov_cr2r) {
  operand_write(id_dest,&id_src->val);

  print_asm("movl %%cr%d,%%%s", id_src->reg, reg_name(id_dest->reg, 4));

  difftest_skip_ref();
}

make_EHelper(int) {
  raise_intr(id_dest->val,decinfo.seq_pc);

  print_asm("int %s", id_dest->str);

  difftest_skip_dut(1, 2);
}

make_EHelper(iret) {
  if (decinfo.isa.is_operand_size_16){
    rtl_pop(&s0);
    decinfo.seq_pc &= 0xffff0000;
    s0 &= 0x0000ffff;
    decinfo.seq_pc += s0;
  }
  else
    rtl_pop(&decinfo.seq_pc);
  
  rtl_pop(&s0);
  cpu.cs=s0 & 0x0000ffff;

  if (decinfo.isa.is_operand_size_16){
    rtl_pop(&s0);
    cpu.eflags.val &= 0xffff0000;
    s0 &= 0x0000ffff;
    cpu.eflags.val += s0;
  }
  else
    rtl_pop(&cpu.eflags.val);

  print_asm("iret");
}

uint32_t pio_read_l(ioaddr_t);
uint32_t pio_read_w(ioaddr_t);
uint32_t pio_read_b(ioaddr_t);
void pio_write_l(ioaddr_t, uint32_t);
void pio_write_w(ioaddr_t, uint32_t);
void pio_write_b(ioaddr_t, uint32_t);

make_EHelper(in) {
  switch (id_src->width){
    case 1:{
      id_dest->val = pio_read_b(id_src->val);
      break;
    }
    case 2:
      id_dest->val = pio_read_w(id_src->val);
      break;
    case 4:
      id_dest->val = pio_read_l(id_src->val);
      break;
    default:;
  }
  operand_write(id_dest,&id_dest->val);
  print_asm_template2(in);
}

make_EHelper(out) {
  switch (id_src->width){
    case 1:{
      pio_write_b(id_dest->val,id_src->val);
      break;
    }
    case 2:
      pio_write_w(id_dest->val,id_src->val);
      break;
    case 4:
      pio_write_l(id_dest->val,id_src->val);
      break;
    default:;
  }
  // difftest_skip_ref();
  print_asm_template2(out);
}
