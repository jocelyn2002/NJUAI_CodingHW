#include "perf.h"
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

void dummy() {
}

void print_hello() {
  printf("hello\n");
}

void print_error() {
  printf("invalid subject!\n");
  exit(1);
}

void simple_loop() {
  for (volatile int i = 0; i < 1000000; i++) ;
}

extern int64_t aa,bb,mm;
// multimod
int64_t multimod_p1(int64_t a, int64_t b, int64_t m) {
  uint64_t ah = a & 0xffffffff00000000,
           al = a & 0x00000000ffffffff,
           bh = b & 0xffffffff00000000,
           bl = b & 0x00000000ffffffff,
           m2 = m;
  ah >>= 32;
  bh >>= 32;
  // [ahbh*2^64+(albh+ahbl)*2^32+albl ] mod m
  // u1 最多 (2^31-1)^2=2^62-2^32+1
  uint64_t u1=(ah*bh)%m2; 
  for (int i=0;i<64;i++){
    u1 <<= 1;
    u1 %= m2;
  }

  // u2 最多 (2^31-1)^(2^32-1)=2^63-2^32-2^31+1
  uint64_t u2=(((ah*bl)%m2)+((al*bh)%m2))%m2; 
  for (int i=0;i<32;i++){
    u2 <<= 1;
    u2 %= m2;
  }
  uint64_t u3 = (al*bl)%m2; // 最后一项不会溢出

  return (int64_t)((((u1%m2)+(u2%m2))%m2)+(u3%m2))%m2;
}
int64_t multimod_p2(int64_t a, int64_t b, int64_t m) {
  
  uint64_t aa=a,bb=b,mm = m;
  uint64_t unit = aa % mm;
  uint64_t answer = 0;

  // 把bb逆序为cc
  uint64_t cc=0;
  while(bb){
    cc <<= 1;
    cc += (bb&1);
    bb >>= 1; 
  }
  // 将原bb最高位放到现在的最低位
  while((!cc&1) && cc)
    cc >>= 1;

  // 展开计算
  while (cc>1){
    if (cc&1){
      answer += unit;
      answer %= mm;
    }
    answer <<= 1;
    answer %= mm;
    cc >>= 1;
  }
  // 对第一位
  if (cc&1){
      answer += unit;
      answer %= mm;
  }

  return (int64_t)answer;
}
int64_t multimod_p3(int64_t a, int64_t b, int64_t m) {
  int64_t t = (a * b - (int64_t)((double)a * b / m) * m) % m;
  return t < 0 ? t + m : t;
}

void m1(){
  volatile int64_t un = multimod_p1(aa, bb, mm);
  un+=1;
}
void m2(){
  volatile int64_t un = multimod_p2(aa, bb, mm);
  un+=1;
  // printf("%ld\n",un-1);
}
void m3(){
  volatile int64_t un = multimod_p3(aa, bb, mm);
  un+=1;
}
