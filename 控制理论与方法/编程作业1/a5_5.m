L=tf(25,[1,5,0]);
sys=feedback(L,1,-1);
t=[0:0.001:3];
y = step(sys,t);
plot(t,y),grid

p=find(y==max(y));
Tp=t(p)
Mpt=(y(p)-1)/1
text(t(p),y(p),'o','color','red')
text(t(p),y(p),['     (',num2str(t(p)),',',num2str(y(p)),')'],'color','b')

p=find(abs(t-1.62)<1e-4);
text(t(p),y(p),'o','color','red')
text(t(p),y(p),['     (',num2str(t(p)),',',num2str(y(p)),')'],'color','b')