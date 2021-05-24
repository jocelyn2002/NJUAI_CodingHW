#include <stdio.h>
#include <getopt.h>
#include <stdlib.h>
#include "multimod.h"

static struct option long_option[] = {
  { "i", required_argument, NULL, 'i' },
  { NULL, 0, NULL, '\0'},
};

multimod_t multimod_tab[] = {
  multimod_p1,
  multimod_p2,
  multimod_p3,
};

int main(int argc, char *argv[]) {
  int64_t a = 0, b = 0, m = 1;
  multimod_t func = NULL;

  while (1) {
    int idx;
    int c = getopt_long(argc, argv, "i:", long_option, &idx);
    if (c == -1) {
      break;
    } if (c == 'i') {
      int i = atoi(optarg);
      if (1 <= i && i <= LENGTH(multimod_tab)) {
        func = multimod_tab[i - 1];
      }
    }
  }

  if (!func) {
    fprintf(stderr, "Usage: lab1 -i 1|2|3 a b m\n");
    exit(1);
  }

  a = strtoll(argv[optind], NULL, 10);
  b = strtoll(argv[optind + 1], NULL, 10);
  m = strtoll(argv[optind + 2], NULL, 10);

  int64_t ret = func(a, b, m);
  printf("%ld\n", ret);
}