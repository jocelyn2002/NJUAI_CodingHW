#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <assert.h>
#include <string.h>

// this should be enough
static char buf[60000];
uint32_t choose(uint32_t n){
	return rand()%n;
}
typedef struct node{
	char c[10];
	struct node* prev;
	struct node* next;
}Node;
void gen(char act,Node* prev_node,Node* next_node) {
	switch (act) {
		//完整元过程
		case '0': { 
			switch (choose(3)) {
				case 0: gen('p',prev_node,next_node);break;
			//	case 1: gen('p',prev_node,next_node);break;
		//		default: gen('o',prev_node,next_node);break;
			}
			break;
		}
		//生成数字
		case 'n' :{
			int a = rand()%1000;
			char co[10];
			sprintf(co,"%d",a);
			Node ppp;
			Node *ss = &ppp;
			strcpy(ss->c,co);
			prev_node->next=ss;
			next_node->prev=ss;
			ss->prev=prev_node;
			ss->next=next_node;
			break;
		}
		//生成括号括起来的表达式
		case 'p': {
			Node ppp;
			Node *pp = &ppp;
			prev_node->next=pp;
			pp->prev=prev_node;
			strcpy(pp->c,"(");
			Node qqq;
			Node *nn = &qqq;
			next_node->prev=nn;
			nn->next=next_node;
			strcpy(nn->c,")");
			gen(0,pp,nn);
			break;
		 }
		//生成中间又个+-*/的表达式
		case 'o': {
			Node ooo;
			Node *op = &ooo;
			switch (choose(4)) {
				case 0:strcpy(op->c,"+");break;
				case 1:strcpy(op->c,"-");break;
				case 2:strcpy(op->c,"*");break;
				case 3:strcpy(op->c,"/");break;
			}
			gen('p',prev_node,op);
			gen('p',op,next_node);	
			break;
		}
		break;
	}
}
static inline void gen_rand_expr() {
	buf[0] = '1';
	buf[1] = '\0';	
	Node sss;
	Node* sb = &sss;
	sb->next=sb;
	sb->prev=sb;
	
	gen(0,sb,sb);
	Node *i;
	for (i=sb->next;i!=sb;i=i->next){
	//	strcat(buf,i->c);
		printf(i->c);
	}
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
  for (i = 0; i < loop; i ++) {
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
