#include "kvdb.h"
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <dlfcn.h>
#include <fcntl.h>
#include <sys/wait.h>
#include <assert.h>


int main() {
  struct kvdb *db;
  const char *key1 = "operating-systems";
  const char *key2 = "ICS";
  char *value;

  db = kvdb_open("a.db");// 打开数据库
  assert(db!=NULL);

  kvdb_put(db, key1, "three-easy-pieces"); // db[key] = "three-easy-pieces"
  
  kvdb_put(db, key2, "STFW");
  
  value = kvdb_get(db, key2); // value = db[key];
  printf("[%s]: [%s]\n", key2, value);
  value = kvdb_get(db, key1);
  printf("[%s]: [%s]\n", key1, value);

  kvdb_close(db); // 关闭数据库
  free(value);
  return 0;
}