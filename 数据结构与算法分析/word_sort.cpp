#include<stdio.h>
#include<string.h>
using namespace std;
int main(){
    int i,j,n;
    char p[21][10];
    char temp[10];
    i=0;
    do{
        scanf("%s",&p[i]); // scanf以换行符结尾，在写\n就要输入两次换行
        i++;
    }while(strcmp(p[i-1],"#")!=0); // i已经++了，相判断刚才输入的结果要-1

    n=i-1; // 不然会把最后一个#算进去

    // 换个in-place排序算法
    for (i=0;i<n;i++){
        for (j=i+1;j<n;j++){
            if(strlen(p[i])>strlen(p[j])){
                strcpy(temp,p[i]);
                strcpy(p[i],p[j]);
                strcpy(p[j],temp);
            }
        }
    }
    
    for (i=0;i<n;i++){
        printf("%s ",p[i]);
    }
    
    return 0;
}

