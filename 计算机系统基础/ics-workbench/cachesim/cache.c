#include "common.h"
#include <inttypes.h>

void mem_read(uintptr_t block_num, uint8_t *buf);
void mem_write(uintptr_t block_num, const uint8_t *buf);
static uint64_t cycle_cnt;
void cycle_increase(int n) { cycle_cnt += n; }


// TODO: implement the following functions

#define OFFSET 0x3f //　块内偏移量,0-63,即最最低6位
#define max_cache_line 2048   // 11+6 可以满足　２^17Byte的数据要求

//　cache结构
struct Cache {
  uint32_t data[16]; //  序号代表块内地址
  bool valid,dirty;  //　有效位，脏位
  uint32_t tag;      //　标记，代表取模后的内存地址高位
}line[max_cache_line];// 序号代表行号

//　三个全局宽度
static int group_lines; //  组内行数
static int total_width; //　数据总宽度
static int group_width; //　组号宽度
// 统计量
static uint64_t hit,miss;
uint64_t real_time;

// 获取高位地址
uint32_t get_tag(uintptr_t addr){
  int mod_width = group_width+BLOCK_WIDTH;
  // 通过右移实现取模
  addr >>= mod_width;
  return addr;
}
// 获取组号
uint32_t get_group_index(uintptr_t addr){
  int mod_width = BLOCK_WIDTH;
  //　右移取模
  addr >>= mod_width;
  //　遮盖获取组号
  addr &= mask_with_len(group_width);
  return addr;
}
// 获取块内地址偏移量
uint32_t get_data_index(uintptr_t addr) {
  return (addr & OFFSET)/sizeof(uint32_t);
}
// 主存块调入cache
void m2c(uintptr_t addr, int line_index){
  // 有效位设置
  line[line_index].valid = true;
  //　由地址获取tag
  line[line_index].tag = get_tag(addr);
  // 获得地址对应的内存快的起始地址
  uintptr_t start = addr >> BLOCK_WIDTH;
  mem_read(start,(uint8_t*)(&line[line_index].data[0]));
  // 脏位设置
  line[line_index].dirty = false;
  
}
// cache放入主存
void c2m(int group_num, int line_index){
  // 若修改过则采用回写法，将新内容写如主存
  if(line[line_index].dirty){
    // 主存地址某一行起始等于，tag与组号的拼接
    uintptr_t start = (line[line_index].tag << group_width)+group_num;
    mem_write(start, (uint8_t*)&line[line_index].data[0]);
  }
  // 有效位置0
  line[line_index].valid = false;
}
//检查地址对应主存是否在它对应的组当中，若在返回行号，缺失返回负数标记
int give_me_an_index(uintptr_t addr) {
    // 获取地址tag
    uint32_t tag = get_tag(addr);
    uint32_t group_num = get_group_index(addr);
    // 本组起始结束行号
    int group_start = group_num * group_lines;
    int group_end = group_start + group_lines;
    // 查找
    for (int i = group_start; i<group_end;i++){
        //　如果地址tag与行tag相同，说明命中
        if (line[i].valid && line[i].tag == tag){
          hit ++;
          return i;
        }
    }

    //进行到这儿，发现没有命中，进行内存与cache替换
    //如果有空行，将所需内存块直接放入空行中
    for(int i = group_start;i< group_end;i++){
      if(!line[i].valid){
        m2c(addr,i);
        return i;
      }
    }
    //如果没有空行，则随机替换，rand用于生成0-0x7fff随机数，进行随机替换
    int line_index = group_start + rand()%group_lines;
    c2m(group_num,line_index);
    m2c(addr,line_index);
    miss ++;

    return line_index;
}



uint32_t cache_read(uintptr_t addr) {
  int line_index = give_me_an_index(addr);
  int data_index = get_data_index(addr);

  return line[line_index].data[data_index];
}

void cache_write(uintptr_t addr, uint32_t data, uint32_t wmask) {
  int line_index = give_me_an_index(addr);
  int data_index = (addr & OFFSET)/sizeof(uint32_t);

  line[line_index].data[data_index] -= line[line_index].data[data_index]&wmask;
  line[line_index].data[data_index] += data&wmask;
  line[line_index].dirty = true;
}

void init_cache(int total_size_width, int associativity_width) {
  //　初始化统计量
  hit=miss=cycle_cnt=real_time=0;
  // 初始化三个宽度
  total_width = total_size_width;
  group_lines = exp2(associativity_width);
  group_width = total_width - associativity_width - BLOCK_WIDTH;
  // 初始化有效位脏位为0
  for (int i=0;i<exp2(total_width-BLOCK_WIDTH);i++) 
    line[i].valid = line[i].dirty = false;
}

void display_statistic(void) {
  double mean_time = (double)real_time/(hit+miss);
  double cache_percent = (double)100*hit/cycle_cnt;
  double hit_rate = (double)100*hit/(hit+miss);
  printf("Cache mean time:%f\n",mean_time);
  printf("Cache time percent:%f\n",cache_percent);
  printf("hit_rate:%f\n",hit_rate);
  printf("Workload:%f\n",mean_time*cache_percent+(100-cache_percent));
}
