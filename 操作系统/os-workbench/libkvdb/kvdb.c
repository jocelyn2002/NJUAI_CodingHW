#include <stdio.h>
#include <assert.h>
#include <stdint.h>
#include <assert.h>
#include <stdlib.h>
#include <sys/file.h>
#include <sys/types.h>
#include <unistd.h>
#include <string.h>
#include <time.h>

// #define DEBUG

#define BLOCKSZ 4096
#define MAGIC 0x4b435546
enum {KEY_ALIVE,KEY_DEAD};
enum {JOURNAL_BEGIN, JOURNAL_END, JOURNAL_FREE};

struct Key {
  int32_t  magic;
  int32_t  status;
  char     name[128];
  int32_t  szblock;
  int32_t  szbyte;
}__attribute__((packed));
struct kvdb {
  int32_t start_block;
  int32_t free_block;
  int32_t fd;
  FILE * fp;
};
struct Journal {
  int32_t status;
  int32_t free_block;
}__attribute__((packed));

void may_crash() {
  #ifdef DEBUG
  int i = rand() % 16;
  printf("%d\n",i);
  if (i==0){
    // printf("may_crash\n");
    exit(0);
  }
  #endif
}
// 工具函数
void get_kvdb(struct kvdb * db) {
  FILE * tmpfp = db->fp;
  int tmpfd = db->fd;
  fseek(tmpfp,0,SEEK_SET);
  fread(db,sizeof(struct kvdb),1,tmpfp);
  db->fp = tmpfp;
  db->fd = tmpfd;
}
void sync_kvdb(struct kvdb * db) {
  fseek(db->fp,0,SEEK_SET);
  fwrite(db,sizeof(struct kvdb),1,db->fp);
  fsync(db->fd);
}
void clear_key(struct kvdb *db,const char *key) {
  int i = db->start_block;
  while (i<db->free_block){
    fseek(db->fp,i * BLOCKSZ,SEEK_SET);
    struct Key * thekey = malloc(sizeof(struct Key));
    fread(thekey,sizeof(struct Key),1,db->fp);
    // printf("cur:%d  free:%d\n",i,db->free_block);
    assert(thekey->magic==MAGIC);
    if (thekey->status==KEY_ALIVE && strcmp(key,thekey->name)==0){
      thekey->status=KEY_DEAD;
      fseek(db->fp,-sizeof(struct Key),SEEK_CUR);
      fwrite(thekey,sizeof(struct Key),1,db->fp);
    }
    i += thekey->szblock;
  }
  fsync(db->fd);
}
void put_key(struct kvdb * db,const char *key, const char *value) {
  // 移动到空闲空间
  fseek(db->fp,db->free_block * BLOCKSZ,SEEK_SET);
  // 新建Key项
  struct Key * thekey = malloc(sizeof(struct Key));
  thekey->magic = MAGIC;
  thekey->status = KEY_ALIVE;
  strcpy(thekey->name,key);
  thekey->szbyte = strlen(value);
  thekey->szblock = (thekey->szbyte + sizeof(struct Key)) / BLOCKSZ;
  int szrest = (thekey->szbyte + sizeof(struct Key))%BLOCKSZ;
  if (szrest != 0)
    thekey->szblock += 1;

  // Data write
  fseek(db->fp,sizeof(struct Key),SEEK_CUR);
  fwrite(value,1,thekey->szbyte,db->fp);
  may_crash();
  // Journal metadata write
  struct Journal * jb = malloc(sizeof(struct Journal));
  jb->status = JOURNAL_BEGIN;
  jb->free_block = db->free_block;
  fseek(db->fp,BLOCKSZ,SEEK_SET);
  fwrite(jb,sizeof(struct Journal),1,db->fp);
  fwrite(thekey,sizeof(struct Key),1,db->fp);
  fsync(db->fd);
  may_crash();
  // Journal commit
  struct Journal * je = malloc(sizeof(struct Journal));
  je->status = JOURNAL_END;
  je->free_block = db->free_block;
  fwrite(je,sizeof(struct Journal),1,db->fp);
  fsync(db->fd);
  may_crash();
  // Check point metadata  
  fseek(db->fp,db->free_block * BLOCKSZ,SEEK_SET);
  fwrite(thekey,sizeof(struct Key),1,db->fp);
  clear_key(db,key);
  fsync(db->fd);
  
  db->free_block += thekey->szblock;
  sync_kvdb(db);
  may_crash();
  // Free
  jb->status = JOURNAL_FREE;
  fseek(db->fp,BLOCKSZ,SEEK_SET);
  fwrite(jb,sizeof(struct Journal),1,db->fp);
  fsync(db->fd);
}
void journal_handling(struct kvdb * db){
  struct Journal * jb = malloc(sizeof(struct Journal));
  fseek(db->fp,BLOCKSZ,SEEK_SET);
  fread(jb,sizeof(struct Journal),1,db->fp);
  // 已经成功free情况,不需要任何操作
  if (jb->status==JOURNAL_FREE)
    return;
  else {
    struct Journal * je = malloc(sizeof(struct Journal));
    fseek(db->fp,BLOCKSZ+sizeof(struct Key)+sizeof(struct Journal),SEEK_SET);
    fread(je,sizeof(struct Journal),1,db->fp);
    // 未成功commit的情况, 认为此次写入无效
    if (jb->free_block != je->free_block)
      return;
    // 成功commit, 但是没能free, 继续完成Checkpoint metadata与free
    db->free_block = jb->free_block;
    struct Key * thekey = malloc(sizeof(struct Key));
    fseek(db->fp,BLOCKSZ+sizeof(struct Key),SEEK_SET);
    fread(thekey,sizeof(struct Key),1,db->fp);
    // Checkpoint metadata  
    fseek(db->fp,db->free_block * BLOCKSZ,SEEK_SET);
    fwrite(thekey,sizeof(struct Key),1,db->fp);
    clear_key(db,thekey->name);
    fsync(db->fd);
    
    db->free_block += thekey->szblock;
    sync_kvdb(db);
    may_crash();
    // Free
    jb->status = JOURNAL_FREE;
    fseek(db->fp,BLOCKSZ,SEEK_SET);
    fwrite(jb,sizeof(struct Journal),1,db->fp);
    fsync(db->fd);
  }
}


// 接口函数
struct kvdb *kvdb_open(const char *filename) {
  #ifdef DEBUG
  srand((unsigned int)time(NULL));
  #endif

  struct kvdb * db = malloc(sizeof(struct kvdb));
  FILE * tmpfp = fopen(filename,"r+");
  // 打开已有db
  if (tmpfp!=NULL){
    db->fp = tmpfp;
    db->fd = fileno(tmpfp);
    assert(flock(db->fd,LOCK_EX)==0);
    get_kvdb(db);
    journal_handling(db);
  }
  // 创建新db
  else {
    db->fp = fopen(filename,"w+");
    db->fd = fileno(db->fp);
    db->start_block = 3;
    db->free_block = 3;
    assert(flock(db->fd,LOCK_EX)==0);
    sync_kvdb(db);
    // 对齐
    // char align[BLOCKSZ];
    // memset(align,0,BLOCKSZ);
    // fwrite(align,1,BLOCKSZ-sizeof(struct kvdb),db->fp);
    // for (int i=1;i<=db->free_block+1;i++)
    //   fwrite(align,1,BLOCKSZ,db->fp);
    
    struct Journal * jb = malloc(sizeof(struct Journal));
    jb->status=JOURNAL_FREE;
    jb->free_block=3;
    fseek(db->fp,BLOCKSZ,SEEK_SET);
    fwrite(jb,sizeof(struct Journal),1,db->fp);
  }

  fsync(db->fd);
  assert(flock(db->fd,LOCK_UN)==0);
  return db;
}

int kvdb_close(struct kvdb *db) {
  assert(flock(db->fd,LOCK_EX)==0);
  journal_handling(db);

  fseek(db->fp,0,SEEK_SET);
  fwrite(db,sizeof(struct kvdb),1,db->fp);
  fsync(db->fd);
  assert(flock(db->fd,LOCK_UN)==0);
  return 0;
}

int kvdb_put(struct kvdb *db, const char *key, const char *value) {
  assert(flock(db->fd,LOCK_EX)==0);

  get_kvdb(db);
  journal_handling(db);
  // clear_key(db,key);
  put_key(db,key,value);
  

  assert(flock(db->fd,LOCK_UN)==0);
  return 0;
}

char *kvdb_get(struct kvdb *db, const char *key) {
  assert(flock(db->fd,LOCK_EX)==0);

  get_kvdb(db);
  journal_handling(db);

  char * ret = NULL;

  int i = db->start_block;
  // printf("%d %d\n",db->start_block,db->free_block);
  while (i<db->free_block){
    fseek(db->fp,i * BLOCKSZ,SEEK_SET);
    struct Key * thekey = malloc(sizeof(struct Key));
    fread(thekey,sizeof(struct Key),1,db->fp);
    // printf("free block:%d\n",db->free_block);
    assert(thekey->magic==MAGIC);
    // printf("%s %s\n",key,thekey->name);
    if (thekey->status==KEY_ALIVE && strcmp(key,thekey->name)==0){
      char * value = malloc(thekey->szbyte+1);
      fread(value,1,thekey->szbyte,db->fp);
      value[thekey->szbyte] = '\0';
      ret = value;
      break;
    }
    i += thekey->szblock;
  }

  // printf("%d\n",db->free_block);
  assert(flock(db->fd,LOCK_UN)==0);
  return ret;
}
