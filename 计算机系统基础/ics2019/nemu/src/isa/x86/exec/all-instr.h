#include "cpu/exec.h"
// initial
make_EHelper(mov);          // data-mov.c       ok
make_EHelper(operand_size); // prefix.c         ok
make_EHelper(inv);          // special.c        ok
make_EHelper(nemu_trap);    // special.c        ok
// dummy.c
make_EHelper(call);         // control.c
make_EHelper(push);         // data-mov.c
make_EHelper(sub);          // arith.c
make_EHelper(xor);          // logic.c
make_EHelper(ret);          // control.c
// add.c
make_EHelper(lea);          // data-mov.c       ok
make_EHelper(and);          // logic.c
make_EHelper(add);          // arith.c
make_EHelper(cmp);          // arith.c
make_EHelper(setcc);        // logic.c
make_EHelper(movzx);        // data-mov.c       ok
make_EHelper(test);         // logic.c
make_EHelper(jcc);          // control.c        ok
make_EHelper(leave);        // data-mov.c
make_EHelper(inc);          // arith.c
make_EHelper(pop);          // data-mov.c
// add-longlong.c
make_EHelper(nop);          // special.c        ok
make_EHelper(adc);          // arith.c          ok(modified)
make_EHelper(or);           // logic.c
make_EHelper(sar);          // logic.c          
make_EHelper(shl);          // logic.c          
// bit.c
make_EHelper(dec);          // arith.c
make_EHelper(not);          // logic.c
// bubble-sort.c
// div.c
make_EHelper(imul2);        // arith.c          ok
make_EHelper(cltd);         // data-mov.c
make_EHelper(idiv);         // arith.c          ok
// fact.c
make_EHelper(jmp);          // control.c        ok
// fib.c
// goldbach.c
// if-else.c
// leap-year.c
// load-store.c
make_EHelper(movsx);        // data-mov.c       ok
// matrix-mul.c
// max.c
// min3.c
// mov-c.c
// movsx.c
// mul-longlong.c
make_EHelper(imul1);        // arith.c          ok
// pascal.c
// prime.c
// quick-sort.c
// recursion.c
make_EHelper(call_rm);      // control.c
make_EHelper(jmp_rm);       // control.c        ok
// select-sort.c
// shift.c
make_EHelper(shr);          // logic.c          ok
// shuixianhua.c
make_EHelper(mul);          // arith.c          ok
// sub-longlong.c
make_EHelper(sbb);          // arith.c          ok(modified)
// sum.c
// switch.c
// to-lower-case
// unalign.c

// hello-str
// string.c
make_EHelper(neg);          // arith.c

// amtest
make_EHelper(out);          // system.c
make_EHelper(in);           // system.c

make_EHelper(div);          // arith.c          ok
make_EHelper(cwtl);         // data-mov.c
make_EHelper(imul3);        // arith.c          ok

// src里面没有函数原型的指令
make_EHelper(rol);          // logic.c
make_EHelper(rcl);          // logic.c
make_EHelper(ror);          // logic.c
make_EHelper(rcr);          // logic.c


// pa3
make_EHelper(lidt);         // system.c
make_EHelper(int);          // system.c
make_EHelper(pusha);        // data-mov.c
make_EHelper(popa);         // data-mov.c
make_EHelper(iret);         // system.c
make_EHelper(mov_r2cr); 
make_EHelper(mov_cr2r); 