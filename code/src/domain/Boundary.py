import itertools
import csv
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


class boundary_points:
    def __init__(self,  test_data, vartype, varbound, function, p_prime, algorithm_parameters={"length": [10, 20], "budget": 20}):
        self.test_data = test_data
        self.p_prime = p_prime
        self.fitness_function = function
        self.budget = algorithm_parameters["budget"]
        self.limit = algorithm_parameters["length"]
        self.vartypes = vartype
        self.varbounds = varbound
        self.retracted_points = list()
        self.non_retracted_points = list()
        self.boundary_test_data = list()
        self.preprocess()

    def preprocess(self):
        len_dim = len(self.vartypes)
        self.oriantation = [list(x) for x in itertools.product([1, 0, -1], repeat=len_dim)]
        return self

    def reverse_oriantation(self, oriantation):
        rev = list()
        # the -1 * oriantaion equal with change of -1 to 1 and 1 to -1
        for i in oriantation:
            if i == 1:
                rev.append(-1)
            elif i == -1:
                rev.append(1)
            else:
                rev.append(0)
        return rev

    def check_for_range(self, data):
        for num, i in enumerate(data):
            low = self.varbounds[num][0]
            high = self.varbounds[num][1]
            if i < low or i > high:
                ans = False
                break
            else:
                ans = True
        return ans

    def boundary_for_oriantation(self, oriantation):
        ori = oriantation
        reverse = self.reverse_oriantation(oriantation)
        step_size = self.length
        t = 0
        flag = False
        while t < self.budget:
            test_data = [x + y for x, y in zip(self.test_data, [step_size * i for i in ori])]
            if self.check_for_range(test_data) is True:
                if (self.fitness_function(test_data) > 0.2):
                    step_size = int(step_size / 2)
                    ori = reverse
                    flag = True
                    self.retracted_points.append(test_data)
                else:
                    self.boundary_test_data.append(test_data)
                    if flag is True:
                        step_size = int(step_size / 2)
                        ori = reverse
                        flag = False
                        self.non_retracted_points.append(test_data)
            t += 1

    def run_boundary_point(self):
        for k in self.limit:
            self.length = k
            for i in self.oriantation:
                self.boundary_for_oriantation(i)
            # extract to csv
            res = list()
        for i in self.boundary_test_data:
            if i not in res:
                res.append(i)
        return res
