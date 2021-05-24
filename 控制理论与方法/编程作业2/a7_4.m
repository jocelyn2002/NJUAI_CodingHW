% 比例控制器
G1=tf([1],[1,5,6]);
rlocus(G1)
hold on
plot([-0.4,-0.4],[-100,100],'--',...
    [0,-10],[0,-10*tan(53.8*pi/180)],'--',...
    [0,-10],[0,10*tan(53.8*pi/180)],'--')
hold off
axis([-6,1,-6,6])
[k1,poles1]=rlocfind(G1)

% 积分控制器
figure
G2=tf([1],[1,5,6,0]);
rlocus(G2)
hold on
plot([-0.4,-0.4],[-100,100],'--',...
    [0,-10],[0,-10*tan(53.8*pi/180)],'--',...
    [0,-10],[0,10*tan(53.8*pi/180)],'--')
hold off
axis([-6,1,-6,6])
[k2,poles2]=rlocfind(G2)

% 比例积分控制器
figure
G3=tf([1,1],[1,5,6,0]);
rlocus(G3)
hold on
plot([-0.4,-0.4],[-100,100],'--',...
    [0,-10],[0,-10*tan(53.8*pi/180)],'--',...
    [0,-10],[0,10*tan(53.8*pi/180)],'--')
hold off
axis([-6,1,-6,6])
[k3,poles3]=rlocfind(G3)

%响应
figure
t=[0:0.1:15];
sys1=feedback(k1*G1,[1]);
sys2=feedback(k2*G2,[1]);
sys3=feedback(k3*G3,[1]);
y1=step(sys1,t);
y2=step(sys2,t);
y3=step(sys3,t);
plot(t,y1,t,y2,t,y3),grid
