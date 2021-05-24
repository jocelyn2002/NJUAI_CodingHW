#include "fs.h"

typedef size_t (*ReadFn) (void *buf, size_t offset, size_t len);
typedef size_t (*WriteFn) (const void *buf, size_t offset, size_t len);

typedef struct {
  char *name;
  size_t size;
  size_t disk_offset; // 在硬盘里的偏移量
  size_t open_offset; // 当前指针位置
  ReadFn read;
  WriteFn write;
} Finfo;

enum {FD_STDIN, FD_STDOUT, FD_STDERR, FD_FB};

size_t ramdisk_read(void *buf, size_t offset, size_t len);
size_t ramdisk_write(const void *buf, size_t offset, size_t len);
size_t invalid_read(void *buf, size_t offset, size_t len) {
  panic("should not reach here");
  return 0;
}
size_t invalid_write(const void *buf, size_t offset, size_t len) {
  panic("should not reach here");
  return 0;
}
size_t serial_write(const void *buf, size_t offset, size_t count);
size_t events_read(void *buf, size_t offset, size_t len);
size_t fb_write(const void *buf, size_t offset, size_t len);
size_t fbsync_write(const void *buf, size_t offset, size_t len);
size_t dispinfo_read(void *buf, size_t offset, size_t len);

/* This is the information about all files in disk. */
static Finfo file_table[] __attribute__((used)) = {
  {"stdin", 0, 0, 0, invalid_read, invalid_write},
  {"stdout", 0, 0, 0, invalid_read, serial_write},
  {"stderr", 0, 0, 0, invalid_read, serial_write},
  {"/dev/events",0, 0, 0, events_read, invalid_write},
  {"/dev/fb",0,0,0,invalid_read,fb_write},
  {"/dev/fbsync",1,0,0,invalid_read,fbsync_write},
  {"/proc/dispinfo",0,0,0,dispinfo_read,invalid_write},
  {"/dev/tty",0,0,0,invalid_read,serial_write},
#include "files.h"
};

#define NR_FILES (sizeof(file_table) / sizeof(file_table[0]))

int fs_open(const char *pathname, int flags, int mode){
  for (int i=0;i<NR_FILES;i++){
    if (strcmp(pathname,file_table[i].name)==0){
      return i;
    }
  }
  // 不应该找不到
  printf("找不到文件%s\n",pathname);
  assert(0);
  return -1;
}
size_t fs_read(int fd, void *buf, size_t len){
  // 计算长度
  size_t actual_len = len;  
  // 有与没有写函数
  if (file_table[fd].read!=NULL){
    if (file_table[fd].size && file_table[fd].open_offset + len > file_table[fd].size) {
      actual_len = file_table[fd].size - file_table[fd].open_offset;
    }
    actual_len = file_table[fd].read(buf,file_table[fd].open_offset,actual_len);
  }
  else{
    if (file_table[fd].open_offset+len >= file_table[fd].size)
      actual_len = file_table[fd].size - file_table[fd].open_offset;
    actual_len = ramdisk_read(buf, file_table[fd].disk_offset+file_table[fd].open_offset, actual_len);
  }
  // 更新与返回
  file_table[fd].open_offset += actual_len;
  return actual_len;
}
size_t fs_write(int fd, const void *buf, size_t len){
  // 计算长度
  size_t actual_len = len;  
  // 有与没有写函数
  if (file_table[fd].write!=NULL){
    if (file_table[fd].size && file_table[fd].open_offset + len > file_table[fd].size) {
      actual_len = file_table[fd].size - file_table[fd].open_offset;
    }
    file_table[fd].write(buf,file_table[fd].open_offset,actual_len);
  }
  else{
    if (file_table[fd].open_offset+len >= file_table[fd].size)
      actual_len = file_table[fd].size - file_table[fd].open_offset;
    ramdisk_write(buf, file_table[fd].disk_offset+file_table[fd].open_offset, actual_len);
  }
  // 更新与返回
  file_table[fd].open_offset += actual_len;
  return actual_len;
}
size_t fs_lseek(int fd, size_t offset, int whence){
  switch (whence){
    case SEEK_SET:
      file_table[fd].open_offset = offset;
      break;
    case SEEK_CUR:
      file_table[fd].open_offset += offset;
      break;
    case SEEK_END:
      file_table[fd].open_offset = file_table[fd].size+offset;
      break;
    
    default:;
  }
  // 不要越过边界
  if (file_table[fd].open_offset > file_table[fd].size) 
    file_table[fd].open_offset = file_table[fd].size;
  if (file_table[fd].open_offset < 0)
    file_table[fd].open_offset = 0;
  
  return file_table[fd].open_offset;
}
int fs_close(int fd){
  file_table[fd].open_offset = 0;
  return 0;
}
size_t fs_start(int fd){
  return file_table[fd].disk_offset;
}// 我自己写的，获得文件在硬盘里的首地址


int dispsize();
void init_fs() {
  // initialize the size of /dev/fb
  int fd = fs_open("/dev/fb",0,0);
  file_table[fd].size = 4 * screen_height() * screen_width();
  fd = fs_open("/proc/dispinfo",0,0);
  file_table[fd].size = dispsize();
}

