K=[0:0.1:5];
n=length(K);
for i=1:n
    sys = tf([1],[1,5,K(i)-3,K(i)+1]);
    p(:,i)=pole(sys);
end
plot(real(p),imag(p),'x'),grid
text(-0.2,1.3,'K=5');
text(0,0.2,'K=0');


K=4;
sys = tf([1],[1,5,K-3,K+1]);
pole(sys)
