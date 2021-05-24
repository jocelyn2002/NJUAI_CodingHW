#include<iostream>
#include<cmath>
using namespace std;
struct Node{
    int t,c;
    bool red;
    Node *fa,*ls,*rs;
};
Node* make(Node* father,int time,int passenger){
    Node* z=new Node;
    z->red=true;
    z->t=time;
    z->c=passenger;
    z->fa=father;
    z->ls=NULL;
    z->rs=NULL;
    return z;
}
void query(Node* root,int time){
    while (root){
        if (root->t==time){
            cout<<root->c<<endl;
            return;
        }
        else if (root->t>time)
            root = root->ls;
        else
            root=root->rs;
    }
    // 找不到的时候
    cout<<0<<endl;
}
Node* insert(Node* rootroot,int time,int passenger){
    Node* ins = make(NULL,time,passenger);
    Node* root=rootroot;
    // 有根，按照BST方法插入,无根跳过
    while (root){
        if(abs(root->t-time)<=30)
            return rootroot;
        else if (root->t>time){
            if (root->ls)
                root = root->ls;
            else{
                ins->fa = root;
                root->ls = ins;
                break;
            }
        }
        else{
            if (root->rs)
                root=root->rs;
            else{
                ins->fa=root;
                root->rs=ins;
                break;
            }
        }
    }
    // 修复破坏的规则

    Doitagain:
    // 1.ins为根，涂黑返回
    if (ins->fa==NULL){
        ins->red=false;
        return ins;
    }
    // 2.ins有父亲
    // 2.1父亲节点为黑色，直接结束
    else if (ins->fa->red==false);
    // 2.2父亲红（说明有爷爷）
    // 2.2.1有红叔叔(因为父亲红，所以相等就行)
    else if (ins->fa->fa->ls&&ins->fa->fa->rs&&ins->fa->fa->ls->red==ins->fa->fa->rs->red){
        ins->fa->fa->ls->red=false;
        ins->fa->fa->rs->red=false;
        ins->fa->fa->red=true;
        ins=ins->fa->fa;
        goto Doitagain;
    }
    // 2.2.2黑叔叔或者没有叔叔
    else{
        bool father_left=false,self_left=false;
        Node *exgrandpa=ins->fa->fa;
        Node *exfather=ins->fa;
        if (exgrandpa->ls&&exgrandpa->ls==exfather) father_left=true;
        if (exfather->ls&&exfather->ls==ins) self_left=true;
        if (father_left)
            if (self_left){
                exgrandpa->red=true;
                exfather->red=false;

                exgrandpa->ls=exfather->rs;
                if (exfather->rs)
                    exfather->rs->fa=exgrandpa;
                exfather->fa=exgrandpa->fa;
                if (exgrandpa->fa)
                    exgrandpa->fa->ls=exfather;
                exfather->rs=exgrandpa;
                exgrandpa->fa=exfather;
            }
            else{
                exgrandpa->ls=ins;
                ins->fa=exgrandpa;
                exfather->rs=ins->ls;
                if (ins->ls)
                    ins->ls->fa=exfather;
                exfather->fa=ins;
                ins->ls=exfather;
                
                ins=exfather;
                goto Doitagain;
            }
        else{
            if (self_left){
                exgrandpa->rs=ins;
                ins->fa=exgrandpa;
                exfather->ls=ins->rs;
                if (ins->rs)
                    ins->rs->fa=exfather;
                exfather->fa=ins;
                ins->rs=exfather;

                ins=exfather;
                goto Doitagain;
            }
            else{
                exgrandpa->red=true;
                exfather->red=false;

                exgrandpa->rs=exfather->ls;
                if (exfather->ls)
                    exfather->ls->fa=exgrandpa;
                exfather->fa=exgrandpa->fa;
                if (exgrandpa->fa)
                    exgrandpa->fa->rs=exfather;
                exfather->ls=exgrandpa;
                exgrandpa->fa=exfather;

            }
        }
    }

    //返回真正的根
    while(rootroot->fa)
        rootroot=rootroot->fa;
    return rootroot;
}
Node* depart(Node* root){
    // 1.空
    if (!root){
        cout<<0<<endl;
        return NULL;
    }
    // 2.有根
    // 2.1根没有左孩子
    if (!root->ls){
        Node* temp=root->rs;
        cout<<root->c<<endl;
        delete root;
        if (temp)
            temp->fa=NULL;
        return temp;
    }
    // 2.2根有左孩子
    Node* y = root;
    while (y->ls){
        y = y->ls;
    } 

    // y是删除的节点，x是他的右子树
    cout<<y->c<<endl;

    y->fa->ls=y->rs;
    Node* x=y->rs;
    Node* xfa = y->fa;
    if (x)
        x->fa=y->fa;
    
    // 1.y红
    if (y->red==true){
        
        delete y;
        return root;
    }
    // 2.y黑x红，把x涂黑
    if (y->red==false&&x!=NULL&&(x->red==true)){
        x->red=false;
        delete y;
        goto endgame;
    }
    delete y;
    // 3.y黑，x黑（此时只可能是空）  x表示双黑节点,一下过程为双黑节点处理法
    
dag:
    // 处理特殊情况或定义上述几个量
    
    if (xfa->rs->red){
        xfa->red=true;
        xfa->rs->red=false;
        
        xfa->rs->fa=xfa->fa;
        if (xfa->fa)
            xfa->fa->ls=x->rs;

        xfa->fa=xfa->rs;
        xfa->rs=xfa->rs->ls;
        xfa->rs->fa=xfa;
        xfa->fa->ls=xfa;
        goto dag;
    }
    // 兄弟有两个黑儿子
    else if ((xfa->rs->ls==NULL||xfa->rs->ls->red==false)
    &&(xfa->rs->rs==NULL||xfa->rs->rs->red==false)){
        x=xfa;
        x->rs->red=true;
        // 黑红变黑
        if (x->red){
            x->red=false;
            goto endgame;
        }
        // 黑黑推到根了
        else if (x->fa==NULL) return x;
        else{
            xfa = x->fa;
            goto dag;
        }

    }
    // 兄弟的儿子左红右黑
    else if ((xfa->rs->rs==NULL||xfa->rs->rs->red==false)
    &&(xfa->rs->ls->red)){
        Node *D=xfa->rs;
        Node *C=xfa->rs->ls;
        C->red=false;
        D->red=true;
        C->fa=xfa;
        xfa->rs=C;
        D->ls=C->rs;
        if (D->ls)
            D->ls->fa=D;
        D->fa=C;
        C->rs=D;
        goto dag;
    }
    // 兄弟儿子左黑又红
    else{
        xfa->rs->rs->red=false;
        Node *D=xfa->rs;
        D->red=xfa->red;
        xfa->red=false;
        xfa->rs=D->ls;
        if(xfa->rs)
            xfa->rs->fa=xfa;
        D->fa=xfa->fa;
        if(D->fa)
            D->fa->ls=D;
        D->ls=xfa;
        xfa->fa=D;
        goto endgame;
    }
    
endgame:
    while(root->fa)
        root=root->fa;
    return root;
}


int main(){
    Node *root = NULL;
    int num_of_operations;
    cin >> num_of_operations;
    for (;num_of_operations>0;num_of_operations--){
        int op;
        cin >> op;
        switch (op){
            case 0:{
                int b,c;
                cin >> b >> c;
                root=insert(root,b,c);
                break;
            }
            case 1:{
                root=depart(root);
                break;
            }
            case 2:{
                int b;
                cin >> b;
                query(root,b);
                break;
            }
            default:;            
        }
    }
    return 0;
}