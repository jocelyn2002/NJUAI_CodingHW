import matplotlib.pyplot as plt
# import matplotlib.ticker as ticker

my = [[3,87],[4,293],[6,122],[5,302],[2,1010]]
rhea = [[3,373],[4,1230],[5,584],[3,671],[1,2000]]
mcts = [[3,50],[4,642],[6,898],[5,1442],[5,1803]]
rs = [[3,156],[2,266],[3,167],[4,737],[3,2000]]

algorithms = {"My":my,"RHEA":rhea,"MCTS":mcts,"RS":rs}
for name,value in algorithms.items():
    for v in value:
        v[0] += 1

plt.figure()
x = range(5)
for name,value in algorithms.items():
    y = []
    for v in value:
        y.append(v[1]  / v[0])
        # y.append(v[1])
    plt.plot(x,y,label=name)

plt.xlabel("game_level")
plt.ylabel("time / score")
plt.title("112 : asteroids")
plt.legend(loc="upper left")

plt.show()