#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <assert.h>
#include <pthread.h>
#include <semaphore.h>

struct thread {
  int id;
  pthread_t thread;
  void (*entry)(int);
  struct thread *next;
};

struct thread *threads;
void (*join_fn)();

// ========== Basics ==========

__attribute__((destructor)) static void join_all() {
  for (struct thread *next; threads; threads = next) {
    pthread_join(threads->thread, NULL);
    next = threads->next;
    free(threads);
  }
  join_fn ? join_fn() : (void)0;
}

static inline void *entry_all(void *arg) {
  struct thread *thread = (struct thread *)arg;
  thread->entry(thread->id);
  return NULL;
}

static inline void create(void *fn) {
  struct thread *cur = (struct thread *)malloc(sizeof(struct thread));
  assert(cur);
  cur->id    = threads ? threads->id + 1 : 0;
  cur->next  = threads;
  cur->entry = (void (*)(int))fn;
  threads    = cur;
  pthread_create(&cur->thread, NULL, entry_all, cur);
}

static inline void join(void (*fn)()) {
  join_fn = fn;
}

