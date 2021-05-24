struct spinlock {
    intptr_t lock;
    const char * name;
};

void kmt_spin_init(spinlock_t *lk, const char *name);
void kmt_spin_lock(spinlock_t *lk);
void kmt_spin_unlock(spinlock_t *lk);


struct semaphore {
    spinlock_t lk;
    int value;
    const char * name;
};

void kmt_sem_init(sem_t *sem, const char *name, int value);
void kmt_sem_wait(sem_t *sem);
void kmt_sem_signal(sem_t *sem);