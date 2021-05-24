sys1=tf([0.5,2],[1,0])
sys2=tf(1,[1,2,0])
sys=series(sys1,sys2)
sys=feedback(sys,1,-1)
t=[0:0.1:100]
subplot(311),impulse(sys,t)
subplot(312),step(sys,t)
subplot(313),lsim(sys,t,t)