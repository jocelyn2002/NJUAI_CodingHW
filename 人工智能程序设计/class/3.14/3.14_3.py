y=input().split()
x=[float(i) for i in y]
if x[1]==0:
    rmb=x[0] * x[2]
    print('$%.1f is %.1f yuan'%(x[2],rmb))
elif x[1]==1:
    dollar=x[2]/x[0]
    print('%.1f yuan is $%.1f' % (x[2], dollar))
else:
    print('Incorrect Input')