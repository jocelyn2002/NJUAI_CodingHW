#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <dlfcn.h>
#include <fcntl.h>
#include <sys/wait.h>
#include <assert.h>

#define LINE_LENGTH 4096

void mkoutputname(char output_name[],char source_name[]) {
  strcpy(output_name,source_name);
  output_name[strlen(source_name)] = '.';
  output_name[strlen(source_name)+1] = 's';
  output_name[strlen(source_name)+2] = 'o';
  output_name[strlen(source_name)+3] = '\0';
}
int call_gcc(char source_name[],char *envp[]) {
  char output_name[128];
  mkoutputname(output_name,source_name);
  
  int pid = fork(); // 0子进程
  
  if (pid == 0) {
    int nfile = open("/dev/null",O_RDWR);
    dup2(nfile,fileno(stderr));
    dup2(nfile,fileno(stdout));
    
    // 调用gcc
    char *exec_argv[10];
    exec_argv[0] = "gcc";
#ifdef __x86_64__
    // printf("-m64\n");
    exec_argv[1] = "-m64";
#else
    // printf("-m32\n");
    exec_argv[1] = "-m32";
#endif
    exec_argv[2] = "-x";
    exec_argv[3] = "c";
    exec_argv[4] = source_name;
    exec_argv[5] = "-shared";
    exec_argv[6] = "-fPIC";
    exec_argv[7] = "-o";
    // printf("%s\n",output_name);
    exec_argv[8] = output_name;
    exec_argv[9] = NULL;

    char PATH[1024];
    memset(PATH,0,sizeof(PATH));
    for (int i=0;envp[i]!=NULL;i++) {
      char temp[5];
      temp[4]='\0';
      strncpy(temp,envp[i],4);
      if (strcmp(temp,"PATH")==0) {
        strcpy(PATH,(char*)&envp[i][5]);
        break;
      }
    }
    
    int j=0;
    char filename[256];
    memset(filename,0,sizeof(filename));
    for (int i=0;i<strlen(PATH);i++) {
      filename[j]=PATH[i];
      j++;
      if (filename[j-1]==':'){

        filename[j-1]='\0';
        strcat(filename,"/gcc");
        execve(filename, exec_argv, envp);
        
        j=0;
        memset(filename,0,sizeof(filename));
      }
    }
    strcat(filename,"/gcc");
    execve(filename, exec_argv, envp);
    
    assert(0);
    return 0;
  }
  else {
    int status;
    assert(wait(&status) == pid);
    if (!access(output_name,0))
      return 1;
    else
      return 0;
  }
}

int main(int argc, char *argv[], char *envp[]) {
  static char line[LINE_LENGTH];
  while (1) {
    printf("crepl> ");
    fflush(stdout);
    if (!fgets(line, sizeof(line), stdin)) {
      break;
    }
    // printf("Got %zu chars.\n", strlen(line)); // WTF?
    
    // 如果是定义函数
    if (line[0]=='i'&&line[1]=='n'&&line[2]=='t') {
      char source_name[LINE_LENGTH]="/tmp/dinghao12601.XXXXXX";
      mkstemp(source_name);
      FILE* file = fopen(source_name,"w");
      // assert(file!=NULL);
      fputs(line,file);
      fclose(file);

      if (call_gcc(source_name,envp)==1){
        char output_name[128];
        mkoutputname(output_name,source_name);
        
        
        void* handle = dlopen(output_name, RTLD_GLOBAL | RTLD_NOW);
        assert(handle!=NULL);
        printf("OK\n");
      }  
      else printf("gcc error\n");
    }
    // 如果是表达式
    else {
      char source_name[LINE_LENGTH]="/tmp/dinghao12601.XXXXXX";
      mkstemp(source_name);

      char newline[LINE_LENGTH];
      memset(newline,0,sizeof(newline));
      strcpy(newline,"int wrapper(){return ");
      strcat(newline,line);
      strcat(newline,";}");

      FILE* file = fopen(source_name,"w");
      // assert(file!=NULL);
      fputs(newline,file);
      fclose(file);

      if (call_gcc(source_name,envp)==1){
        char output_name[128];
        mkoutputname(output_name,source_name);
        
        void* handle = dlopen(output_name,RTLD_GLOBAL | RTLD_NOW);
        // assert(handle!=NULL);
        int (*func)() = dlsym(handle,"wrapper");
        // assert(func!=NULL);
        printf("%d\n",func());
        dlclose(handle);
      }
      else      
        printf("operation gcc error\n");

    }
  }
}
