#ifndef __CPU_DECODE_H__
#define __CPU_DECODE_H__

#include "common.h"

#define make_DHelper(name) void concat(decode_, name) (vaddr_t *pc)
typedef void (*DHelper) (vaddr_t *);

#define OP_STR_SIZE 40
enum { OP_TYPE_REG, OP_TYPE_MEM, OP_TYPE_IMM };

typedef struct {
  uint32_t type;        // 操作数类型
  int width;            // 操作数宽度(字节数)
  union {                     
    uint32_t reg;       // 寄存器
    rtlreg_t addr;      // rtl寄存器地址
    uint32_t imm;       // 无符号立即数
    int32_t simm;       // 有符号立即数  
  };
  rtlreg_t val;         // 操作数 值
  char str[OP_STR_SIZE];// 操作数 字符串写法
} Operand; // 操作数结构体

#include "isa/decode.h"

typedef struct {
  uint32_t opcode; // opcode
  uint32_t width;  // 字节数
  vaddr_t seq_pc;  // sequential pc
  bool is_jmp;     // 
  vaddr_t jmp_pc;
  Operand src, dest, src2;
  struct ISADecodeInfo isa;
} DecodeInfo; // 解码信息结构体

void operand_write(Operand *, rtlreg_t *);

/* shared by all helper functions */
extern DecodeInfo decinfo;

#define id_src (&decinfo.src)
#define id_src2 (&decinfo.src2)
#define id_dest (&decinfo.dest)

#ifdef DEBUG
#define print_Dop(...) snprintf(__VA_ARGS__)
#else
#define print_Dop(...)
#endif

#endif
