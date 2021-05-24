#include<iostream>
#include<cmath>
#include<stdlib.h>
#include<time.h>
using namespace std;

int main(){
	int times=10000000;
	for (int j=100;j>0;j*=10){
		srand((unsigned)time(0));
		int sums = 0;
		for (int i=0;i<j;i++){
			float a=(rand()%10000)/10000.0;
			float b=(rand()%10000)/10000.0;
			float c=(rand()%10000)/10000.0;
			float d=(rand()%10000)/10000.0;
			if (pow(a,2)+sin(b)+a*exp(c)<=d) sums+=1;
		}
		printf("%d  %f\n",j,float(sums)/float(j));	 	
	}
}
