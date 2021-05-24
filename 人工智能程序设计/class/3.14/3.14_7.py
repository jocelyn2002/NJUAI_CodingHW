x = int(input())
def fenjie(x ,y):
   if x < 2*y:
       print(int(x))
   else:
       i = y
       while i >= y:
           if x%i==0 and x/i>=i:
               print(str(i)+'*', end='')
               fenjie(x/i, i)
               break
           elif x%i==0 and x/i<i:
               print(str(i))
               break
           else:
                i += 1


print(x, '= ', end='')
fenjie(x, 2)




