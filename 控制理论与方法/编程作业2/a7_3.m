sys1=tf([10],conv([1,10,0],[1,5]));
sys2=tf(conv([1,0.01],[1,5.5]),conv([1,6.5],[1,0.0001]));
sys=series(sys1,sys2);
rlocus(sys)

figure
K=8.58;
new_sys=series(sys1,sys2*K);
new_sys=feedback(new_sys,[1]);
step(new_sys)

figure
systd=feedback(sys1,sys2);
step(systd)