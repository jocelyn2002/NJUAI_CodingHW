#include <stdio.h>
#include <assert.h>
#include <string.h>
#include <stdint.h>
#include <sys/types.h>
#include <dirent.h>


#define max_name_len 64
#define max_line_len 1024
#define max_proc_num 4096

struct proc {
  pid_t pid,ppid;
  char name[max_name_len];
  int used;
}; // 进程结构体，有进程号，父亲进程号，以及自己的名字
struct proc procs[max_proc_num];
struct proc* Procs[max_proc_num];
int max_proc=0; // 用来统计最大进程的个数

// 字符串转化为整形，默认无符号且不超
int s2i(char *str){
  int num = 0;
  sscanf(str,"%d",&num);
  return num;
}
// 整形转化为字符串
void i2s(int num,char* str){
  sprintf(str,"%d",num);
}

void output(int level, int index) {
  int children[max_proc_num];
  int num_of_children=0;
  int my_pid = Procs[index]->pid;
  // 打印自己的部分
  char buff[256];
  int i=0;
  for (;i<level;i++)
    buff[2*i]=buff[2*i+1]=' ';
  buff[2*i]='\0';
  strcat(buff,Procs[index]->name);
  printf("%s\n",buff);
  Procs[index]->used=1;
  // 打印可能的孩子
  for (int i=0;i<max_proc;i++)
    if (Procs[i]->ppid==my_pid)
      children[num_of_children++] = i;
  
  for (int i=0;i<num_of_children;i++)
    output(level+1,children[i]);
}

void show_V() {
  fprintf(stderr,"pstree (PSmisc) 23.1\n\
Copyright (C) 1993-2017 Werner Almesberger and Craig Small\n\
\n\
PSmisc comes with ABSOLUTELY NO WARRANTY.\n\
This is free software, and you are welcome to redistribute it under\n\
the terms of the GNU General Public License.\n\
For more information about these matters, see the files named COPYING.\n");
} // 懒得改 直接抄的pstree原文


int main(int argc, char *argv[]) {
  // 0.初始化一些常量
  for (int i=0;i<max_proc_num;i++){
    procs[i].name[0]='\0';
    procs[i].pid=procs[i].ppid=-1; // 进程号-1 在这里表示未赋值
    procs[i].used=0;
  }
  for (int i=0;i<max_proc_num;i++)
    Procs[i]=&procs[i];

  // 1.得到命令行参数，根据要求设置标识变量的数值
  int is_p=0,is_n=0,is_V=0;// 打印进程号，按pid从小到大输出一个进程的孩子，打印版本
  for (int i = 0; i < argc; i++) {
    assert(argv[i]);
    // printf("argv[%d] = %s\n", i, argv[i]);
    if (!strcmp(argv[i],"-p")||!strcmp(argv[i],"--show-pids"))
      is_p = 1;
    else if (!strcmp(argv[i],"-n")||!strcmp(argv[i],"--numeric-sort"))
      is_n = 1;
    else if (!strcmp(argv[i],"-V")||!strcmp(argv[i],"--version"))
      is_V = 1;
  }
  // printf("%d %d %d\n",is_p,is_n,is_V);
  assert(!argv[argc]);


  // 2.得到系统中所有进程的编号，保存在列表里
  struct dirent *ent;
  DIR *dir;
  assert((dir=opendir("/proc")));
  while ((ent=readdir(dir))!=NULL) {
    // printf("%s\n",ent->d_name);
    // 检查名称是否为纯数字
    for (int i=0;i<strlen(ent->d_name);i++)
      if (!(ent->d_name[i]>='0'&&ent->d_name[i]<='9'))
        goto NotNum;
    Procs[max_proc++]->pid = s2i(ent->d_name);
    // 如果不是
  NotNum:;
  }
  closedir(dir);

  // 3.对列表里的每个编号，得到他的父亲是谁
  int ppid;
  char filename[max_name_len];
  char pid[max_name_len];
  char line[max_line_len];
  FILE *fp;
  for (int i=0;i<max_proc;i++) {
    filename[0]='\0';
    strcat(filename,"/proc/");
    i2s(Procs[i]->pid,pid);
    strcat(filename,pid);
    strcat(filename,"/status");
    fp = fopen(filename,"r");
    assert(fp!=NULL);

    while (fgets(line,sizeof(line),fp)!=NULL){
      char type[max_name_len];
      sscanf(line,"%s",type);
      if (strcmp(type,"Name:")==0) {
        char *lp = &line[5];
        while (*lp==' ') lp++;
        sscanf(lp,"%s",Procs[i]->name);
      }
      else if (strcmp(type,"PPid:")==0) {
        char *lp = &line[5];
        while (*lp==' ') lp++;
        sscanf(lp,"%d",&Procs[i]->ppid);
        break; //跳出while
      }
    }
  }

  // // 打印得到的所有pid文件夹
  // for (int i=0;i<max_proc;i++){
  //   printf("%d %d %s\n",Procs[i]->pid,Procs[i]->ppid,Procs[i]->name);
  // }
  
  // 4.在内存中把树建好，按照命令行参数要求排序
  if (is_p) 
    for (int i=0;i<max_proc;i++) {
      char number_str[10];
      i2s(Procs[i]->pid,number_str);
      strcat(Procs[i]->name,"(");
      strcat(Procs[i]->name,number_str);
      strcat(Procs[i]->name,")");
    }
  
  if (is_n) 
    assert(is_n);
  
  
  // 5.打印树
  if (!is_V) {
    for (int i=0;i<max_proc;i++)
      if (Procs[i]->used==0)
        output(0,i);
  }
  else {
    show_V();
  }
  return 0;
}