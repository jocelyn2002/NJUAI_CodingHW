t=[0:0.01:20];

omega=2;xi=0;
sys=tf(omega*omega,[1,2*xi*omega,omega*omega]);
pole(sys)
y=impulse(sys,t);
subplot(221),plot(t,y),title('omega=2,xi=0')

omega=2;xi=0.1;
sys=tf(omega*omega,[1,2*xi*omega,omega*omega]);
pole(sys)
y=impulse(sys,t);
subplot(222),plot(t,y),title('omega=2,xi=0.1')

omega=1;xi=0;
sys=tf(omega*omega,[1,2*xi*omega,omega*omega]);
pole(sys)
y=impulse(sys,t);
subplot(223),plot(t,y),title('omega=1,xi=0')

omega=1;xi=0.2;
sys=tf(omega*omega,[1,2*xi*omega,omega*omega]);
pole(sys)
y=impulse(sys,t);
subplot(224),plot(t,y),title('omega=1,xi=0.2')