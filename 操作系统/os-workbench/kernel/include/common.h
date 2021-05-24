// #ifndef DHDEBUG
//   #define DHDEBUG
// #endif
#include <kernel.h>
#include <klib.h>
#include <klib-macros.h>
#include "./utility.h"
#include "./lock_sem.h"
#include <sys/time.h>
#include <sys/types.h>

#define MAX_CPUS 8
#define MAGIC 0x4b435546 // 也就是小端方式表示的的 "FUCK"
#define INT_MAX __INT_MAX__
#define INT_MIN (-INT_MAX - 1)




/* ---------- Lab1-pmm ---------- */
#define NUMSLAB 9 // 每个CPU分配1,2,4,8,16,32,64,128,4096共9个slab区域
#define NBITMAP 16 // 64*16=1024
enum {SPACE_FREE,SPACE_USED}; // 用于space_header的status字段

struct space_header {
  int status;
  size_t size;
  struct space_header* prev;
  struct space_header* next;
};

// 假设slab_header总大小为1MiB, 第一个page用于存放metadata, 后面紧跟255个page
#define SLABSZ (1<<20)
#define SLAB_BEGIN(addr) (void*)(ROUNDDOWN(addr,SLABSZ)) // 由块内地址快速获得slab起始地址
#define ITEM_NUM(addr,slab_begin,itemsz) (((intptr_t)addr - ((intptr_t)slab_begin + 4096)) / itemsz + 1)
#define ITEM_ADDR(slab_begin,itemsz,item_num) (void*)((intptr_t)slab_begin + 4096 + itemsz*(item_num-1))

struct slab_header {
	struct space_header sph; // (暂未启用)整个slab作为空闲链表中的一个分配空间, 可以用空闲链表方法回收
	struct slab_header *next; // 指向下一个slab, 用于扩容
  
	spinlock_t lock; // 保护本slab metadata的自旋锁

	int32_t magic; // 魔数, 用于校验
  int32_t item_size; // 分配数据大小, 目前只有4096一种
  int32_t item_num;  // slab总大小
	int32_t bitmap_num; // bitmap的实际uint32_t数量
	int32_t is_full; // 标记此slab是否已经全满
  
  uint32_t bitmap;  // 之后的空余空间全部用于bitmap,可任意扩展到4kb上限
};




/* ---------- Lab2-kmt ---------- */
#define MAX_TASKS 40
#define MAX_HANDLERS 20
#define STACKSZ 4096

struct task {
	int wait; // 此task是否可以被调度
	const char * name;
	_Context *context; // 初始由_kcontext生成,在栈顶
	void  *stack; // 指向堆栈起始地址指针,需回收
};
struct cpu_local {
	task_t * idle; // 每个cpu专属的idle线程
	task_t * last; //上一线程
	task_t * current; // 当前线程
	int current_i; // 当前线程在线程列表中的编号
	int intr_on; // 在自旋锁关中断之前是否处于开中断
	int hold_locks; // 当前持有锁的数量 
};
struct structured_handler {
  int seq;
  int event;
  handler_t handler;
};

#define my_cpu	CPU[_cpu()]
#define my_last CPU[_cpu()].last
#define my_current	CPU[_cpu()].current
#define my_idle	CPU[_cpu()].idle
#define my_i	CPU[_cpu()].current_i

extern struct cpu_local CPU[MAX_CPUS];
extern task_t * tasks[MAX_TASKS];
extern int ncpus, ntasks,  nhandlers;
extern spinlock_t task_lock, handler_lock;




// ---------- Lab3 ----------