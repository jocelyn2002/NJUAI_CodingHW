#include "perf.h"
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <assert.h>
#include <stdint.h>
#include <sys/time.h>
#include <math.h>

#define DECL(fn) void fn();

PROGRAMS(DECL)

static void run(void (*func)(), int rounds);
static uint64_t gettime();
static void (*lookup(const char *fn))();


int64_t aa=18;
int64_t bb=0x7fffffffffffffff;
int64_t mm=16;


int main(int argc, char **argv) {
  // TODO: parse arguments: set @func and @rounds
  int rounds = 1;
  void (*func)() = lookup("dummy");
  if (argc==4 && strcmp(argv[1],"-r")==0){
    sscanf(argv[2],"%d",&rounds);
    func = lookup(argv[3]);
  }
  else if (argc==2){
    func = lookup(argv[1]);
  }
  run(func, rounds); 

}

static uint64_t gettime() {
  // TODO: implement me!
  struct timeval timenow;
  gettimeofday(&timenow,NULL);
  return (uint64_t)1000000*timenow.tv_sec+timenow.tv_usec;
}

static void (*lookup(const char *fn))() {
  #define PAIR(fn) { #fn, fn },
  struct pair {
    const char *name;
    void *ptr;
  };
  struct pair lut[] = {
    PROGRAMS(PAIR)
  };

  for (int i = 0; i < LENGTH(lut); i++) {
    struct pair *p = &lut[i];
    if (strcmp(fn, p->name) == 0) return p->ptr;
  }
  return print_error;
}

static void run(void (*func)(), int rounds) {
  uint64_t *elapsed = malloc(sizeof(uint64_t) * rounds);
  if (!elapsed) {
    perror("elapsed");
    return;
  }
  // 获得开始时间
  uint64_t star = gettime();

  for (int round = 0; round < rounds; round++) {
    uint64_t st = gettime();
    func();
    uint64_t ed = gettime();
    elapsed[round] = ed - st;
    // printf("%ld\n",ed-st);
  }

  uint64_t ende = gettime();
  // TODO: display runtime statistics
  uint64_t total=ende-star; //样本总时间
  double mean = total/(double)rounds; // 样本均值
  // printf("%f\n",mean);
  
  double var = 0; // 样本方差
  uint64_t max=1, //最大值
  min = 0x0ffffffffffffffff;// 最小值
  for (int i=0;i<rounds;i++){
    if (elapsed[i]>max) max=elapsed[i];
    else if (elapsed[i]<min) min=elapsed[i];
    var += pow((elapsed[i]-mean),2);
  }
  var /= rounds;
  uint64_t range = max-min; // 样本极差

  printf("共运行:%d 次\n共耗时:%ld 微秒\n最大耗时:%ld\n最小耗时:%ld\n极差:%ld\n平均耗时:%f\n方差:%f\n",
  rounds,total,max,min,range,mean,var);

  


  free(elapsed);
}