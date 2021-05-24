#include <iostream>
using namespace std;
int main()
{
	int num_of_add;
	cin >> num_of_add;
	int answer[100000];
	for (int i =0;i<num_of_add;i++)
	{
		int a,b;
		cin>>a>>b;
		answer[i]=a+b;
		}	
	for (int i=0;i<num_of_add-1;i++)
	{
		cout << answer[i] <<endl;
	}
	cout << answer[num_of_add-1];
}

