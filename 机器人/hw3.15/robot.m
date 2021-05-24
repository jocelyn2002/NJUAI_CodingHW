clear all
% 定义D-H参数表
syms l1 l2 c1 c2 c4 d3
alpha1=0
alpha2=0
alpha3=0
alpha4=0
a1=0
a2=l1
a3=l2
a4=0
theta1 = c1
theta2 = c2
theta3 = 0
theta4 = c4
dis1=0
dis2=0
dis3=-d3
dis4=0
% 计算4个A矩阵
A1 = [cos(theta1),-sin(theta1),0,a1;
    sin(theta1)*cos(alpha1),cos(theta1)*cos(alpha1),-sin(alpha1),-dis1*sin(alpha1);
    sin(theta1)*sin(alpha1),cos(theta1)*sin(alpha1),cos(alpha1),dis1*cos(alpha1);
    0,0,0,1]
A2 = [cos(theta2),-sin(theta2),0,a2;
    sin(theta2)*cos(alpha2),cos(theta2)*cos(alpha2),-sin(alpha2),-dis2*sin(alpha2);
    sin(theta2)*sin(alpha2),cos(theta2)*sin(alpha2),cos(alpha2),dis2*cos(alpha2);
    0,0,0,1]
A3 = [cos(theta3),-sin(theta3),0,a3;
    sin(theta3)*cos(alpha3),cos(theta3)*cos(alpha3),-sin(alpha3),-dis3*sin(alpha3);
    sin(theta3)*sin(alpha3),cos(theta3)*sin(alpha3),cos(alpha3),dis3*cos(alpha3);
    0,0,0,1]
A4 = [cos(theta4),-sin(theta4),0,a4;
    sin(theta4)*cos(alpha4),cos(theta4)*cos(alpha4),-sin(alpha4),-dis4*sin(alpha4);
    sin(theta4)*sin(alpha4),cos(theta4)*sin(alpha4),cos(alpha4),dis4*cos(alpha4);
    0,0,0,1]
%正解
T=simplify(A1*A2*A3*A4)

%逆解
syms nx ny nz ox oy oz ax ay az px py pz
T40 = [nx ox ax px;
    ny oy ay py;
    nz oz az pz;
    0 0 0 1]

PX=l2*cos(c1 + c2) + l1*cos(c1)
PY=l2*sin(c1 + c2) + l1*sin(c1)
PZ=-d3
simplify(PX^2+PY^2)
c2=acos((px^2+py^2-l1^2-l2^2)/2l1l2)

simplify(inv(A1)*T40)
simplify(A2*A3*A4)

simplify(inv(A2)*inv(A1)*T40)
simplify(A3*A4)

simplify(inv(A3)*inv(A2)*inv(A1)*T40)
simplify(A4)
