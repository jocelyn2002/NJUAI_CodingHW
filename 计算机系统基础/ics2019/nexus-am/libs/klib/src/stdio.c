#include "klib.h"
#include <stdarg.h>
#if !defined(__ISA_NATIVE__) || defined(__NATIVE_USE_KLIB__)

static char hex_table[16]={'0','1','2','3','4','5','6','7','8','9','a','b','c','d','e','f'};

int printf(const char *fmt, ...) {
  static char temp[512];
  va_list local_args;
  va_start(local_args,fmt);
  int a = vsprintf(temp, fmt, local_args);
  va_end(local_args);
  char *c = temp;
  while (*c != '\0'){
    _putc(*c);
    c++;
  }
  return a;
}

int vsprintf(char *out, const char *fmt, va_list ap) {
  char *str = out;
  const char *f = fmt;
  int counter = 0;
  while (*f != '\0'){
    // 非控制字符
    if (*f != '%'){
      *str = *f;
      str++;
      f++;
      counter++;
      continue;
    }
    

    // 此时str指向字符串末尾空位，f指向 %
    // 控制字符
    f++;
    switch (*f){
      case 'd':{
        int arg = va_arg(ap,int);
        int len = 1;
        while (1){
          int tmp = arg;
          for (int i =1;i<=len;i++)
            tmp /= 10;
          if (tmp==0) break;
          len++;
        }
        for (;len>=1;len--){
          int tmp = arg;
          for (int i = 1;i<len;i++)
            tmp /= 10;
          char a = (char)(tmp%10) + '0';
          *str = a;
          str++;
          counter += 1;
        }
        break;
      }
      case 's':{
        char *arg = va_arg(ap,char *);
        int len = strlen(arg);
        strncpy(str,arg,len);
        str += len;
        counter += len; 
        break;
      }
      case 'x':{
        *str='0';
        str++;
        *str='x';
        str++;
        counter+=2;
        int arg = va_arg(ap,int);
        int len = 1;
        while (1){
          int tmp = arg;
          for (int i =1;i<=len;i++)
            tmp /= 16;
          if (tmp==0) break;
          len++;
        }
        for (;len>=1;len--){
          int tmp = arg;
          for (int i = 1;i<len;i++)
            tmp /= 16;
          *str = hex_table[tmp%16];
          str++;
          counter += 1;
        }
        
        break;
      }
      default:{
        char aa[2];
        aa[0]=*f;
        printf("\n未定义的printf格式：%s\n",aa);
      }
    }

    f++;
  }
  
  if (*str != '\0')
    *str = '\0';

  return counter;
}


int sprintf(char *out, const char *fmt, ...) {
  va_list local_args;
  va_start(local_args,fmt);
  int a = vsprintf(out, fmt, local_args);
  va_end(local_args);
  return a;
}

int snprintf(char *out, size_t n, const char *fmt, ...) {
  return 0;
}

#endif
