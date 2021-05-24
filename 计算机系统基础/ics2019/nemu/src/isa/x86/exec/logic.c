#include "cpu/exec.h"
#include "cc.h"

make_EHelper(test) {
  rtl_and(&s1,&id_dest->val,&id_src->val);
  s0 = 0;
  rtl_set_CF(&s0);
  rtl_set_OF(&s0);
  
  // rtl_andi(&s1, &s1, 0xffffffffu >> ((4 - id_dest->width) * 8));
  rtl_update_ZFSF(&s1,id_dest->width);
  print_asm_template2(test);
}

make_EHelper(and) {
  // 和
  rtl_sext(&s1,&id_src->val,id_src->width);
  rtl_and(&s0,&id_dest->val,&s1);
  operand_write(id_dest,&s0);
  // 置0 CF,OF  更新ZF,SF
  rtl_update_ZFSF(&s0,id_dest->width);
  s0=0;
  rtl_set_CF(&s0);
  rtl_set_OF(&s0);
  print_asm_template2(and);
}

make_EHelper(xor) {
  rtl_xor(&s0,&id_dest->val,&id_src->val);
  operand_write(id_dest,&s0);
  // 更新符号位
  rtl_update_ZFSF(&s0,id_src->width);
  s1 = 0;
  rtl_set_CF(&s1);
  rtl_set_OF(&s1);
  print_asm_template2(xor);
}

make_EHelper(or) {
  rtl_or(&s0,&id_dest->val,&id_src->val);
  operand_write(id_dest,&s0);
  //设置符号位
  rtl_update_ZFSF(&s0,id_dest->width);
  s0 = 0;
  rtl_set_CF(&s0);
  rtl_set_OF(&s0);

  print_asm_template2(or);
}

make_EHelper(sar) {
  // unnecessary to update CF and OF in NEMU
  // printf("dest:%08x\n",id_dest->val);
  // printf("src:%08x\n",id_src->val);
  s0 = id_src->val;
  while (s0 != 0){
      // 更新CF
      // 循环有符号除法
      s1 = 1;
      rtl_sar(&id_dest->val,&id_dest->val,&s1);
      s0 -= 1;
  }
  // 更新OF
  // 更新ZFSF
  if (id_src->val!=0){
    operand_write(id_dest,&id_dest->val);
    rtl_update_ZFSF(&id_dest->val,id_dest->width);
  }
  print_asm_template2(sar);
}

make_EHelper(shl) {
  // printf("%08x\n",id_dest->val);
  // printf("%08x\n",id_src->val);
  // unnecessary to update CF and OF in NEMU
  s0 = id_src->val;
  while (s0 != 0){
    // CF := high-order bit of r/m;
    // r/m := r/m * 2;
    s2 = 2;
    rtl_imul_lo(&id_dest->val,&id_dest->val,&s2);
    s0 -= 1;
  }
  // if (id_src->val == 1){
    // OF := high-order bit of r/m <> (CF);
  //}// ELSE OF := undefined;
  if (id_src->val!=0){
    operand_write(id_dest,&id_dest->val);
    rtl_update_ZFSF(&id_dest->val,id_dest->width);
  }

  print_asm_template2(shl);
}


make_EHelper(shr) {
  // unnecessary to update CF and OF in NEMU
  s0 = id_src->val;
  while (s0 != 0){
    // CF := low-order bit of r/m;
    // r/m := r/m / 2; (* Unsigned divide *);
    s2 = 2;
    rtl_div_q(&id_dest->val,&id_dest->val,&s2);
    s0 -= 1;
  }
  if (id_src->val!=0){
    operand_write(id_dest,&id_dest->val);
    rtl_update_ZFSF(&id_dest->val,id_dest->width);
  }

  print_asm_template2(shr);
}

make_EHelper(setcc) {
  uint32_t cc = decinfo.opcode & 0xf;

  rtl_setcc(&s0, cc);
  operand_write(id_dest, &s0);

  print_asm("set%s %s", get_cc_name(cc), id_dest->str);
}

make_EHelper(not) {
  rtl_not(&id_dest->val,&id_dest->val);
  operand_write(id_dest,&id_dest->val);

  print_asm_template1(not);
}


// 自建
make_EHelper(rol){
  s0 = id_src->val;
  s2 = id_dest->val;
  while (s0!=0){
    rtl_msb(&s1,&s2,id_dest->width);
    s2 *=2;
    s2+=s1;
    s0--;
  }
  operand_write(id_dest,&s2);
  // 更新符号位，同上，CFOF暂不更新

  // if (id_src == 1)
  // {
  //   rtl_msb(&s1,&s2,id_dest->width);
  //   rtl_get_CF(&s0);
  //   if (s1 != s0)
  //     s2 = 1;
  //   else
  //     s2 = 0;
  //   rtl_set_OF(&s2);
  // }
  // ELSE OF := undefined;

  print_asm_template2(rol);
}
make_EHelper(rcl){
  s0 = id_src->val;
  while (s0!=0){
    rtl_msb(&s1,&id_dest->val,id_dest->val);
    rtl_get_CF(&s2);
    id_dest->val <<= 1;
    id_dest->val += s2;
    rtl_set_CF(&s1);
    s0--;
  }
  operand_write(id_dest,&id_dest->val);
  print_asm_template2(rcl);
}
make_EHelper(rcr){
  s0 = id_src->val;
  while (s0!=0){
    s1 = 0x1;
    s1 |= id_dest->val;
    rtl_get_CF(&s2);
    id_dest->val >>= 1;
    id_dest->val += (s2<<(id_dest->width-1));
    rtl_set_CF(&s1);
    s0--;
  }
  operand_write(id_dest,&id_dest->val);
  print_asm_template2(rcr);
}
make_EHelper(ror){
  s0 = id_src->val;
  while(s0!=0){
    s1 = 0x1;
    s1 |= id_dest->val;
    id_dest->val >>= 1;
    id_dest->val += (s1<<(8*id_dest->width-1));
    s0--;
  }
  operand_write(id_dest,&id_dest->val);
  print_asm_template2(ror);
}