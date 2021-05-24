G=tf([1,10],[1,15,0,0]);
sys = feedback(G,[1],-1);
t = [0:0.1:50];
lsim(sys,t,t)