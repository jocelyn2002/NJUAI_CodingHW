dz={'username':'dazhuang','password':'233'}
fh={'username':'fuhao','password':'123'}
jj=[dz,fh]
x=input().split(',')
k=0
for user in jj:
    if (user['username'] == x[0]) and (user['password']==x[1]):
        print('Yes!')
        k=1
if k==0:
    print('Wrong!')

