z=5;
sys1=tf(20/z*[1 z],[1 3 20]);
z=10;
sys2=tf(20/z*[1 z],[1 3 20]);
z=15;
sys3=tf(20/z*[1 z],[1 3 20]);


t = [0:0.01:5];
y1=step(sys1,t);
y2=step(sys2,t);
y3=step(sys3,t);
plot(t,y1,t,y2,t,y3),grid
xlabel('second');
ylabel('output');
title('blue for 5, red for 10, yellow for 15');
