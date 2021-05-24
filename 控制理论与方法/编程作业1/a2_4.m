g=tf([1,1],[1,2]);
h=tf([1],[1,1]);
sys=feedback(g,h,-1)

pzmap(sys)
p=pole(sys)
z=zero(sys)

sys=minreal(sys)