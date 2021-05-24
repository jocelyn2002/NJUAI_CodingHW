#include "multimod.h"

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