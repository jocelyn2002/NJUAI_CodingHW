#include "multimod.h"

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
