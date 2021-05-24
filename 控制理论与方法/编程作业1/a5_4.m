sys1=tf(1,[1,2]);
sys2=tf(21,[1,0]);
sys=series(sys1,sys2);
sys=feedback(sys,1,-1);
t=[0:0.01:10];
step(sys,t)