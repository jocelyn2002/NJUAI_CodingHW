def sum_plus(a):
    answer = 0
    for i in a:
        answer += i
    print(answer)



try:
    x = eval(input())
    sum_plus(x)
except:
    print("object of type 'int' has no len()!!!")

