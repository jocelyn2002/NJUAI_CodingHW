sys2=tf([-10],[1,10]);
sys3=tf([-1,-6],[1,3,6,0])
t1=2;K=1;t2=0.5;
t=0.1;%fast
num=-K*[t1*t t-2*t1 -2];
den=[t2*t t+2*t2 2];
sys1=tf(num,den);
sys=series(sys1,sys2);
sys=series(sys,sys3);
sys=feedback(sys,[1]);
fast = pole(sys)
t=0.6;%slow
num=-K*[t1*t t-2*t1 -2];
den=[t2*t t+2*t2 2];
sys1=tf(num,den);
sys=series(sys1,sys2);
sys=series(sys,sys3);
sys=feedback(sys,[1]);
slow = pole(sys)

tt=0.2044;
num=-K*[t1*tt tt-2*t1 -2];
den=[t2*tt tt+2*t2 2];
sys1=tf(num,den);
sys=series(sys1,sys2);
sys=series(sys,sys3);
sys=feedback(sys,[1]);
edge = pole(sys)