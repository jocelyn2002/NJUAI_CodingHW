#include "monitor/watchpoint.h"
#include "monitor/expr.h"

#define NR_WP 32

uint32_t expr(char*,bool*);

static WP wp_pool[NR_WP] = {};

void init_wp_pool() {
  int i;
  for (i=0;i<NR_WP;i++){
    wp_pool[i].NO=i;
    wp_pool[i].used=false;
    wp_pool[i].pre_value=0;
  }
}

int new_wp(char *expression){
  int i;
  for (i=0;i<NR_WP;i++)
    if (wp_pool[i].used==false){
      wp_pool[i].used=true;
      strcpy(wp_pool[i].watch_expression,expression);
      return i;
    }
  return 0;
}
void free_wp(int n_watch){
  wp_pool[n_watch].used=0;
}
void show_wp(){
  for (int i=0;i<NR_WP;i++)
    if(wp_pool[i].used==true)
      printf("NO.%d  %s: %d\n",i,wp_pool[i].watch_expression,wp_pool[i].pre_value);
}
bool watch_wp(){
  bool changed=false;
  for (int i=0;i<NR_WP;i++)
    if (wp_pool[i].used==true){
      bool bb=false;
      bool *aa=&bb;
      uint32_t now_value = expr(wp_pool[i].watch_expression,aa);
      if (now_value!=wp_pool[i].pre_value){
        //printf("NO.%d  %d  %s\n",i,now_value,wp_pool[i].watch_expression);
        wp_pool[i].pre_value = now_value;
        changed = true;
      }
    }
  if (changed==true)
    show_wp();
  return changed;
}


