#ifndef __RTL_RTL_H__
#define __RTL_RTL_H__

#include "nemu.h"
#include "rtl/c_op.h"
#include "rtl/relop.h"
#include "rtl/rtl-wrapper.h"


/* 约定：优先用dest,
t01在rtl指令实现中用，
s01在姨妈服主函数和执行辅助函数中用*/
extern rtlreg_t s0, s1, s2, t0, t1, ir;


void decinfo_set_jmp(bool is_jmp);
bool interpret_relop(uint32_t relop, const rtlreg_t src1, const rtlreg_t src2);

/* RTL basic instructions */

static inline void interpret_rtl_li(rtlreg_t* dest, uint32_t imm) {
  *dest = imm;
}// 立即数到寄存器

static inline void interpret_rtl_mv(rtlreg_t* dest, const rtlreg_t *src1) {

  *dest = *src1;
}// 寄存器到寄存器


// 32位寄存器类型的算数、逻辑运算
#define make_rtl_arith_logic(name) \
  static inline void concat(interpret_rtl_, name) (rtlreg_t* dest, const rtlreg_t* src1, const rtlreg_t* src2) { \
    *dest = concat(c_, name) (*src1, *src2); \
  } \
  /* Actually those of imm version are pseudo rtl instructions,
   * but we define them here in the same macro */ \
  static inline void concat(rtl_, name ## i) (rtlreg_t* dest, const rtlreg_t* src1, int imm) { \
    rtl_li(&ir, imm); \
    rtl_ ## name (dest, src1, &ir); \
  } 

make_rtl_arith_logic(add) // 加
make_rtl_arith_logic(sub) // 减
make_rtl_arith_logic(and) // 和
make_rtl_arith_logic(or)  // 或
make_rtl_arith_logic(xor) // 异或
make_rtl_arith_logic(shl) // 逻辑左移（一律补0）
make_rtl_arith_logic(shr) // 逻辑右移（一律补0）
make_rtl_arith_logic(sar) // 算数右移（补最高位的值）
make_rtl_arith_logic(mul_lo) // 乘法取低位
make_rtl_arith_logic(mul_hi) // 乘法取高位
make_rtl_arith_logic(imul_lo)// 带符号乘法取低位
make_rtl_arith_logic(imul_hi)// 带符号乘法取高位
make_rtl_arith_logic(div_q)  // 整除
make_rtl_arith_logic(div_r)  // 取余
make_rtl_arith_logic(idiv_q) // 带符号整除
make_rtl_arith_logic(idiv_r) // 带符号取余

//被除数位64位的除法运算，同上4种模式
static inline void interpret_rtl_div64_q(rtlreg_t* dest,
    const rtlreg_t* src1_hi, const rtlreg_t* src1_lo, const rtlreg_t* src2) {
  uint64_t dividend = ((uint64_t)(*src1_hi) << 32) | (*src1_lo);
  uint32_t divisor = (*src2);
  *dest = dividend / divisor;
}
static inline void interpret_rtl_div64_r(rtlreg_t* dest,
    const rtlreg_t* src1_hi, const rtlreg_t* src1_lo, const rtlreg_t* src2) {
  uint64_t dividend = ((uint64_t)(*src1_hi) << 32) | (*src1_lo);
  uint32_t divisor = (*src2);
  *dest = dividend % divisor;
}
static inline void interpret_rtl_idiv64_q(rtlreg_t* dest,
    const rtlreg_t* src1_hi, const rtlreg_t* src1_lo, const rtlreg_t* src2) {
  int64_t dividend = ((uint64_t)(*src1_hi) << 32) | (*src1_lo);
  int32_t divisor = (*src2);
  *dest = dividend / divisor;
}
static inline void interpret_rtl_idiv64_r(rtlreg_t* dest,
    const rtlreg_t* src1_hi, const rtlreg_t* src1_lo, const rtlreg_t* src2) {
  int64_t dividend = ((uint64_t)(*src1_hi) << 32) | (*src1_lo);
  int32_t divisor = (*src2);
  *dest = dividend % divisor;
}


static inline void interpret_rtl_lm(rtlreg_t *dest, const rtlreg_t* addr, int len) {
  *dest = vaddr_read(*addr, len);
} // guest内存读取（读取虚拟内存）

static inline void interpret_rtl_sm(const rtlreg_t* addr, const rtlreg_t* src1, int len) {
  vaddr_write(*addr, *src1, len);
} // guest内存写入（写入虚拟内存）

static inline void interpret_rtl_host_lm(rtlreg_t* dest, const void *addr, int len) {
  switch (len) {
    case 4: *dest = *(uint32_t *)addr; return;
    case 1: *dest = *( uint8_t *)addr; return;
    case 2: *dest = *(uint16_t *)addr; return;
    default: assert(0);
  }
} // host内存读取(操作寄存器)

static inline void interpret_rtl_host_sm(void *addr, const rtlreg_t *src1, int len) {
  switch (len) {
    case 4: *(uint32_t *)addr = *src1; return;
    case 1: *( uint8_t *)addr = *src1; return;
    case 2: *(uint16_t *)addr = *src1; return;
    default: assert(0);
  }
} // host内存写入（操作寄存器）

static inline void interpret_rtl_setrelop(uint32_t relop, rtlreg_t *dest,
    const rtlreg_t *src1, const rtlreg_t *src2) {
  *dest = interpret_relop(relop, *src1, *src2);
} // 条件跳转

static inline void interpret_rtl_j(vaddr_t target) {
  cpu.pc = target;
  decinfo_set_jmp(true);
} // 直接跳转（参数是地址，跳转到地址）

static inline void interpret_rtl_jr(rtlreg_t *target) {
  cpu.pc = *target;
  decinfo_set_jmp(true);
} // 间接跳转(参数是地址指针，跳转到所指向地址)

static inline void interpret_rtl_jrelop(uint32_t relop,
    const rtlreg_t *src1, const rtlreg_t *src2, vaddr_t target) {
  bool is_jmp = interpret_relop(relop, *src1, *src2);
  if (is_jmp) cpu.pc = target;
  decinfo_set_jmp(is_jmp);
} // 依据interpret_relop 得出的条件，条件跳转

void interpret_rtl_exit(int state, vaddr_t halt_pc, uint32_t halt_ret);
// 终止nemu

/* RTL pseudo instructions */
static inline void rtl_setrelopi(uint32_t relop, rtlreg_t *dest,
    const rtlreg_t *src1, int imm) {
  rtl_li(&ir, imm);
  rtl_setrelop(relop, dest, src1, &ir);
} // 用立即数设置relop

static inline void rtl_not(rtlreg_t *dest, const rtlreg_t* src1) {
 *dest = ~*src1;
} // 按位取反

static inline void rtl_sext(rtlreg_t* dest, const rtlreg_t* src1, int width) {
  t0 = 8*(4-width);
  rtl_shl(&t1,src1,&t0);
  rtl_sar(dest,&t1,&t0);
} // 符号扩展(扩展为32位)

static inline void rtl_msb(rtlreg_t* dest, const rtlreg_t* src1, int width) {
  rtl_sext(&t0,src1,width);
  *dest = ((int32_t)t0) < 0;
} // 获取操作数符号位

static inline void rtl_mux(rtlreg_t* dest, const rtlreg_t* cond, const rtlreg_t* src1, const rtlreg_t* src2) {
  *dest = *cond ? *src1 : *src2;
} // 当cond不为0时赋给dest src1,否则src2

#include "isa/rtl.h"

#endif