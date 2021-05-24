#include "proc.h"
#include <elf.h>
#include <sys/types.h>
#include <unistd.h>


#ifdef __ISA_AM_NATIVE__
# define Elf_Ehdr Elf64_Ehdr
# define Elf_Phdr Elf64_Phdr
#else
# define Elf_Ehdr Elf32_Ehdr
# define Elf_Phdr Elf32_Phdr
#endif

extern size_t ramdisk_read(void *buf, size_t offset, size_t len);
extern int fs_open(const char *pathname, int flags, int mode);
extern size_t fs_read(int fd, void *buf, size_t count);
extern off_t fs_lseek(int fd, off_t offset, int whence);
size_t fs_start(int fd);
int fs_close(int fd);

static uintptr_t loader(PCB *pcb, const char *filename) {
  
  int fd = fs_open(filename,0,0);
  // 读入elf headers
  Elf_Ehdr ehdr;
  fs_read(fd,(void*)&ehdr,sizeof(ehdr));
  // 文件在硬盘里的绝对地址
  size_t file_start = fs_start(fd);

  // 循环读取program headers的每一个segment，并执行复制操作
  for(int i = 0; i < ehdr.e_phnum; i++){
    Elf_Phdr phdr;
    ramdisk_read((void*)&phdr,file_start+ehdr.e_phoff,ehdr.e_phentsize);

    switch(phdr.p_type){
      case PT_LOAD:{
        // Pa4.1
        // ramdisk_read((void*)phdr.p_vaddr,file_start+phdr.p_offset,phdr.p_filesz);　// 拷贝
        // memset((void*)phdr.p_vaddr+phdr.p_filesz,0,phdr.p_memsz-phdr.p_filesz);　　// 置零
      
        // PA4.2
        fs_lseek(fd, phdr.p_offset, SEEK_SET);
        int32_t file_sz = phdr.p_filesz;
        void *start_vaddr = (void *)phdr.p_vaddr;
        while (file_sz > 0) {
          void *page_vaddr = new_page(1);
          _map(&pcb->as, start_vaddr, page_vaddr, 0);
          uint32_t copy_size = min(file_sz, PGSIZE);
          // 拷贝
          fs_read(fd, page_vaddr, copy_size);
          file_sz -= copy_size;
          start_vaddr += copy_size;
        }
        file_sz = phdr.p_memsz - phdr.p_filesz;
        while (file_sz > 0) {
          void *page_vaddr = new_page(1);  
          _map(&pcb->as, start_vaddr, page_vaddr, 0);
          uint32_t copy_size = min(file_sz, PGSIZE);
          // 置零
          memset(page_vaddr, 0, copy_size);
          file_sz -= copy_size;
          start_vaddr += copy_size;
        }
        break;
      }
      default:;
    }
    ehdr.e_phoff += ehdr.e_phentsize;
  }
  fs_close(fd);
  
  return ehdr.e_entry;
}

void naive_uload(PCB *pcb, const char *filename) {
  uintptr_t entry = loader(pcb, filename);
  Log("Jump to entry = %x", entry);
  ((void(*)())entry) ();
}

void context_kload(PCB *pcb, void *entry) {
  _Area stack;
  stack.start = pcb->stack;
  stack.end = stack.start + sizeof(pcb->stack);

  pcb->cp = _kcontext(stack, entry, NULL);
}

void context_uload(PCB *pcb, const char *filename) {
  _protect(&pcb->as);
  
  uintptr_t entry = loader(pcb, filename);

  _Area stack;
  stack.start = pcb->stack;
  stack.end = stack.start + sizeof(pcb->stack);

  pcb->cp = _ucontext(&pcb->as, stack, stack, (void *)entry, NULL);
}
