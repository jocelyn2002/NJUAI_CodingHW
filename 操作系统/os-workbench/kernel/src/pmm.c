#include "../include/common.h"
#include <math.h>

// 全局变量
struct space_header* free_head; // 全局空闲链表头, 无大小, 占位置
spinlock_t head_lock; // 保护全局链表的一把大锁

struct slab_header *slab_entry[MAX_CPUS];
void* slab_ptr; // 用来标记当前最前面slab的起始地址
spinlock_t slab_ptr_lock;

// slab尝试
static int alloc_shift(size_t raw_size) {// 获取对齐到2^i的i
  uint32_t size = (uint32_t)raw_size;
  dassert(size > 0);
  int mask = 31 - __builtin_clz(size);
  dassert(0<=mask && mask<=12);
  if (size & (~((uint32_t)1<<mask))){ // 本身不为整2^i情况
    // dprintf("+1 %x %d\n",raw_size,mask+1);
    return mask+1;
  }
  else {
    // dprintf("+0 %x %d\n",raw_size, mask);
    return mask;
  }
}
static void bitmap_clear(struct slab_header* sh, int item_n) {
  item_n -= 1; // 转化为下标
  int bitmap_n = item_n / 32;
  int bit_n = item_n % 32;
  // dprintf("%d %d %x %x   ",bitmap_n,bit_n,*(uint32_t*)((void*)&sh->bitmap + bitmap_n*4),(~((uint32_t)1<<bit_n)));
  *(uint32_t*)((void*)&sh->bitmap + bitmap_n*4) &= (~((uint32_t)1<<(bit_n)));
}
static int get_item(struct slab_header * sh){// 从一个slab中找到一个空闲位
  // 找到bitmap组
  int bitmap_n = -1;
  int bit_n = -1;
  uint32_t tmp;
  for (int i=0;i<sh->bitmap_num;i++){
    tmp = *(uint32_t*)((void*)&sh->bitmap + i*4);
    if (~tmp){ // 如果还有0位
      bitmap_n = i;
      bit_n = __builtin_ffs(~tmp);
      *(uint32_t*)((void*)&sh->bitmap + i*4) |= 1<<(bit_n-1);
      break;
    }
  }
  int ret = bitmap_n*32+bit_n;
  // dprintf("ret:%d\n",ret);
  return ret;
}
static struct slab_header * create_slab(int sz_shift) {// 新建一个slab,返回其首地址
  kmt_spin_lock(&slab_ptr_lock);
  slab_ptr -= SLABSZ;
  struct slab_header * sh = slab_ptr;
  kmt_spin_unlock(&slab_ptr_lock);
  kmt_spin_lock(&head_lock);
  free_head->prev->size-= SLABSZ;
  kmt_spin_unlock(&head_lock);

  sh->next=NULL;
  kmt_spin_init(&sh->lock,NULL);
  sh->magic=MAGIC;
  sh->item_size = 1<<sz_shift;
  sh->item_num = (SLABSZ-4096) / sh->item_size;
  sh->bitmap_num = (sh->item_num) / 32;
  memset(&sh->bitmap,0,4096+4-sizeof(struct slab_header));
  int res = sh->item_num % 32;
  if (res != 0) {
    sh->bitmap_num++;
    uint32_t *tmp = (uint32_t*)((void*)&sh->bitmap+(sh->bitmap_num-1)*4);
    *tmp |= (~(uint32_t)0)<<res;
  }

  sh->is_full = 0;
  // dprintf("slab ptr at:%x\n",slab_ptr);
  return sh;
}

static void* slab_alloc(size_t raw_size) {// 基于slab分配, 成功返回指针, 失败返回NULL
  int cpu = _cpu();
  // int sz_shift = alloc_shift(raw_size);
  int sz_shift = 12;

  struct slab_header* sh = slab_entry[cpu];
  dassert(sh->magic == MAGIC);
  dassert(sh->item_size == 1<<sz_shift);

  void * ret = NULL;

  kmt_spin_lock(&sh->lock);
  while (sh->is_full) {
    struct slab_header* next = sh->next;
    kmt_spin_lock(&next->lock);
    kmt_spin_unlock(&sh->lock);
    sh = next;
  }

  dassert(!sh->is_full);

  int item_n = get_item(sh);
  // dprintf("item_n:%d\n",item_n);
  if (item_n >= 0){
    ret = ITEM_ADDR(sh,sh->item_size,item_n);
    kmt_spin_unlock(&sh->lock);
  }
  else {
    sh->is_full = 1;
    struct slab_header * sh_next;
    if (sh->next == NULL){
      sh_next = create_slab(sz_shift);
      sh->next = sh_next;
    }
    else
      sh_next = sh->next;
    kmt_spin_lock(&sh_next->lock);
    kmt_spin_unlock(&sh->lock);
    item_n = get_item(sh_next);
    dassert(item_n>=0);
    ret = ITEM_ADDR(sh_next,sh_next->item_size,item_n);
    kmt_spin_unlock(&sh_next->lock);
  }

  return ret;
}
static int slab_free(void* ptr) {// 基于slab回收,成功返回0,失败返回-1
    struct slab_header * sh = SLAB_BEGIN(ptr);
    // dprintf("sh: %x\n",sh);
    dassert(sh->magic==MAGIC);
    int item_n = ITEM_NUM(ptr,sh,sh->item_size);
    kmt_spin_lock(&sh->lock);
    bitmap_clear(sh, item_n);
    sh->is_full = 0;
    // dprintf("watch:%x  item_n:%d addr:%x\n",*(uint32_t*)((void*)&sh->bitmap + 7*4),item_n,ptr);
    kmt_spin_unlock(&sh->lock);
    return 0;
}


// 慢速分配回收
static void* split(struct space_header* h,size_t aligne, size_t s) {
  struct space_header* this_node = (struct space_header*)((char*)h+aligne-sizeof(struct space_header));
  struct space_header* next_node = (struct space_header*)((char*)this_node + sizeof(struct space_header)+s);
  
  void* ret = (void*)((char*)this_node + sizeof(struct space_header));
  this_node->status = SPACE_USED;
  this_node->size = s;
  
  next_node->status = SPACE_FREE;
  next_node->size = h->size-aligne-s; // header与空区域一道算
  next_node->next = h->next;
  next_node->prev = h;
  
  h->size = aligne-sizeof(struct space_header); // 代表可用分配区域大小
  h->next->prev = next_node;
  h->next = next_node;
  
  return ret;
}
static void *slow_alloc(size_t size) {
  int mask = alloc_shift(size);
  // 采用first fit
  kmt_spin_lock(&head_lock);
  struct space_header* tmp = free_head->next;
  do {
    size_t aligne_size = ((1 << mask) - ((intptr_t)tmp % (1 << mask)));
    while (aligne_size < 2*sizeof(struct space_header)) aligne_size += 1<<mask;
    if (tmp->size >=  aligne_size + size + sizeof(struct space_header)) {
      void* ret = split(tmp,aligne_size,size);
      kmt_spin_unlock(&head_lock);
      // dassert(((intptr_t)ret - (((intptr_t)ret>>mask)<<mask))==0);
      return ret;
    }
    tmp = tmp->next;
  } while(tmp != free_head);
  
  kmt_spin_unlock(&head_lock);
  return NULL;
}
static void slow_free(void* ptr){
  kmt_spin_lock(&head_lock);
  struct space_header* h = ptr-sizeof(struct space_header);
  // 把自己建立起来
  h->status = SPACE_FREE;
  h->size+=sizeof(struct space_header);
  // 后向合并
  struct space_header* nnode = ptr-sizeof(struct space_header) + h->size;
  if (nnode!=free_head && nnode->status == SPACE_FREE) {
    h->size += nnode->size;
    
    h->next = nnode->next;
    h->prev = nnode->prev;
    h->next->prev = h;
    h->prev->next = h;
    
    // 前向合并
    struct space_header* pnode = h->prev;
    if (pnode!=free_head && (void*)pnode + pnode->size == (void*)h) {
      pnode->size += h->size;
      pnode->next = h->next;
      pnode->next->prev = pnode;
    }

    kmt_spin_unlock(&head_lock);
    return;
  }

  struct space_header* next_node = free_head->next;
  while (next_node!=free_head && next_node<h) {
    next_node = next_node->next;
  }
  struct space_header* prev_node = next_node->prev;
  
  prev_node->next = h;
  h->prev = prev_node;
  next_node->prev = h;
  h->next = next_node;

  if (prev_node!=free_head && (void*)prev_node + prev_node->size == (void*)h) {
      prev_node->size += h->size;
      prev_node->next = h->next;
      prev_node->next->prev = prev_node;
  }

  kmt_spin_unlock(&head_lock);
}


static void pmm_init() {
  // 空闲双向循环链表的"哨兵"
  free_head = (struct space_header*) _heap.start;
  free_head->status = SPACE_USED;
  free_head->size = 0;

  // 空闲链表真正的第一个元素
  struct space_header* first = free_head+1;
  first->status = SPACE_FREE;
  first->size = _heap.end -_heap.start - sizeof(struct space_header);

  free_head->next = first;
  free_head->prev = first;
  first->next = free_head;
  first->prev = free_head;
  
  kmt_spin_init(&head_lock,NULL);
  

  // 预分配每个CPU的slab结构体
  slab_ptr = _heap.end;
  kmt_spin_init(&slab_ptr_lock,NULL);
  for (int i=0;i<_ncpu();i++) {
    struct slab_header *sh = create_slab(12);
    slab_entry[i] = sh;
  }
  void * ttmp = slab_alloc(4096);
  slab_free(ttmp);

  size_t pmsize = ((uintptr_t)_heap.end - (uintptr_t)_heap.start);
  
  dprintf("Got %d MiB heap: [%p, %p)\n", pmsize >> 20, _heap.start, _heap.end);
  dprintf("-----pmm init success-----\n");
}
static void *kalloc(size_t size) {
  int in = _intr_read();
  _intr_write(0);

  void *ret;
  // if (size==4096){
  //   ret = slab_alloc(size);
  //   dassert(ret!=NULL);
  //   return ret;
  // }
  // else
    ret = slow_alloc(size);

  if (in) _intr_write(1);
  return ret;
}
static void kfree(void *ptr) {
  int in = _intr_read();
  _intr_write(0);

  // if (ptr > slab_ptr)
  //   slab_free(ptr);
  // else
    slow_free(ptr);
  
  if (in) _intr_write(1);
}


MODULE_DEF(pmm) = {
  .init  = pmm_init,
  .alloc = kalloc,
  .free  = kfree,
};



