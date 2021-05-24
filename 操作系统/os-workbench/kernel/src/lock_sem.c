#include "../include/common.h"

void kmt_spin_init(spinlock_t *lk, const char *name){
    lk->lock = 0;
    lk->name = name;
}
void kmt_spin_lock(spinlock_t *lk) {
    int intr_on = _intr_read();

     // 关中断
    _intr_write(0);

    if (my_cpu.hold_locks == 0)
        my_cpu.intr_on = intr_on;
    my_cpu.hold_locks++;
    
    while(_atomic_xchg(&lk->lock,1));
}
void kmt_spin_unlock(spinlock_t *lk) {
    _atomic_xchg(&lk->lock, 0);
    
    my_cpu.hold_locks--;
    dassert(my_cpu.hold_locks>=0);
    dassert(_intr_read()==0);
    // 恢复中断
    if (my_cpu.hold_locks == 0 && my_cpu.intr_on)
        _intr_write(1);
}


void kmt_sem_init(sem_t *sem, const char *name, int value) {
    sem->name = name;
    sem->value = value;
    kmt->spin_init(&sem->lk,name);
}
void kmt_sem_wait(sem_t *sem) {
    while (1) {
        kmt->spin_lock(&sem->lk);
        if (sem->value > 0) {
            sem->value--;
            kmt->spin_unlock(&sem->lk);
            return;
        }
        else {
            kmt->spin_unlock(&sem->lk);
            _yield();
        }
    }
}
void kmt_sem_signal(sem_t *sem) {
    kmt->spin_lock(&sem->lk);
    sem->value++;
    kmt->spin_unlock(&sem->lk);
}
