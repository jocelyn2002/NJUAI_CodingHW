#include<iostream>
using namespace std;
void merge(long long *num,int *result,int *L,int mi_L,int *R,int mi_R){
    int l=0,r=0,i=0;
    while((l<=mi_L) || (r<=mi_R)){
        if (l>mi_L)
            result[i++]=R[r++];
        else if (r>mi_R)
            result[i++]=L[l++];
        else{
            if (L[l]<=R[r])
                result[i++]=L[l++];
            else{
                result[i++]=R[r++];
                *num += mi_L-(l-1);2
            }
        }
    }
}
void merge_sort(long long *num,int *A,int mi_A){
    if (mi_A==0) return;
    int l=(mi_A+1)/2; // 左长度
    int r=mi_A+1-l; // 右长度
    int *L= new int[l];
    int *R= new int[r];
    for (int i=0;i<=l-1;i++)
        L[i]=A[i];
    for (int i=l;i<=mi_A;i++)
        R[i-l]=A[i];
    merge_sort(num,L,l-1);
    merge_sort(num,R,r-1);
    // long long a = *num;
    merge(num,A,L,l-1,R,r-1);
    // cout<<endl<<*num-a<<endl;
    delete [] L;
    delete [] R;
}



int main(){
    // 输入部分
    int length;
    cin >> length;
    int *up=new int[length];
    int *down=new int[length];
    int *shifter=new int[length];
    for (int i=0;i<length;i++)
        cin >> up[i];
    for (int i=0;i<length;i++)
        cin >> down[i];

    // 将down数组转化为标准逆序数形式
    for (int i=0;i<length;i++)
        shifter[up[i]]=i;
    for (int i=0;i<length;i++)
        down[i]=shifter[down[i]];
    // for (int i=0;i<length;i++)
    //     cout<<down[i]<<" ";
    // cout<<endl;
    long long a=0;
    long long *num = &a;
    merge_sort(num,down,length-1);

    cout<<a;
}