from datetime import datetime
import os
# 固定随机种子
np.random.seed(2021)
os.environ['PYTHONHASHSEED'] = str(2021)

# # NSGA-II Test
# from my_NSGA_II import *
# result = []

# # 2d
# from Max_Cut_main_2D import *
# data=GetFacebookData('./football.gml')
# objectiveFunc = ObjectiveFunction(data)
# population = NSGA(dimension=2)
# ratio = Max_Cut_RRMS_2D.Do(population, data, objectiveFunc)
# print(datetime.now().strftime('20%y-%m-%d %H:%M:%S'),'the regret ratio 2d is %f'%(ratio))
# result.append(ratio)

# # 3d
# from Max_Cut_main_3D import *
# data=GetFacebookData('./football.gml')
# objectiveFunc = ObjectiveFunction(data)
# population = NSGA(dimension=3)
# ratio = Max_Cut_RRMS_3D.Do(population, data, objectiveFunc)
# print(datetime.now().strftime('20%y-%m-%d %H:%M:%S'),'the regret ratio 3d is %f'%(ratio))
# result.append(ratio)

# # 4d
# from Max_Cut_main_4D import *
# data=GetFacebookData('./football.gml')
# objectiveFunc = ObjectiveFunction(data)
# population = NSGA(dimension=4)
# ratio = Max_Cut_RRMS_4D.Do(population, data, objectiveFunc)
# print(datetime.now().strftime('20%y-%m-%d %H:%M:%S'),'the regret ratio 4d is %f'%(ratio))
# result.append(ratio)

# # 5d
# from Max_Cut_main_5D import *
# data=GetFacebookData('./football.gml')
# objectiveFunc = ObjectiveFunction(data)
# population = NSGA(dimension=5)
# ratio = Max_Cut_RRMS_5D.Do(population, data, objectiveFunc)
# print(datetime.now().strftime('20%y-%m-%d %H:%M:%S'),'the regret ratio 5d is %f'%(ratio))
# result.append(ratio)

# print("NSGA-II results: ",result)



# MOEA/D Test
from my_MOEA_D import *
result = []

# 2d
from Max_Cut_main_2D import *
data=GetFacebookData('./football.gml')
objectiveFunc = ObjectiveFunction(data)
population = MOEA(dimension=2)
ratio = Max_Cut_RRMS_2D.Do(population, data, objectiveFunc)
print(datetime.now().strftime('20%y-%m-%d %H:%M:%S'),'the regret ratio 2d is %f'%(ratio))
result.append(ratio)

# 3d
from Max_Cut_main_3D import *
data=GetFacebookData('./football.gml')
objectiveFunc = ObjectiveFunction(data)
population = MOEA(dimension=3)
ratio = Max_Cut_RRMS_3D.Do(population, data, objectiveFunc)
print(datetime.now().strftime('20%y-%m-%d %H:%M:%S'),'the regret ratio 3d is %f'%(ratio))
result.append(ratio)

# 4d
from Max_Cut_main_4D import *
data=GetFacebookData('./football.gml')
objectiveFunc = ObjectiveFunction(data)
population = MOEA(dimension=4)
ratio = Max_Cut_RRMS_4D.Do(population, data, objectiveFunc)
print(datetime.now().strftime('20%y-%m-%d %H:%M:%S'),'the regret ratio 4d is %f'%(ratio))
result.append(ratio)

# 5d
from Max_Cut_main_5D import *
data=GetFacebookData('./football.gml')
objectiveFunc = ObjectiveFunction(data)
population = MOEA(dimension=5)
ratio = Max_Cut_RRMS_5D.Do(population, data, objectiveFunc)
print(datetime.now().strftime('20%y-%m-%d %H:%M:%S'),'the regret ratio 5d is %f'%(ratio))
result.append(ratio)

print("MOEA_D results: ",result)