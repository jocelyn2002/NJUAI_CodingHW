#include "rtl/rtl.h"

/* Condition Code */

void rtl_setcc(rtlreg_t* dest, uint8_t subcode) {
  bool invert = subcode & 0x1;
  enum {
    CC_O, CC_NO, CC_B,  CC_NB,
    CC_E, CC_NE, CC_BE, CC_NBE,
    CC_S, CC_NS, CC_P,  CC_NP,
    CC_L, CC_NL, CC_LE, CC_NLE
  };

  // TODO: Query EFLAGS to determine whether the condition code is satisfied.
  // dest <- ( cc is satisfied ? 1 : 0)
  switch (subcode & 0xe) {
    case CC_O:{
      rtl_get_OF(&t0);
      *dest = t0;
      break;
    }
    case CC_B:{
      rtl_get_CF(&t0);
      *dest = t0;
      break;
    }
    case CC_E:{
      rtl_get_ZF(&t0);
      *dest = t0;
      break;
    }
    case CC_BE:{
      rtl_get_CF(&t0);
      rtl_get_ZF(&t1);
      rtl_or(dest,&t0,&t1);
      break;
    }
    case CC_S:{
      rtl_get_SF(&t0);
      *dest = t0;
      break;
    }
    case CC_L:{
      rtl_get_SF(&t0);
      rtl_get_OF(&t1);
      *dest = (t0!=t1);
      break;
    }
    case CC_LE:{
      rtl_get_SF(&t0);
      rtl_get_OF(&t1);
      *dest = (t0!=t1);
      rtl_get_ZF(&t0);
      *dest = *dest || t0;
      break;
    }
    default:{
      printf("？？？？：%d\n",subcode & 0xe);
      panic("should not reach here");
    }
    case CC_P: panic("n86 does not have PF");
  }

  if (invert) {
    rtl_xori(dest, dest, 0x1);
  }
  assert(*dest == 0 || *dest == 1);
}
