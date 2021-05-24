#include "nemu.h"

paddr_t page_translate(vaddr_t addr) {
  // 从一级页表获得二级页表
  PDE DE;
  DE.val = paddr_read(cpu.cr3.val + PDX(addr) * sizeof(PDE), sizeof(PDE)); 
  assert(DE.present);
  // 从二级页表获得页框
  PTE TE;
  TE.val = paddr_read((DE.page_frame<<12) + PTX(addr) * sizeof(PTE), sizeof(PTE));
  assert(TE.present);
  // 从页框获得实地址
  paddr_t paddr = (TE.page_frame<<12) | OFF(addr);
  return paddr;
}

uint32_t isa_vaddr_read(vaddr_t addr, int len) {
  // 开启分页
  if (cpu.cr0.paging == 1) {
    uint32_t p_start = PTE_ADDR(addr);
    uint32_t p_end = PTE_ADDR(addr + len - 1);
    // 跨页
    if (p_start != p_end) {
      uint8_t bytes[4];
      for (int i = 0; i < len; i++)
        bytes[i] = isa_vaddr_read(addr + i, 1);
      
      return *(uint32_t *)bytes;
    }
    // 不跨页
    else {
      paddr_t paddr = page_translate(addr);
      return paddr_read(paddr, len);
    }
  }
  // 未开启分页
  else
    return paddr_read(addr, len);
}

void isa_vaddr_write(vaddr_t addr, uint32_t data, int len) {
  // 开启分页
  if (cpu.cr0.paging == 1) {
    uint32_t p_start = PTE_ADDR(addr);
    uint32_t p_end = PTE_ADDR(addr + len - 1);
    // 跨页
    if (p_start != p_end) {
      uint8_t bytes[4];
      
      *(uint32_t *)bytes = data;
      for (int i = 0; i < len; i++)
        isa_vaddr_write(addr + i, bytes[i], 1);
    }
    // 不跨页
    else {
      paddr_t paddr = page_translate(addr);
      paddr_write(paddr, data, len);
    }
  }
  //　未开启分页
  else
    paddr_write(addr, data, len); 
}