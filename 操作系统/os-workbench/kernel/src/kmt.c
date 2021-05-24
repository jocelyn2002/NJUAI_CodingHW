#include "../include/common.h"

extern struct structured_handler * sorted_handlers[MAX_HANDLERS];

struct cpu_local CPU[MAX_CPUS];
task_t * tasks[MAX_TASKS];

int ncpus, ntasks;
spinlock_t task_lock;

_Context* kmt_context_save(_Event ev, _Context *ctx) {
  if (my_current == NULL) { // 首次调度
    my_idle->context = ctx;
    my_current = my_idle;
  } else {
    my_current->context = ctx;
  }

  // 维护last
  if (my_last != NULL)
    my_last->wait = 0;
  my_last = my_current;

  // 打印切换前线程
  // dprintf("%s(%d) -> ",my_current->name,my_current->cpu);

  return NULL;
}

_Context* kmt_schedule(_Event ev, _Context *ctx) {
  kmt->spin_lock(&task_lock);

  task_t *next = my_idle;
  for (int n = ntasks;n;n--) {
    my_i = (my_i + 1) % ntasks;
    dassert(tasks[my_i]!=NULL);
    if (tasks[my_i]->wait == 0) {
      next = tasks[my_i];
      break;
    }
  }
  my_current = next;

  // 维护wait
  my_current -> wait = 1;
  
  // 打印切换后线程
  // dprintf("%s(%d)\n",my_current->name,my_current->cpu);
  
  kmt->spin_unlock(&task_lock);
  return my_current->context;
}

static void kmt_init() {
  // task初始化
  ntasks = 0;
  for (int i=0;i<MAX_TASKS;i++)
    tasks[i]=NULL;
  kmt_spin_init(&task_lock, "task_lock");
  
  // CPU初始化
  ncpus = _ncpu();
  dprintf("have %d cpus\n",ncpus);
  for (int i=0;i<ncpus;i++) {
    CPU[i].last = NULL;
    CPU[i].current = NULL;
    CPU[i].intr_on = 0;
    CPU[i].hold_locks = 0;
    CPU[i].current_i = -1;
    // 分配idle: 纯空线程
    CPU[i].idle = pmm->alloc(sizeof(task_t));
    char * idname = pmm->alloc(32);
    sprintf(idname,"IDLE-%d\0",i);
    CPU[i].idle->name = idname;
    CPU[i].idle->stack = NULL;
    CPU[i].idle->context = NULL;
  }

  //注册调度处理函数
  os->on_irq(INT_MIN, _EVENT_NULL, kmt_context_save);   // 总是最先调用
  os->on_irq(INT_MAX, _EVENT_NULL, kmt_schedule);       // 总是最后调用
  dassert(sorted_handlers[0]->seq == INT_MIN);
  dassert(sorted_handlers[1]->seq == INT_MAX);

  dprintf("-----kmt init success-----\n");
}
static int kmt_create(task_t *task, const char *name, void (*entry)(void *arg), void *arg){
	// 共享变量,ntasks,tasks
  kmt_spin_lock(&task_lock);
  
  dassert(ntasks<MAX_TASKS);
  tasks[ntasks] = task;
  task->wait = 0;
  task->name = name;
  task->stack = pmm->alloc(STACKSZ);
  _Area tmp_Are = {.start = task->stack, .end = task->stack + STACKSZ};
  task->context = _kcontext(tmp_Are,entry,arg);

  dprintf("%d %s\n",ntasks,task->name);
  ntasks++;

  kmt_spin_unlock(&task_lock);
  return 0;
}
static void kmt_teardown(task_t *task){
  kmt_spin_lock(&task_lock);
  
  // 获取要删除的task编号
  int del = MAX_TASKS;
  for (int i=0;i<ntasks;i++)
    if (tasks[i] == task) {
      del = i;
      break;
    }
  dassert(0<=del && del<MAX_TASKS);
  
  // 删除task
  pmm->free(task->stack);
  pmm->free(task);
  for (int i=del;i<=ntasks-1;i++) {
    tasks[i] = tasks[i+1];
  }

  ntasks--;

  kmt_spin_unlock(&task_lock);
}

MODULE_DEF(kmt) = {
  .init =  kmt_init,
  .create = kmt_create,
  .teardown = kmt_teardown,
  .spin_init = kmt_spin_init,
  .spin_lock  = kmt_spin_lock,
  .spin_unlock = kmt_spin_unlock,
  .sem_init = kmt_sem_init,
  .sem_wait = kmt_sem_wait,
  .sem_signal = kmt_sem_signal,
};