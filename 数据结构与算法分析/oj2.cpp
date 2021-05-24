#include<iostream>
using namespace std;

struct Node {
	char c;
	Node *next;
	Node *prev;
};


void app(int l, int s, char x, Node *editor[]) {
	if (s==0) {
		Node *node = new Node;
		node->c=x;
		node->next=editor[l]->next;
		editor[l]->next->prev=node;
		editor[l]->next=node;
		node->prev=editor[l];
	} else if (s==1) {
		Node *node = new Node;
		node->c=x;
		node->prev=editor[l]->prev;
		editor[l]->prev->next=node;
		editor[l]->prev=node;
		node->next=editor[l];
	}
}
void del(int l, int s, Node *sb, Node *editor[]) {
	char x='#';
	if (editor[l]->next != editor[l]) {
		if (s==1) {
			x=editor[l]->prev->c;
			editor[l]->prev=editor[l]->prev->prev;
			delete editor[l]->prev->next;
			editor[l]->prev->next=editor[l];
		} else if (s==0) {
			x=editor[l]->next->c;
			editor[l]->next=editor[l]->next->next;
			delete editor[l]->next->prev;
			editor[l]->next->prev = editor[l];
		}
	}


	Node *p = new Node;
	p->c=x;
	p->prev = sb->prev;
	sb->prev->next = p;
	p->next=sb;
	sb->prev=p;
}
void que(int l, int s, Node *sb, Node *editor[]) {
	char x;
	if (s==0)
		x = editor[l]->next->c;
	else if (s==1)
		x = editor[l]->prev->c;


	Node *p = new Node;
	p->c=x;
	p->prev = sb->prev;
	sb->prev->next = p;
	p->next=sb;
	sb->prev=p;
}

int main() {
	Node *editor[100];
	for (int i=0; i<100; i++) {
		Node *ss=new Node;
		editor[i]=ss;
		editor[i]->next = editor[i];
		editor[i]->prev = editor[i];
		editor[i]->c = '#';
	}

	int times;
	cin >> times;
//	cout << times;  get:1000000

	Node *sb = new Node;
	sb->next=sb;
	sb->prev=sb;
	sb->c='#'; // will never be used

	for (int time=0; time<times; time++) {
		int l,s,op;
		cin >> l>>s>>op;
		if (op==0) {
			char x;
			cin>>x;
			app(l,s,x,editor);
		}
		else if (op==1) del(l,s,sb,editor);
		else if (op==2) que(l,s,sb,editor);
	}
	for (Node *head=sb; head->next->next!=sb; head=head->next)
		cout << head->next->c << endl;
	cout <<sb->prev->c;
	
	return 0;
}
