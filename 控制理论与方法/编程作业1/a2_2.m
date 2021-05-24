sys1=tf([1],[1 0 0]);
sys1=feedback(sys1,[50],1);

sys2=tf([1],[1,1]);
sys3=tf([1 0],[1 0 2]);
sys4=series(sys2,sys3);
sys5=tf([4 2],[1,2,1]);
sys6=feedback(sys4,sys5,-1);

sys7=series(sys6,sys1);
sys8=tf([1 0 2],[1 0 0 14]);
sys9=feedback(sys7,sys8,-1);

sys10=tf([4],[1]);
sys11=series(sys10,sys9);
sys11 = minreal(sys11)


pzmap(sys11)


p=pole(sys11)
z=zero(sys11)