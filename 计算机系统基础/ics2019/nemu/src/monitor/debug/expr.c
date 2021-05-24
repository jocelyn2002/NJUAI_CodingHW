#include "nemu.h"
#include "DIY/expr.h"

/* We use the POSIX regex functions to process regular expressions.
 * Type 'man regex' for more information about POSIX regex functions.
 */
#include <sys/types.h>
#include <regex.h>

extern uint32_t vaddr_read(vaddr_t, int);
extern uint32_t isa_reg_str2val(const char *s,bool *success);

enum {
  TK_NOTYPE = 256,	// space
  TK_EQ,	//== equal 
  TK_VALUE_D,	//decimal value
  TK_VALUE_H,	//hexadecimal value
  TK_PR,	// pointer reference
  TK_AND,	// && and
  TK_OR,	// || or
  /* TODO: Add more token types */

};

static struct rule {
  char *regex;
  int token_type;
} rules[] = {
  /* TODO: Add more rules.	
   * Pay attention to the precedence level of different rules.
   * */
  // level0 无歧直接匹配义
  {" +", TK_NOTYPE},	// spaces
  {"==", TK_EQ},	// equal
  {"\\+", '+'}, // plus
  {"-", '-'},	// minus
  {"/", '/'},	// divide
  {"\\(", '('},	// left parenthesis
  {"\\)", ')'},	// rignt parenthesis
  {"\\$[abcdefghijklmnopqrstuvwxyz]+", '$'},	// get reg value
  {"\\*",'*'},	// multiply or pointer reference
  // level1 有歧义高优先级
  {"0x[0123456789abcdef]+", TK_VALUE_H}, // hexadecimal value
  // leval2 有歧义低优先级
  {"[0123456789]+", TK_VALUE_D},	// decimal value
};

#define NR_REGEX (sizeof(rules) / sizeof(rules[0]) )

static regex_t re[NR_REGEX] = {};

/* Rules are used for many times.
 * Therefore we compile them only once before any usage.
 */
void init_regex() {
  int i;
  char error_msg[128];
  int ret;

  for (i = 0; i < NR_REGEX; i ++) {
    ret = regcomp(&re[i], rules[i].regex, REG_EXTENDED);
    if (ret != 0) {
      regerror(ret, &re[i], error_msg, 128);
      panic("regex compilation failed: %s\n%s", error_msg, rules[i].regex);
    }
  }
}


static Token tokens[200] __attribute__((used)) = {}; //暂定200，出问题再说
static int nr_token __attribute__((used))  = 0;

static bool make_token(char *e) {
  int position = 0;
  int i;
  regmatch_t pmatch;

  nr_token = 0;

  while (e[position] != '\0') {
    /* Try all rules one by one. */
    for (i = 0; i < NR_REGEX; i ++) {
      if (regexec(&re[i], e + position, 1, &pmatch, 0) == 0 && pmatch.rm_so == 0) {
        char *substr_start = e + position;
        int substr_len = pmatch.rm_eo;
        // Log("match rules[%d] = \"%s\" at position %d with len %d: %.*s",
        //     i, rules[i].regex, position, substr_len, substr_len, substr_start);
        position += substr_len;
        /* TODO: Now a new token is recognized with rules[i]. Add codes
         * to record the token in the array `tokens'. For certain types
         * of tokens, some extra actions should be performed.
         */
        switch (rules[i].token_type) {
          case TK_NOTYPE: nr_token-=1;//为了平衡每次循环的增量
                          break;

          case '+': tokens[nr_token].type='+';strcpy(tokens[nr_token].str,"+");break;
          case '-': tokens[nr_token].type='-';strcpy(tokens[nr_token].str,"-");break;
          case '/': tokens[nr_token].type='/';strcpy(tokens[nr_token].str,"/");break;
          case '(': tokens[nr_token].type='(';strcpy(tokens[nr_token].str,"(");break;
          case ')': tokens[nr_token].type=')';strcpy(tokens[nr_token].str,")");break;
          
          case '*':
            if ((nr_token==0)||(tokens[nr_token-1].type=='(')||
            (tokens[nr_token-1].type=='+')||(tokens[nr_token-1].type=='-')||
            (tokens[nr_token-1].type=='*')||(tokens[nr_token-1].type=='/')){
              tokens[nr_token].type=TK_PR;
              strncpy(tokens[nr_token].str,substr_start,substr_len);
            }
            else {
              tokens[nr_token].type='*';
              strcpy(tokens[nr_token].str,"*");
            }
            break;
          
          case TK_VALUE_D:
            tokens[nr_token].type=TK_VALUE_D;
            strncpy(tokens[nr_token].str,substr_start,substr_len);
            break;

          case TK_VALUE_H:
            tokens[nr_token].type=TK_VALUE_H;
            strncpy(tokens[nr_token].str,substr_start,substr_len);
            break;
          
          case '$':
            tokens[nr_token].type='$';
            strncpy(tokens[nr_token].str,substr_start+1,substr_len-1);
            break;

          case TK_EQ:
            tokens[nr_token].type=TK_EQ;
            strcpy(tokens[nr_token].str,"==");
            break;
          
          default: TODO();
        }
        nr_token+=1;   
        // 此处还需添加越界情况
        break;
      }
    }

    if (i == NR_REGEX) {
      printf("no match at position %d\n%s\n%*.s^\n", position, e, position, "");
      return false;
    }
  }
  return true;
}

uint32_t token_get_value(int start_index, int end_index) {
  // 首先 脱去最外层括号
	if ((tokens[start_index].type=='(')&&(tokens[end_index].type==')'))
		return token_get_value(start_index+1,end_index-1);
  // 其次 单项情况
	if (start_index==end_index) {
    // 十进制 数字
    if (tokens[start_index].type==TK_VALUE_D){
      uint32_t a;
      sscanf(tokens[start_index].str,"%d",&a);
      return a;
    }
    // 十六进制 数字
      if (tokens[start_index].type==TK_VALUE_H){
        uint32_t a;
        sscanf(tokens[start_index].str,"%x",&a);
        return a;
      }
    // 检查是否为获取寄存器的值
	  if (tokens[start_index].type=='$'){
      // printf("%s\n",tokens[start_index].str);
      bool bbb=false;
      bool *reg_success=&bbb;
      char ss[10]="\0";
      strcpy(ss,tokens[start_index].str);
		  uint32_t reg_value = isa_reg_str2val(ss,reg_success);
      assert(*reg_success != false);
      return (int)reg_value;
    }
	}
  // 再次 多项情况
  else{
    // 主运算符为 + -
    int num_of_pare = 0;
    for (int i=end_index;i>=start_index;i--) {
      if (tokens[i].type == ')') num_of_pare += 1;
      else if (tokens[i].type == '(') num_of_pare -= 1;
      else if ((tokens[i].type == '+')&&(num_of_pare==0))
        return (token_get_value(start_index,i-1) + token_get_value(i+1,end_index));
      else if ((tokens[i].type == '-')&&(num_of_pare==0))
        return (token_get_value(start_index,i-1) - token_get_value(i+1,end_index));
    }
    // 主运算符为 * /
    num_of_pare = 0;
    for (int i=end_index;i>=start_index;i--) {
          if (tokens[i].type == ')') num_of_pare += 1;
          else if (tokens[i].type == '(') num_of_pare -= 1;
          else if ((tokens[i].type == '*')&&(num_of_pare==0))
            return (token_get_value(start_index,i-1) * token_get_value(i+1,end_index));
          else if ((tokens[i].type == '/')&&(num_of_pare==0))
            return (token_get_value(start_index,i-1) / token_get_value(i+1,end_index));
    }
    // 主运算符为逻辑运算符
    num_of_pare = 0;
    for (int i=end_index;i>=start_index;i--) {
          if (tokens[i].type == ')') num_of_pare += 1;
          else if (tokens[i].type == '(') num_of_pare -= 1;
          else if ((tokens[i].type == TK_EQ)&&(num_of_pare==0))
            return (token_get_value(start_index,i-1)==token_get_value(i+1,end_index));
    }
    // 检查是否为指针解引用
    if ((tokens[start_index].type==TK_PR)&&
        (tokens[start_index+1].type='(')&&
        (tokens[end_index].type=')')){
        uint32_t location = token_get_value(start_index+2,end_index-1);
        return (uint32_t)vaddr_read(location,1);
      }
    }
  
	return 0;
}

uint32_t expr(char *e, bool *success) {
  if (!make_token(e)) {
    *success = false;
    printf("你妈！\n");
    return 0;
  }
  
  *success = true;
  return token_get_value(0,nr_token-1);
}