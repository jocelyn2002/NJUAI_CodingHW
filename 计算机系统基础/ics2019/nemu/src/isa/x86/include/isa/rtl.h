#ifndef __X86_RTL_H__
#define __X86_RTL_H__

#include "rtl/rtl.h"

/* RTL pseudo instructions */

static inline void rtl_lr(rtlreg_t* dest, int r, int width) {
  switch (width) {
    case 4: rtl_mv(dest, &reg_l(r)); return;
    case 1: rtl_host_lm(dest, &reg_b(r), 1); return;
    case 2: rtl_host_lm(dest, &reg_w(r), 2); return;
    default: assert(0);
  }
} // 把r号寄存器的值读入dest，区分宽度

static inline void rtl_sr(int r, const rtlreg_t* src1, int width) {
  switch (width) {
    case 4: 
      // printf("\ndest=%08x",reg_l(r));
      // printf("\nsrc1=%08x",*src1);
      rtl_mv(&reg_l(r), src1); 
      return;
    case 1: rtl_host_sm(&reg_b(r), src1, 1); return;
    case 2: rtl_host_sm(&reg_w(r), src1, 2); return;
    default: assert(0);
  }
} // 把src1写入r号寄存器，区分宽度

static inline void rtl_push(const rtlreg_t* src1) {
  cpu.esp -= 4;
  rtl_sm(&cpu.esp,src1,4);//M[esp] = src1;
} // 进栈

static inline void rtl_pop(rtlreg_t* dest) {
  rtl_lm(dest,&cpu.esp,4);//dest <- M[esp]
  cpu.esp += 4;
} // 出栈

static inline void rtl_is_sub_overflow(rtlreg_t* dest,
    const rtlreg_t* res, const rtlreg_t* src1, const rtlreg_t* src2, int width) {
  // dest <- is_overflow(src1 - src2)
  t0 = (((int32_t)*src1 >=0) == ((int32_t)*src2 < 0));
  t1 = (((int32_t)*res < 0)  !=  ((int32_t)*src1 < 0 ));
  *dest =  t0 && t1;
} //有符号数减法溢出（正减负的负，负减正得正）
static inline void rtl_is_sub_carry(rtlreg_t* dest,
    const rtlreg_t* res, const rtlreg_t* src1) {
  // dest <- is_carry(src1 - src2)
  *dest = (rtlreg_t)(*src1<*res);
} // 无符号数减法借位
static inline void rtl_is_add_overflow(rtlreg_t* dest,
    const rtlreg_t* res, const rtlreg_t* src1, const rtlreg_t* src2, int width) {
  // dest <- is_overflow(src1 + src2)
  t0 = (((int32_t)*src1 < 0) == ((int32_t)*src2 < 0));
  t1 = (((int32_t)*res < 0)  !=  ((int32_t)*src1 < 0 ));
  *dest =  t0 && t1;
} // 有符号数加法溢出
static inline void rtl_is_add_carry(rtlreg_t* dest,
    const rtlreg_t* res, const rtlreg_t* src1) {
  // dest <- is_carry(src1 + src2)
  *dest = (*res<*src1);
} // 无符号数加法进位

#define make_rtl_setget_eflags(f) \
  static inline void concat(rtl_set_, f) (const rtlreg_t* src) { \
    cpu.eflags.f = *src; \
  } \
  static inline void concat(rtl_get_, f) (rtlreg_t* dest) { \
    *dest = cpu.eflags.f; \
  }

make_rtl_setget_eflags(CF)
make_rtl_setget_eflags(OF)
make_rtl_setget_eflags(ZF)
make_rtl_setget_eflags(SF)

static inline void rtl_update_ZF(const rtlreg_t* result, int width) {
  // eflags.ZF <- is_zero(result[width * 8 - 1 .. 0])
  t1 = 8*(4 - width);
  rtl_shl(&t0, result, &t1);
  if(t0 == 0) cpu.eflags.ZF = 1;
  else cpu.eflags.ZF = 0;
} // 更新0标志

static inline void rtl_update_SF(const rtlreg_t* result, int width) {
  // eflags.SF <- is_sign(result[width * 8 - 1 .. 0])
  rtl_msb(&t0, result, width);
  cpu.eflags.SF = t0;
} // 更新符号标志

static inline void rtl_update_ZFSF(const rtlreg_t* result, int width) {
  rtl_update_ZF(result, width);
  rtl_update_SF(result, width);
} // 同时更新ZFSF

#endif
