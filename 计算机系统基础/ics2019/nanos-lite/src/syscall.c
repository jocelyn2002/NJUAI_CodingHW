#include "common.h"
#include "syscall.h"
#include "fs.h"
#include "proc.h"


void naive_uload(PCB *pcb, const char *filename);
int mm_brk(uintptr_t brk, intptr_t increment);


intptr_t sys_yield(){
  printf("sys_yield!\n");
  _yield();
  return 0;
}
intptr_t sys_open(const char *pathname, int flags, int mode){
  return fs_open(pathname,flags,mode);
}
intptr_t sys_write(int fd, void *buf, size_t count){
  return fs_write(fd,buf,count);
};
intptr_t sys_brk(uintptr_t brk, intptr_t increment){
  return mm_brk(brk,increment);
}
intptr_t sys_read(int fd, void *buf, size_t len){
  return fs_read(fd, buf, len);
}
intptr_t sys_close(int fd){
  return fs_close(fd);
}
intptr_t sys_lseek(int fd, size_t offset, int whence){
  return fs_lseek(fd,offset,whence);
}
intptr_t sys_execve(const char *fname, char * const argv[], char *const envp[]){
  naive_uload(NULL, fname);
  return 0;
}
void sys_exit(int arg){
  printf("sys_exit!\n");
  // sys_execve("/bin/init",NULL,NULL);
  _halt(arg);
}


_Context* do_syscall(_Context *c) {
  uintptr_t a[4];
  a[0] = c->GPR1;
  a[1] = c->GPR2;
  a[2] = c->GPR3;
  a[3] = c->GPR4;
  
  // printf("eve_syscal:");
  // for (int i=0;i<4;i++)
  //   printf("%d ",a[i]);
  // printf("\n");

  switch (a[0]) {
    case SYS_yield:c->GPRx=sys_yield();break;
    case SYS_exit:sys_exit(a[1]);break;
    case SYS_write:c->GPRx=sys_write((int)a[1],(void*)a[2],(size_t)a[3]);break;
    case SYS_brk:c->GPRx=sys_brk(a[1],a[2]);break;
    case SYS_open:c->GPRx=sys_open((const char *)a[1],a[2],a[3]);break;
    case SYS_read:c->GPRx=sys_read(a[1],(void*)a[2],a[3]);break;
    case SYS_close:c->GPRx=sys_close(a[1]);break;
    case SYS_lseek:c->GPRx=sys_lseek(a[1],a[2],a[3]);break;
    case SYS_execve:c->GPRx=sys_execve((const char*)a[1],(char * const*)a[2],(char * const*)a[3]);break;
    default:
      panic("Unhandled syscall ID = %d", a[0]);
  }
  return c;
}