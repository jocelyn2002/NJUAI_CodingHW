group1=set(str(i) for i in [1,2,3,4,5])
group2=set(str(i) for i in [6,7,8,9,10])
vote=set(str(i) for i in [4,7,9,1,2,2,6,2,2,1,6,9,7,4,5,5,7,9,5,5,4])

num=input()
print(sorted(vote))
print(sorted(vote & group1))
print(sorted(group2 - vote))
if num in vote:
    print('Y')
else:
    print('N')
