#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <ctype.h>
#include <sys/time.h>
#include <fcntl.h>

struct {
  char name[32];
  double time;
} sys_call[128];
double total_time =0;
int max_call = 0;

void update_value(char name[], double time) {
  total_time += time;
  for (int i=0;i<max_call;i++)
    if (strcmp(sys_call[i].name,name)==0) {
      sys_call[i].time += time;
      goto A;
    }
  
  strcpy(sys_call[max_call].name,name);
  sys_call[max_call].time = time;
  max_call ++;

A:return;
}
void update(char * buf) {
    // 解析参数 name time
    char name[32];
    memset(name,0,sizeof(name));
    char time_str[32];
    memset(time_str,0,sizeof(time_str));
    double time;
    
    int i;
    for (i=0;i<strlen(buf);i++)
      if (buf[i]=='(')
        break;
    strncpy(name,buf,i);

    int j=0;
    for (i=strlen(buf)-1;i>=0;i--) {
      if (isdigit(buf[i])){
        j = i;
        break;
      }
    }
    for (i=j;i>=0;i--)
      if (buf[i]=='<')
        break;
    i++;
    strncpy(time_str,buf+i,j-i+1);
    sscanf(time_str,"%lf",&time);

    // 更新列表
    update_value(name,time);
}
void show_value() {
  int ff[5] ={0,1,2,3,4};
  // 最小的放到4
  for (int i=0;i<=3;i++)
    if (sys_call[ff[i]].time < sys_call[ff[i+1]].time) {
      int tmp = ff[i];
      ff[i] = ff[i+1];
      ff[i+1] = tmp;
    }
  // 遍历找到最大的5个
  for (int k=5;k<max_call;k++) {
    if (sys_call[k].time > sys_call[ff[4]].time) {
      ff[4] = k;
      for (int i=0;i<=3;i++)
        if (sys_call[ff[i]].time < sys_call[ff[i+1]].time) {
          int tmp = ff[i];
          ff[i] = ff[i+1];
          ff[i+1] = tmp;
        }
    }
   
  }
  
  // 输出
  for (int i=0;i<=4;i++) {
    printf("%s (%f%%)\n",sys_call[ff[i]].name,sys_call[ff[i]].time/total_time * 100);
    fflush(stdout);
  }
  printf("\n");
  fflush(stdout);
  for (int i=0;i<80;i++) {
    putc('\0',stdout);
    fflush(stdout);
  }
}

int main(int argc, char *argv[], char *envp[]){
  char PATH[1024];
  memset(PATH,0,sizeof(PATH));
  for (int i=0;envp[i]!=NULL;i++) {
    char temp[5];
    temp[4]='\0';
    strncpy(temp,envp[i],4);
    if (strcmp(temp,"PATH")==0) {
      strcpy(PATH,(char*)&envp[i][5]);
      break;
    }
  }
  // 解析参数
  char *exec_argv[argc+6];
  exec_argv[0] = "strace";
  exec_argv[1] = "-T";
  for (int i=0;i<argc-1;i++)
    exec_argv[i+2] = argv[i+1];
  exec_argv[argc+1] = NULL;
  
  
  // 创建虚拟机
  int fildes[2];  // 0读 1写
  pipe(fildes);
  int pid = fork(); // 0子进程
  
  // 子进程
  if (pid == 0) {
    close(fildes[0]);
    int fd = open("/dev/null",O_RDWR);
    dup2(fd,fileno(stdout));
    dup2(fildes[1],fileno(stderr));
    

    int j=0;
    char filename[256];
    memset(filename,0,sizeof(filename));
    for (int i=0;i<strlen(PATH);i++) {
      filename[j]=PATH[i];
      j++;
      if (filename[j-1]==':'){
        
        filename[j-1]='\0';
        strcat(filename,"/strace");
        execve(filename, exec_argv, envp);
        
        j=0;
        memset(filename,0,sizeof(filename));
      }
    }
    strcat(filename,"/strace");
    execve(filename, exec_argv, envp);
    perror(argv[0]);
    exit(EXIT_FAILURE);
  }
  
  // 父进程
  else {
    struct timeval then,now;
    gettimeofday(&then,NULL);
    sleep(0.5);

    close(fildes[1]);
    char buf[256];
    char *bufptr = &buf[0];
    int j;

    memset(buf,0,sizeof(buf));
    while (1){
      bufptr = &buf[0];
      memset(buf,0,sizeof(buf));

      j = read(fildes[0],bufptr,1);
      if (j==0) goto Done;
      bufptr+=1;
      while (1){
        j = read(fildes[0],bufptr,1);
        if (j==0) goto Done;
        bufptr+=1;
        if (*(bufptr-1)=='\n' && *(bufptr-2)=='>')
          break;
      }
      // 解析参数
      update(buf);
      gettimeofday(&now,NULL);
      if (now.tv_sec > then.tv_sec) {
        show_value();
        then = now;
      }
    }

    Done:;
  
    return 0;
  }
}
