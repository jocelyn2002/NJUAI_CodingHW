#include <am.h>
#include <amdev.h>
#include <nemu.h>

#define KEYDOWN_MASK 0x8000

size_t __am_input_read(uintptr_t reg, void *buf, size_t size) {
  switch (reg) {
    case _DEVREG_INPUT_KBD: {
      uint32_t a = inl(0x60);
      uint16_t ma = a;
      int t=0;
      if ((int16_t)ma < 0)
        t = 1;
      ma <<=1;
      ma >>=1;
      _DEV_INPUT_KBD_t *kbd = (_DEV_INPUT_KBD_t *)buf;
      kbd->keydown = t;
      kbd->keycode = ma;
      // kbd->keycode = _KEY_NONE;
      return sizeof(_DEV_INPUT_KBD_t);
    }
  }
  return 0;
}
