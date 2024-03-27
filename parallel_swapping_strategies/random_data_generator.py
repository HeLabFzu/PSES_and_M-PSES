import numpy as np
def random_data_generator(path_lenth,std):
    path = []
    cost = {}
    random_numbers = np.random.normal(100, std, path_lenth-2)
    random_positive_numbers = np.abs(random_numbers)
    for i in range(0,path_lenth):
        path.append('x'+str(i))
        if i == 0 or i == path_lenth-1:
            cost[path[i]] = 0
        else:
            cost[path[i]] = random_positive_numbers[i-1]
#    print(np.std(random_positive_numbers))
    return path,cost

#if __name__=="__main__":
#    path,cost = random_data_generator(6, 50)
   # print(path)
   # print(cost)
