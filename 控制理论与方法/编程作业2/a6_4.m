K=[0:0.1:30];
n=length(K);
for i=1:n
    G=tf([5],[1,10,0]);
    H=tf([2,K(i)],[1,0]);
    sys=feedback(G,H);
    p(:,i)=pole(sys);
end
plot(real(p),imag(p),'x'),grid