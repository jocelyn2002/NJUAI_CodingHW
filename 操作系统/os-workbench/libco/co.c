#include "co.h"
#include <stdlib.h>
#include <stdint.h>
#include <setjmp.h>
#include <assert.h>
#include <string.h>
#include <stdio.h>

#define STACK_SIZE 64*1024 // 每个协程堆栈使用不超过 64 KiB
#define CO_SIZE 128 // 任意时刻系统中的携程数量不会超过128个

static inline void stack_switch_call(void *sp, void *entry, uintptr_t arg) {
  asm volatile (
#if __x86_64__
    "movq %0, %%rsp; movq %2, %%rdi; jmp *%1"
      : : "b"((uintptr_t)sp),     "d"(entry), "a"(arg)
#else
    "movl %0, %%esp; movl %2, 4(%0); jmp *%1"
      : : "b"((uintptr_t)sp - 8), "d"(entry), "a"(arg)
#endif
  );
}

enum co_status {
  CO_NEW = 1, // 新创建，还未执行过
  CO_RUNNING, // 已经执行过
  CO_WAITING, // 在 co_wait 上等待
  CO_DEAD,    // 已经结束，但还未释放资源
};

struct co {
  char name[20];
  void (*func)(void *); // co_start 指定的入口地址和参数
  void *arg;

  enum co_status status;  // 协程的状态
  struct co *    waiter;  // 是否有其他协程在等待当前协程
  struct co*     waiting;
  jmp_buf        context; // 寄存器现场 (setjmp.h)
  uint8_t        stack[STACK_SIZE]; // 协程的堆栈
};

struct co* co_pointer[CO_SIZE];
unsigned co_num=0;
struct co* co_this;

struct func_arg {
  void (*func)(void *);
  void *arg;
};

void wrapper(void* func_arg) {
  struct func_arg* fna=(struct func_arg*)func_arg;
  void (*func)(void *)=fna->func;
  void *arg = fna->arg;
  // printf("arg=%s\n",(char*)arg);
  func(arg);
  co_this->status=CO_DEAD;
  co_yield();
}

struct co *co_start(const char *name, void (*func)(void *), void *arg) {
  // 最初运行，还没有main
  if (co_num==0) {
    struct co* co_main = malloc(sizeof(struct co));
    strcpy(co_main->name,"main");
    co_main->status = CO_RUNNING;
    co_main->waiter=NULL;
    co_main->waiting=NULL;

    co_pointer[co_num]=co_main;
    co_num++;
    co_this = co_main;
    // printf("successfully start:%s\n","main");
  }
  // 创建新携程
  struct func_arg *fna=malloc(sizeof(struct func_arg));
  fna->func=func;
  fna->arg=arg;
  // printf("arg=%s\n",(char*)arg);

  struct co* tmp = malloc(sizeof(struct co));
  strcpy(tmp->name,name);
  tmp->func = wrapper;
  tmp->arg = fna;
  tmp->status = CO_NEW;
  tmp->waiter = NULL;
  tmp->waiting = NULL;
  memset(&tmp->stack[0],0,sizeof(tmp->stack));
  
  co_pointer[co_num]=tmp;
  co_num++;
  // printf("successfully start:%s\n",name);
  return tmp;
}

void co_wait(struct co *co) {
  while (co->status!=CO_DEAD) {
    // printf("%s wait %s\n",co_this->name,co->name);
    co_this->status=CO_WAITING;
    co_this->waiting = co;
    co->waiter = co_this;
    co_yield();
  }
  // 从co列表中删除这一项
  // printf("deleting %s\n",co->name);  
  int i;
  for (i=0;i<co_num;i++)
    if (co_pointer[i]==co)
      break;
  for (int j=i;j<co_num-1;j++)
    co_pointer[j]=co_pointer[j+1];
  
  // 释放空间
  free(co->arg);
  free(co);
  co_this->waiting = NULL;
  co_this->status = CO_RUNNING;
  co_num--;
}

void co_yield() {
  if (setjmp(co_this->context)==0){
    // printf("setjmp\n");
    int index = 0;
    if (co_num>0) {
      index = rand() % co_num;
      while (co_pointer[index]->status==CO_DEAD)
        index = rand() % co_num;
    }
    co_this=co_pointer[index];
    // printf("total:%d id:%d switch to: %s\n",co_num,index,co_this->name);
    switch (co_pointer[index]->status) {
      case CO_NEW:
        co_this->status=CO_RUNNING;
        stack_switch_call(&co_this->stack[STACK_SIZE],co_this->func,(uintptr_t)co_this->arg);
        break;
      case CO_RUNNING:
      case CO_WAITING:
        longjmp(co_this->context,1);
        break;
      default:
        printf("\n fuck u wrong %d\n",co_pointer[index]->status);
        assert(0);
    }
  }
  else {
    ;
    // for (int k=0;k<co_num;k++)
    //   printf("%s_%d  ",co_pointer[k]->name,co_pointer[k]->status);
    // printf("longjmp:%s\n",co_this->name);
  }
}
