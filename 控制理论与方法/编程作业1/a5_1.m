sys=tf([15],[1,8,15]);
t=[0:0.1:5];
y1 = impulse(sys,t);
y2 = 15/2*exp(-3*t)-15/2*exp(-5*t);
plot(t,y1,t,y2,'o'),grid
xlabel('seconds')
ylabel('output')
title('line for func:impulse, o for analytic solution');