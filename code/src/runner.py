import sys
import csv

distances_true = {}
distances_false = {}


class run:
    def __init__(self, search_algorithm, algorithm_name, input_path, file_name, function_name,
                 output_path, source, prime_pathes, requirement, p_path, test_data,algorithm_parameters):
        from .test_tools import get_argument_and_type, pc_num_extract, line_true_false, and_or, dom_type
        self.algorithm = search_algorithm
        self.algorithm_name = algorithm_name
        self.algorithm_parameters = algorithm_parameters
        self.function_name = function_name
        self.output_path = output_path
        self.input_path = input_path
        self.p_path = p_path
        self.test_data = test_data

        if algorithm_name == "mcmc_domain":
            self.fitness = mcmc_fitness

        elif algorithm_name == "boundary_points":
            self.fitness = boundary_fitness

        global dims, instrumented_file, out_path, and_or_dict, pp_prime, trues_false, func, require, trues, falses, p_prime, p_requirement
        p_prime = p_path
        p_requirement = requirement
        func = function_name
        pp_prime = prime_pathes
        instrumented_file = function_name + "_instrumented"
        out_path = output_path + "/Code"
        with open(output_path + f"/Code/{instrumented_file}.py", 'r') as file:
            code = file.read()
        and_or_dict = and_or(code)
        trues_false = list(and_or_dict.keys())
        ar = get_argument_and_type(input_path, file_name, function_name)
        self.varbound, self.vartyp = dom_type(ar)
        dims = int(len(ar))
        path_line_true, path_line_false = line_true_false(
            prime_pathes, output_path)

        trues = list()
        falses = list()
        try:
            line_true = path_line_true[str(p_path)]
            line_false = path_line_false[str(p_path)]
            indx = prime_pathes.index(p_path)
            require = requirement[indx]
            nums = pc_num_extract(prime_pathes, source)
            for i in line_true:
                for j in nums[i]:
                    trues.append(int(j))
            for i in line_false:
                for j in nums[i]:
                    falses.append(int(j))
        except:
            pass

    def execute(self):

        if self.algorithm_name == "mcmc_domain":
            # path which try to generate domain p_prime
            # requirement for their path
            model = self.algorithm(function=self.fitness, vartype=self.vartyp, varbound=self.varbound,
                                   algorithm_parameters=self.algorithm_parameters)
            dom_point = model.run_dom_mcmc()
            return dom_point

        elif self.algorithm_name == "boundary_points":
            # extract csv file for test data
            model = self.algorithm(test_data= self.test_data, function=self.fitness, vartype=self.vartyp, varbound=self.varbound,
                                   p_prime=p_prime.copy(), algorithm_parameters=self.algorithm_parameters)
            datas = model.run_boundary_point()
            with open(f"{self.output_path}/Domain/boundary_{self.function_name}.csv", 'w', newline='') as f:
                writer = csv.writer(f, delimiter=',')
                writer.writerow(["boundary_datas"])
                for i in datas:
                    writer.writerow(i)


def update_maps(condition_num, d_true, d_false):
    global distances_true, distances_false

    if condition_num in distances_true.keys():
        distances_true[condition_num] = min(
            distances_true[condition_num], d_true)
    else:
        distances_true[condition_num] = d_true

    if condition_num in distances_false.keys():
        distances_false[condition_num] = min(
            distances_false[condition_num], d_false)
    else:
        distances_false[condition_num] = d_false


def evaluate_condition(num, op, lhs, rhs):
    distance_true = 0
    distance_false = 0

    if isinstance(lhs, str):
        lhs = ord(lhs)
    if isinstance(rhs, str):
        rhs = ord(rhs)

    if op == "Eq":
        if lhs == rhs:
            distance_false = 1
        else:
            distance_true = abs(lhs - rhs)

    elif op == "NotEq":
        if lhs != rhs:
            distance_false = abs(lhs - rhs)
        else:
            distance_true = 1

    elif op == "Lt":
        if lhs < rhs:
            distance_false = rhs - lhs
        else:
            distance_true = lhs - rhs + 1

    elif op == "LtE":
        if lhs <= rhs:
            distance_false = rhs - lhs + 1
        else:
            distance_true = lhs - rhs

    elif op == "Gt":
        if lhs > rhs:
            distance_false = lhs - rhs
        else:
            distance_true = rhs - lhs + 1

    elif op == "GtE":
        if lhs >= rhs:
            distance_false = lhs - rhs + 1
        else:
            distance_true = rhs - lhs

    elif op == "In":
        minimum = sys.maxsize
        for elem in rhs:
            distance = abs(lhs - elem)
            if distance < minimum:
                minimum = distance

        distance_true = minimum
        if distance_true == 0:
            distance_false = 1

    update_maps(num, distance_true, distance_false)

    if distance_true == 0:
        return True
    else:
        return False


def check(l1, l2):
    # return True if list2 is sublist of list1 but order of l2 is same in l1.
    index_list = [i for i, v in enumerate(l1) if v == l2[0]]
    for ii in index_list:
        l1_slice = l1[ii:ii + len(l2)]
        if l1_slice == l2:
            return True
    else:
        return False


def normalize(x):
    return x / (1.0 + x)


def mcmc_fitness(x):
    exe_file = instrumented_file
    sys.path.append(out_path)
    exec(f"from {instrumented_file} import {instrumented_file}")
    argss = ""
    for i in range(0, dims):
        argss += f"x[{str(i)}],"
    exe_file += "(" + argss[:-1] + ")"
    executed_path, result = eval(exe_file)

    NC = 0
    covered_list = list()
    for i in p_requirement:
        if check(executed_path, i) is True:
            covered_list.append(i)
            NC += 1
    APP = len(p_requirement)
    cov_path = 1 - (NC / APP)

    # Sum up branch distances
    fitness = 0.0
    for branch in trues_false:
        if branch in distances_true:
            if and_or_dict[branch] == "and":
                fitness += normalize(distances_true[branch])
            elif and_or_dict[branch] == "or":
                fitness = min(fitness, normalize(distances_true[branch]))
        # else:
        #     fitness += 1.0

    for branch in trues_false:
        if branch in distances_false:
            if and_or_dict[branch] == "and":
                fitness += normalize(distances_false[branch])
            elif and_or_dict[branch] == "or":
                fitness = min(fitness, normalize(distances_false[branch]))
        # else:
        #     fitness += 1.0
    return fitness


def boundary_fitness(x):
    exe_file = instrumented_file
    sys.path.append(out_path)
    exec(f"from {instrumented_file} import {instrumented_file}")
    argss = ""
    for i in range(0, dims):
        argss += f"x[{str(i)}],"
    exe_file += "(" + argss[:-1] + ")"
    executed_path, result = eval(exe_file)
    NC = 0
    covered_list = list()
    for i in p_requirement:
        if check(executed_path, i) is True:
            covered_list.append(i)
            NC += 1
    # Sum up branch distances
    fitness = 0.0
    for branch in trues_false:
        if branch in distances_true:
            if and_or_dict[branch] == "and":
                fitness += normalize(distances_true[branch])
            elif and_or_dict[branch] == "or":
                fitness = min(fitness, normalize(distances_true[branch]))
    for branch in trues_false:
        if branch in distances_false:
            if and_or_dict[branch] == "and":
                fitness += normalize(distances_false[branch])
            elif and_or_dict[branch] == "or":
                fitness = min(fitness, normalize(distances_false[branch]))
    return fitness
