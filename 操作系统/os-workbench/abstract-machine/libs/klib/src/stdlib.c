static unsigned long int next = 1;

// int atoi(const char* nptr);
int abs(int x) {
  return x>=0 ? x : -x;
}
// unsigned long time();
void srand(unsigned int seed) {
  next = seed;
}
int rand(void) {
  // RAND_MAX assumed to be 32767
  next = next * 1103515245 + 12345;
  return (unsigned int)(next/65536) % 32768;
}