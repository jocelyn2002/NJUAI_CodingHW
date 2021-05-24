#include "common.h"
#include <amdev.h>

// 为了避免反复调用函数，存一下
static int width,height;

size_t serial_write(const void *buf, size_t offset, size_t count) {
  size_t return_value = count;
  char* abyte=(char*)buf;
  for (;count>0;count--){
    if (!*abyte) break;
    _putc(*abyte);
    abyte++;
  }
  return_value -= count;
  return return_value;
}

#define NAME(key) \
  [_KEY_##key] = #key,

static const char *keyname[256] __attribute__((used)) = {
  [_KEY_NONE] = "NONE",
  _KEYS(NAME)
};

extern int fg_pcb;
size_t events_read(void *buf, size_t offset, size_t len) {
  // 没有按键事件时才返回时钟事件
  int key = read_key();
  int down = 0;
  if (key & 0x8000) {
    key ^= 0x8000;
    down = 1;
  }
  // 无按键事件
  if (key == _KEY_NONE){
    int time = uptime();
    return sprintf(buf,"t %d\n",time);
  }
  // 按下
  else if (down==1){
    switch (key) {
      case _KEY_F1: Log("F1_first_pal"); fg_pcb = 1; break;
      case _KEY_F2: Log("F2_second_pal"); fg_pcb = 2; break;
      case _KEY_F3: Log("F3_third_pal"); fg_pcb = 3; break;
      default: break;
    }
    return sprintf(buf,"kd %s\n",keyname[key]);
  }
  // 松开
  else{
    return sprintf(buf,"ku %s\n",keyname[key]);
  }
}

static char dispinfo[128] __attribute__((used)) = {};

size_t dispinfo_read(void *buf, size_t offset, size_t len) {
  strncpy(buf,dispinfo+offset,len);
  return len;
}

size_t fb_write(const void *buf, size_t offset, size_t len) {
  // 2.最后, 我们还需要在serial_write(), events_read() 和fb_write()的开头调用_yield(), 来模拟设备访问缓慢的情况. 
  // _yield();


  size_t actual_len = len;
  if (offset+len > width*height*4)
    actual_len = width*height*4 - offset; 
  int x=(offset/4)%width;
  int y=(offset/4)/width;
  draw_rect((void *)buf, x, y, actual_len/4, 1);
  return actual_len;
}
// size_t fb_write(const void *buf, size_t offset, size_t len) {
//   int x, y;
//   assert(offset + len <= (size_t)height * width * 4);
//   x = (offset / 4) % width;
//   y = (offset / 4) / width;
//   assert(x + len < (size_t)width * 4);
//   draw_rect((void *)buf, x, y, len / 4, 1);
//   return len;
// }
size_t fbsync_write(const void *buf, size_t offset, size_t len) {
  draw_sync();
  return len;
}


void init_device() {
  Log("Initializing devices...");
  _ioe_init();
  width = screen_width();
  height = screen_height();
  // TODO: print the string to array `dispinfo` with the format
  // described in the Navy-apps convention
  sprintf(dispinfo,"WIDTH:%d\nHEIGHT:%d\n",width,height);
}

int dispsize(){
  return strlen(dispinfo);
}