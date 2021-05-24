// 头文件与需要使用的函数申明
#include "monitor/monitor.h"
#include "monitor/expr.h"
#include "monitor/watchpoint.h"
#include "nemu.h"
#include <stdlib.h>
#include <readline/readline.h>
#include <readline/history.h>
uint32_t vaddr_read(vaddr_t, int);
void isa_reg_display();
bool make_token(char*);
uint32_t expr(char*,bool*);
uint32_t isa_reg_str2val(const char *s,bool *success);
int new_wp(char *expression);
void free_wp(int n_watch);
void cpu_exec(uint64_t);
void show_wp();

static char* rl_gets() {
  static char *line_read = NULL;

   if (line_read) {
    free(line_read);
    line_read = NULL;
  }

  line_read = readline("(nemu) ");

   if (line_read && *line_read) {
    add_history(line_read);
  }

  return line_read;
}/* We use the `readline' library to provide more flexibility to read from stdin. */


// nemu简化版gdb指令
static int cmd_c(char *args) {
  cpu_exec(-1);
  return 0;
} // 继续执行到底
static int cmd_q(char *args) {
  return -1;
} // 退出
static int cmd_help(char *args);
  // 指令帮助, 由于需要用到table，这里只做申明
static int cmd_si(char *args) {
  // extract the first argument
  char *arg = strtok(NULL, " ");
  int i;
  // when arg is "a" int
  if (arg && (sscanf( arg, "%d" , &i) == 1) && (i>=1))
    cpu_exec(i);
  // all the other conditions
  else
    printf("Invalid argument\n");
  return 0;
} // 单步执行
static int cmd_info(char *args) {
	char *arg = strtok(NULL, " ");
	if (arg) {
		if (*arg == 'r') {
			isa_reg_display();
			return 0;
	 	}
		if (*arg == 'w') {
      show_wp();
			return 0;
	 	}
	}
	printf("Invalid argument\n");
	return 0;
} // 寄存器或监视点信息
static int cmd_x(char *args) {
	char *arg = strtok(NULL, " ");
	int N,i;
	uint32_t a;
	if (arg && (sscanf(arg, "%d", &N) == 1) && (N>=1)) {
		arg = strtok(NULL, " ");
		if (arg) {
      bool bb=false;
      bool *aa=&bb;
      a = expr(arg,aa);
			for (i=0;i<N;i++)
				printf("%#x : %#x\n",a+4*i,vaddr_read(a+4*i, 4));
			return 0;
		}
	}
	printf("Invalid argument\n");
	return 0;
} // 扫描内存
static int cmd_p(char *args) {
  bool bb=false;
  bool *aa=&bb;
	if (strcmp(args,"file")==0){
		FILE *fp = fopen("/home/onstantine/ics2019/nemu/tools/gen-expr/input","r");
		assert(fp!=NULL);
		while (!feof(fp)){
			char Line[1024];
			char *ttt = fgets(Line,1024,fp);
      assert(ttt);
			Line[strlen(Line)-1]=' ';
			char *valu = strtok(Line, " ");
			char *expression = strtok(NULL, " ");
			uint32_t value;
			sscanf(valu,"%d",&value);
			//printf("ok1\n");
			uint32_t value_exp = expr(expression,aa);
			//printf("ok2\n");
			printf("%d   %d\n",value,value_exp);
		}
		fclose(fp);
	}
  else printf("%d\n",expr(args,aa));
  return 0;
} // 表达式求值
static int cmd_w(char *args) {
	char *arg = strtok(NULL, " ");
  printf("Set watchpoint %d\n",new_wp(arg));
  return 0;
} // 添加监视点
static int cmd_d(char *args) {
  char *arg = strtok(NULL, " ");
  int n;
  sscanf(arg,"%d",&n);
  free_wp(n);
  return 0;
} // 删除第n号监视点


// 指令表
static struct {
  char *name;
  char *description;
  int (*handler) (char *);
} cmd_table [] = {
  // nemu成品机要用的方法 
  { "help", "Display informations about all supported commands", cmd_help },
  { "c", "Continue the execution of the program", cmd_c },
  { "q", "Exit NEMU", cmd_q },
  { "si", "Execute singly for N steps", cmd_si },
  { "info", "Display informations about reg or window", cmd_info },
  { "x", "Show memory conditions, x N EXPR", cmd_x},
  { "p", "Evaluate an expression", cmd_p},
  { "w", "set a watchpoint, whenever it changes suspand nemu", cmd_w},
  { "d", "delete the wathpoint number N", cmd_d},
};


#define NR_CMD (sizeof(cmd_table) / sizeof(cmd_table[0]))
static int cmd_help(char *args) {
  /* extract the first argument */
  char *arg = strtok(NULL, " ");
  int i;

  if (arg == NULL) {
    /* no argument given */
    for (i = 0; i < NR_CMD; i ++) {
      printf("%s - %s\n", cmd_table[i].name, cmd_table[i].description);
    }
  }
  else {
    for (i = 0; i < NR_CMD; i ++) {
      if (strcmp(arg, cmd_table[i].name) == 0) {
        printf("%s - %s\n", cmd_table[i].name, cmd_table[i].description);
        return 0;
      }
    }
    printf("Unknown command '%s'\n", arg);
  }
  return 0;
} // help指令的实现


void ui_mainloop(int is_batch_mode) {
  if (is_batch_mode) {
    cmd_c(NULL);
    return;
  } // batch_mode直接执行

  for (char *str; (str = rl_gets()) != NULL; ) {
    char *str_end = str + strlen(str);

    /* extract the first token as the command */
    char *cmd = strtok(str, " ");
    if (cmd == NULL) { continue; }

    /* treat the remaining string as the arguments,
     * which may need further parsing
     */
    char *args = cmd + strlen(cmd) + 1;
    if (args >= str_end) {
      args = NULL;
    }

#ifdef HAS_IOE
    extern void sdl_clear_event_queue(void);
    sdl_clear_event_queue();
#endif

    int i;
    for (i = 0; i < NR_CMD; i ++) {
      if (strcmp(cmd, cmd_table[i].name) == 0) {
        if (cmd_table[i].handler(args) < 0) { return; }
        break;
      }
    }

    if (i == NR_CMD) { printf("Unknown command '%s'\n", cmd); }
  }
}
