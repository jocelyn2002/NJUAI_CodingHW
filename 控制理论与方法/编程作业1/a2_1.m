j=10.8e+8;k=10.8e+8;a=1;b=8;
num=k*[1 a];den=j*[1 b 0 0];
sys = tf(num,den);
sys = feedback(sys,[1],-1);

t = [0:0.1:100];

in = 10*pi/180;
out = sys*in;
y = step(out,t);
plot(t,y*180/pi),grid;

j=10.8e+8*0.8;k=10.8e+8;a=1;b=8;
num=k*[1 a];den=j*[1 b 0 0];
sys = tf(num,den);
sys = feedback(sys,[1],-1);
in = 10*pi/180;
out = sys*in;
y1 = step(out,t);

j=10.8e+8*0.5;k=10.8e+8;a=1;b=8;
num=k*[1 a];den=j*[1 b 0 0];
sys = tf(num,den);
sys = feedback(sys,[1],-1);
in = 10*pi/180;
out = sys*in;
y2 = step(out,t);

plot(t,y*180/pi,t,y1*180/pi,t,y2*180/pi),grid;
xlabel('second');
ylabel('degree');
title('blue for 100%, red for 80%, yellow for 50%');
