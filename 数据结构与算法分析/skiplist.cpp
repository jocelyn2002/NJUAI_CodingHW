#include<iostream>
#include<cstdlib>
using namespace std;


struct Node{
    int t,c;
    Node *right,*down;
};
inline Node* make_node(int time,int passengers){
    Node *s = new Node;
    s->t = time;
    s->c = passengers;
    return s;
}

// 全局变量定义
#define big_number 1000
#define maxint 1147483647
#define minint -1147483647

Node *left_sentinals[big_number];
Node *right_single_sentinal;
int max_height = 0;
int historical_max_height = 0;



inline void init(){
    Node* l = make_node(minint,0);
    l->down=NULL;
    Node* r = make_node(maxint,0);
    r->down=NULL;
    l->right = r;
    left_sentinals[max_height] = l;
    right_single_sentinal=r;
}
inline void upgrade(){
    Node* l = make_node(minint,0);
    l->down = left_sentinals[historical_max_height];
    l->right = right_single_sentinal;
    max_height++;
    historical_max_height++;
    left_sentinals[max_height] = l;
}


int query(int time){
    Node *temp = left_sentinals[max_height];
    while (temp){
        if (temp->t==time) return temp->c;  // 找到了
        if (temp->right->t <= time)         // 右边的还小，右移
            temp = temp->right;             // 右边的比time大，往下移
        else
            temp = temp->down; 
    }
    return 0;//执行到这里说明没找到

}
void insert(int time,int passengers){
    Node *addlist[big_number];
    Node *temp = left_sentinals[max_height];
    int height = max_height;
    // 一次失败的查找，把要插入元素每一个高度左边一个节点存在addlist当中
    while (height>=0){
        if (temp->t==time) return;  // 找到了
        if (temp->right->t <= time){
            temp = temp->right;
        }
        else{
            addlist[height] = temp;
            height -= 1;
            temp = temp->down; 
        }
    } // 此时的temp已经是null,height是-1

    // 30分钟之内有航班，直接不插
    if ((time-addlist[0]->t<=30)||(addlist[0]->right->t-time<=30))
        return;

    // 从底层开始向上插
    bool do_it_again = true;
    Node *lower_alpha = NULL;
    height = 0;
    while (do_it_again){
        // 如果超过当前最大，升一级
        if (height>max_height){
            if (height<=historical_max_height){
                addlist[height] = left_sentinals[height];
                max_height++;
            }
            else{
                upgrade();
                addlist[height] = left_sentinals[height];
            }
        }
        Node *alpha = make_node(time,passengers);
        alpha -> right = addlist[height]->right;
        addlist[height]->right = alpha;
        alpha->down = lower_alpha;
        lower_alpha = alpha;
        height++;

        // 二分之一概率再向上插入一层
        do_it_again = rand() % 2;
    }
}
int depart(){
    // 没有航班，直接返回
    if (left_sentinals[0]->right==right_single_sentinal)
        return 0;

    int depart_time = left_sentinals[0]->right->t;
    int return_value = left_sentinals[0]->right->c;
    int i;
    for (i=max_height;left_sentinals[i]->right->t!=depart_time;i--);

    Node *temp;
    while (i>=0){
        temp = left_sentinals[i]->right;
        left_sentinals[i]->right = left_sentinals[i]->right->right;
        delete temp;
        i--;
    }
    // 记得检查一下是否最高层空了
    while (max_height > 0 && left_sentinals[max_height]->right==right_single_sentinal){
        max_height-=1;
    }
    return return_value;
}

int main(){
    // 进行初始化
    init();
    int num_of_operations;
    scanf("%d",&num_of_operations);
    for (;num_of_operations>0;num_of_operations--){
        int op;
        scanf("%d",&op);
        switch (op){
            case 0:{
                int b,c;
                scanf("%d %d",&b,&c);
                insert(b,c);
                break;
            }
            case 1:{
                printf("%d\n",depart());
                break;
            }
            case 2:{
                int b;
                scanf("%d",&b);
                printf("%d\n",query(b));
                break;
            }          
        }
    }
    return 0;
}