#include "klib.h"

#if !defined(__ISA_NATIVE__) || defined(__NATIVE_USE_KLIB__)


void *memset(void* v,int c,size_t n) {
  if (v==NULL) return NULL;
  char *d = (char *)v;
  while (n){
    *d = c;
    n--;
  }
  return v;
} // 把v指向的n字节地址全部设为c的值
void *memcpy(void* out, const void* in, size_t n) {
  if (out==NULL || in==NULL) return NULL;
  char *s1 = (char *)out;
  const char *s2=(char*)in;
  while (n){
    *s1 = *s2;
    s1++;
    s2++;
    n--;
  }
  return out;
} // 拷贝n个字节的内存
void *memmove(void* dst, const void* src, size_t n){
  if (!(dst && src)) return NULL;
  if (dst<=src) return memcpy(dst,src,n);
  else {
    char *ptr_src = (char*)src + n -1;
    char *ptr_dst = (char*)dst + n -1;
    while (n) {
      *ptr_dst = *ptr_src;
      ptr_src--;
      ptr_dst--;
      n--;
    }
    return dst;
  }
}
int memcmp(const void* s1, const void* s2, size_t n){
  const char *ss1 = (char *)s1;
  const char *ss2=(char*)s2;
  int tmp=0;
  while (n){
    tmp = *ss1-*ss2;
    if (tmp!=0) return tmp;
    n--;
  }
  return 0;
}



size_t strlen(const char *s) {
  const char* temp = s;
  size_t len = 0;
  while (*temp != '\0'){
    len ++;
    temp ++;
  }
  return len;
} // 计算不含结尾\0的字符串长度，返回类型 无符号！！！！
char *strcat(char* dst, const char* src) {
  char* tmp = dst;
  while (*tmp!='\0')
    tmp++;
  strcpy(tmp,src);
  return dst;
} // 拼接字符串，我的方法是调用strcpy
char *strcpy(char* dst,const char* src) {
  char *d=dst;
  const char *s=src;
  while (*s!='\0'){
    *d = *s;
    d++;
    s++;
  }
  *d = '\0';
  return dst;
} // 拷贝字符串，包括\0
char *strncpy(char* dst, const char* src, size_t n) {
  char *d = dst;
  const char *s=src;
  while (n) {
      *d = *s;
      s++;
      d++;
      n--;
      if (*s=='\0') break;
  }
  while(n){
      *d = '\0';
      d++;
      n--;
  }
  return dst;
} // 拷贝n个字符,不自动添加\0
int strcmp(const char* s1, const char* s2) {
  const char *ss1 = s1;
  const char *ss2=s2;
  int result;
  while (*ss1!='\0'&&*ss2!='\0'){
    result = *ss1 - *ss2;
    if (result != 0) return result;
    ss1++;
    ss2++;
  }
  if (*ss1=='\0')
    if (*ss2=='\0')
      return 0;
    else
      return -1;
  else
    return 1;
} // 从左往右逐个比较字符串的每个字符的ascii值
int strncmp(const char* s1, const char* s2, size_t n) {
  const char *ss1 = s1;
  const char *ss2=s2;
  int result;
  while (*ss1!='\0'&&*ss2!='\0'&& n){
    result = *ss1 - *ss2;
    if (result != 0) return result;
    ss1++;
    ss2++;
    n--;
  }
  if (n==0) return 0;
  if (*ss1=='\0')
    if (*ss2=='\0')
      return 0;
    else
      return -1;
  else
    return 1;
} // 比较n个字符
// char *strtok(char* s,const char* delim);
// char *strstr(const char *, const char *);
// char *strchr(const char *s, int c);
// char *strrchr(const char *s, int c);

#endif
