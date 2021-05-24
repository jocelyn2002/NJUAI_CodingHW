#include "../include/common.h"
// 全局变量
struct structured_handler * sorted_handlers[MAX_HANDLERS];
spinlock_t handler_lock;
int nhandlers;

// 测试用函数
sem_t empty, fill;
#define P kmt->sem_wait
#define V kmt->sem_signal
void producer(void *arg) { 
  // assert(0);
  // for (int i=0;i<3;i++) {
  while(1){
    P(&empty); 
    _putc('('); 
    V(&fill);
  } 
}
void consumer(void *arg) { 
  // for (int i=0;i<3;i++) {
  while(1){
    P(&fill);  
    _putc(')'); 
    V(&empty); 
  }
}

static void os_init() {
  // 为了使用内存分配,第一个初始化pmm
  pmm->init();
  // 为了在kmt中进行on_irq,第二个初始化全局handlers列表
  nhandlers=0;
  for (int i=0;i<MAX_HANDLERS;i++)
    sorted_handlers[i] = NULL;
  const char * str = "handler_lock";
  kmt_spin_init(&handler_lock,str);
  
  kmt->init();
  dev->init();

#ifdef DHDEBUG
  kmt->sem_init(&empty, "empty", 5);  // 缓冲区大小为 5
  kmt->sem_init(&fill,  "fill",  0);
  for (int i = 0; i < 5; i++) {
    char * name = pmm->alloc(32);
    sprintf(name,"producer-%d\0",i);
    kmt->create(pmm->alloc(sizeof(task_t)), name, producer, NULL);
  }
  for (int i = 0; i < 7; i++){
    char * name = pmm->alloc(32);
    sprintf(name,"consumer-%d\0",i);
    kmt->create(pmm->alloc(sizeof(task_t)), name, consumer, NULL);
  }
#endif

  
  dprintf("-----os init success----\n");
}



static void os_run() {
  _intr_write(1);
  while (1);
}

static _Context * os_trap(_Event ev, _Context *context) {
  // dprintf("event:%d\n",ev.event);
  // 共享变量 全局handler列表需要上锁
  kmt->spin_lock(&handler_lock);
  _Context *next = NULL;
  for (int i=0;i<nhandlers;i++){
    struct structured_handler * h = sorted_handlers[i];
    dassert(h!=NULL);
    // dprintf("%x\n",h->seq);
    if (h->event == _EVENT_NULL || h->event == ev.event) {
      _Context *r = h->handler(ev, context);
      panic_on(r!=NULL && next!=NULL, "returning multiple contexts");
      if (r!=NULL) next = r;
    }
  }
  panic_on(!next, "returning NULL context");
  // panic_on(sane_context(next), "returning to invalid context");
  kmt->spin_unlock(&handler_lock);
  return next;
}

static void os_on_irq(int seq, int event, handler_t handler) {
  // 不用实现线程安全
  // 找到插入点
  int insert_point=0;
  if (nhandlers==0 || seq >= sorted_handlers[nhandlers-1]->seq)
    insert_point = nhandlers;
  else
    for (int i=0;i<nhandlers;i++) {
      if (sorted_handlers[i]->seq > seq) {
        insert_point = i;
        break;
      }
    }
  
  // 插入
  struct structured_handler * tmp = pmm->alloc(sizeof(struct structured_handler));
  dassert(tmp!=NULL);
  tmp->seq = seq;
  tmp->event = event;
  tmp->handler = handler;
  for (int i=nhandlers-1;i>=insert_point;i--)
    sorted_handlers[i+1] = sorted_handlers[i];
  sorted_handlers[insert_point] = tmp;

  nhandlers++;
  // dprintf("%d\n",nhandlers);
}


MODULE_DEF(os) = {
  .init = os_init,
  .run  = os_run,
  .trap = os_trap,
  .on_irq = os_on_irq,
};
