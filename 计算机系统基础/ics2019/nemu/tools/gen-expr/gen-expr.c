#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <assert.h>
#include <string.h>

// this should be enough
static char buf[65436]; //减了100暂时解除了warning，有待后续研究

uint32_t choose(uint32_t n){
	return rand()%n;
}
extern void gen();
void gen_num(){
	char a[10];
	sprintf(a,"%d",choose(100));
	strcat(buf,a);
}
void gen_pare(){
	strcat(buf,"(");
	gen();
	strcat(buf,")");
}
void gen_op(){
	gen();
	//因为可能不整除，以及存在除以0情况，暂时无法用与检验
	switch (choose(4)){
		case 0:strcat(buf,"+");break;
		case 1:strcat(buf,"-");break;
		case 2:strcat(buf,"*");break;
		default:strcat(buf,"/");break;
	} 
	gen();
}

void gen() {
	switch (choose(3)){
		case 0:gen_op();break;
		case 1:gen_pare();break;
		default: gen_num();break;
	}
}

static inline void gen_rand_expr() {
	buf[0] = '\0';	
	gen();
}

static char code_buf[65536];
static char *code_format =
"#include <stdio.h>\n"
"int main() { "
"  unsigned result = %s; "
"  printf(\"%%u\", result); "
"  return 0; "
"}";

int main(int argc, char *argv[]) {
  int seed = time(0);
  srand(seed);
  int loop = 1;
  if (argc > 1) {
    sscanf(argv[1], "%d", &loop);
  }
  int i;
  for ( i = 0; i < loop; i ++) {
    gen_rand_expr();

    sprintf(code_buf, code_format, buf);

    FILE *fp = fopen("/tmp/.code.c", "w");
    assert(fp != NULL);
    fputs(code_buf, fp);
    fclose(fp);

    int ret = system("gcc /tmp/.code.c -o /tmp/.expr");
    if (ret != 0) continue;

    fp = popen("/tmp/.expr", "r");
    assert(fp != NULL);

    int result;
    fscanf(fp, "%d", &result);
    pclose(fp);

    printf("%u %s\n", result, buf);
  }
  return 0;
}
