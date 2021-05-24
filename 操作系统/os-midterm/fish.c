#include "threads.h"

// Allowed libraries:
// * pthread_mutex_lock, pthread_mutex_unlock
// * pthread_cond_wait, pthread_cond_signal, pthread_cond_broadcast
// * sem_init, sem_wait, sem_post


pthread_cond_t cond;
pthread_mutex_t mutex;
int pos;
int is_left;
int is_write;

void fish_init() {
  // TODO
  pthread_cond_init(&cond,NULL);
  pthread_mutex_init(&mutex,NULL);
  pos=0;
  is_left = 1; 
  // is_left = rand() % 2; 
  is_write = 0;
}

void fish_before(char ch) {
  // TODO
  pthread_mutex_lock(&mutex);
  switch (ch) {
    case '<':
      while (!(   is_write==0   &&(( is_left==1 && (pos==0 || pos==2) )   ||  ( is_left==0 && pos==1 ))   )) {
        pthread_cond_wait(&cond,&mutex);
      }
      is_write=1;
      pos += 1;
      break;
    case '>':
      while (!  (is_write==0 && ((is_left==0 && (pos==0 || pos==2)) || (is_left==1 && pos==1)))) {
        pthread_cond_wait(&cond,&mutex);
      }
      is_write=1;
      pos += 1;
      break;
    case '_':
      while (!  (is_write==0 && pos==3)) {
        pthread_cond_wait(&cond,&mutex);
      }
      is_write=1;
      pos = 0;
      is_left = rand() % 2;
      break;
  }
  pthread_mutex_unlock(&mutex);
}

void fish_after(char ch) {
  // TODO
  pthread_mutex_lock(&mutex);
  is_write = 0;
  pthread_cond_broadcast(&cond);
  pthread_mutex_unlock(&mutex);
}

// static const char roles[] = "<<<<<>>>>___";
static const char roles[] = ">>><<_<_<<<_><<<<<>>___>_>__";

void fish_thread(int id) {
  char role = roles[id];
  while (1) {
    fish_before(role);
    putchar(role); // should not hold *any* mutex lock now
    fish_after(role);
  }
}

int main() {
  setbuf(stdout, NULL);
  fish_init();
  for (int i = 0; i < strlen(roles); i++)
    create(fish_thread);
  join(NULL);
}

