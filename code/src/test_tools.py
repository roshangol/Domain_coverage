from .cfg.ControlFlow import get_cfg, gen_cfg, unhack
from .instrument import conditions
import ast
import astor
import csv
from colorama import Fore, Style
from graphviz import Digraph
import inspect
import matplotlib.pyplot as plt
import networkx as nx
import sys


def compute_dominator(cfg, start=0, key='parents'):
    # dominator tree of cfg compute with this function
    dominator = {}
    dominator[start] = {start}
    all_nodes = set(cfg.keys())
    rem_nodes = all_nodes - {start}
    for n in rem_nodes:
        dominator[n] = all_nodes
    c = True
    while c:
        c = False
        for n in rem_nodes:
            pred_n = cfg[n][key]
            doms = [dominator[p] for p in pred_n]
            i = set.intersection(*doms) if doms else set()
            v = {n} | i
            if dominator[n] != v:
                c = True
            dominator[n] = v
    return dominator


def compute_flow(pythonfile):
    # this function compute flow of program with using of dominator tree of cfg
    cfg, first, last = get_cfg(pythonfile)
    return cfg, compute_dominator(cfg, start=first), compute_dominator(
        cfg, start=last, key='children')


def to_graph(cache, arcs=[]):
    # convert CFG from CFGNode object in ControlFlow.py file format to graph with graphviz library 
    id_lineno = dict()
    graph = Digraph(comment='Control Flow Graph')
    colors = {0: 'blue', 1: 'red'}
    kind = {0: 'T', 1: 'F'}
    cov_lines = set(i for i, j in arcs)
    for _, cnode in cache.items():
        lineno = cnode.lineno()
        shape, peripheries = 'oval', '1'
        if isinstance(cnode.ast_node, ast.AnnAssign):
            if cnode.ast_node.target.id in {'_if', '_for', '_while'}:
                shape = 'diamond'
            elif cnode.ast_node.target.id in {'enter', 'exit'}:
                shape, peripheries = 'oval', '2'
        else:
            shape = 'rectangle'
        graph.node(cnode.i(), "%d: %s" % (lineno, unhack(cnode.source())),
                   shape=shape, peripheries=peripheries)
        id_lineno[cnode.i()] = lineno
        for pn in cnode.parents:
            plineno = pn.lineno()
            if hasattr(pn, 'calllink') and pn.calllink > 0 and not hasattr(
                    cnode, 'calleelink'):
                graph.edge(pn.i(), cnode.i(), style='dotted', weight=100)
                continue

            if arcs:
                if (plineno, lineno) in arcs:
                    graph.edge(pn.i(), cnode.i(), color='green')
                elif plineno == lineno and lineno in cov_lines:
                    graph.edge(pn.i(), cnode.i(), color='green')
                # child is exit and parent is covered
                elif hasattr(cnode, 'fn_exit_node') and plineno in cov_lines:
                    graph.edge(pn.i(), cnode.i(), color='green')
                # parent is exit and one of its parents is covered.
                elif hasattr(pn, 'fn_exit_node') and len(
                        set(n.lineno() for n in pn.parents) | cov_lines) > 0:
                    graph.edge(pn.i(), cnode.i(), color='green')
                # child is a callee (has calleelink) and one
                # of the parents is covered.
                elif plineno in cov_lines and hasattr(cnode, 'calleelink'):
                    graph.edge(pn.i(), cnode.i(), color='green')
                else:
                    graph.edge(pn.i(), cnode.i(), color='red')
            else:
                order = {c.i(): i for i, c in enumerate(pn.children)}
                if len(order) < 2:
                    graph.edge(pn.i(), cnode.i())
                else:
                    o = order[cnode.i()]
                    graph.edge(pn.i(), cnode.i(),
                               color=colors[o], label=kind[o])
    return graph, id_lineno


def show(cache):
    # show CFG networkx as plot
    g = nx.DiGraph()
    for _, cnode in cache.items():
        g.add_node(cnode.lineno())
        for pn in cnode.parents:
            if cnode.lineno() == 1:
                g.add_edge(pn.lineno(), "end", color="red")
            else:
                g.add_edge(pn.lineno(), cnode.lineno(), color="red")

    edge_color_list = [g[e[0]][e[1]]['color'] for e in g.edges()]
    nx.draw(g, with_labels=True, edge_color=edge_color_list)
    plt.show()


def repair_dot(path, pairs):
    # this function edit dot file according to line number of python function code
    pairs["2"] = 0
    file = path + "/Digraph.gv"
    with open(file, "r") as f:
        lines = f.readlines()

    with open(file, "w") as f:
        f.write("digraph {\n")
        for line in lines:
            if "->" in line:
                if line[1:3].isdigit() and line[7:9].isdigit():
                    if str(pairs[line[1:3]]) != str(pairs[line[7:9]]):
                        f.write("\t" + str(pairs[line[1:3]]) + " -> " + str(pairs[line[7:9]]) + line[9:])
                elif line[1:3].isdigit() and line[7:8].isdigit():
                    if str(pairs[line[1:3]]) != str(pairs[line[7:8]]):
                        f.write("\t" + str(pairs[line[1:3]]) + " -> " + str(pairs[line[7:8]]) + line[8:])
                elif line[1:2].isdigit() and line[6:8].isdigit():
                    if str(pairs[line[1:2]]) != str(pairs[line[6:8]]):
                        f.write("\t" + str(pairs[line[1:2]]) + " -> " + str(pairs[line[6:8]]) + line[8:])
                elif line[1:2].isdigit() and line[6:7].isdigit():
                    if str(pairs[line[1:2]]) != str(pairs[line[6:7]]):
                        f.write("\t" + str(pairs[line[1:2]]) + " -> " + str(pairs[line[6:7]]) + line[7:])
                else:
                    pass
            else:
                if line[1:3].isdigit():
                    f.write("\t" + str(pairs[line[1:3]]) + line[3:])
                elif line[1:2].isdigit():
                    f.write("\t" + str(pairs[line[1:2]]) + line[2:])
        f.write("}")


def cyclomatic_complexity(cache):
    # compute cyclomatic complexity of CFG
    g = nx.DiGraph()
    for _, cnode in cache.items():
        g.add_node(cnode.lineno())
        for pn in cnode.parents:
            if cnode.lineno() == 1:
                g.add_edge(pn.lineno(), "end", color="red")
            else:
                g.add_edge(pn.lineno(), cnode.lineno(), color="red")
    e = len(g.edges)
    n = len(g.nodes)
    return e - n + 2


def extract_dot(func, path):
    # this function create and extrac dot file of Control Flow Graph
    graph, pairs = to_graph(gen_cfg(func))
    graph.save(directory=path)
    repair_dot(path, pairs)


def extract_pdf(func, path):
    # this function create and extrac pdf file and schema of Control Flow Graph
    graph, pairs = to_graph(gen_cfg(func))
    graph.render(directory=path)
    repair_dot(path, pairs)


def show_graph(func):
    # show CFG networkx as plot
    return show(gen_cfg(func))


def max_line(input_path, file, func):
    # This function use for compute first and last line of a function defined in a python file
    ffile = open(input_path + "/" + file + ".py", "r")
    lines = ffile.readlines()
    rang = len(lines)
    name = "def " + str(func)
    min_number = float("inf")
    for number, line in enumerate(lines):
        if name in line:
            min_number = number + 1
        elif ("def" in line and number > min_number - 1):
            max_number = number
            break
        elif number == rang - 1:
            max_number = number + 1
        else:
            continue
    return max_number


def get_arguments(source):
    # This function extract argument of a function that given by user as SUT
    sourcee = ast.parse(source)
    for node in ast.walk(sourcee):
        if node.__class__.__name__ == "FunctionDef":
            for child in ast.iter_child_nodes(node):
                if hasattr(child, "args"):
                    return (astor.to_source(child))


def cyclomatic(func):
    # This function compute cyclomatic complexity of a SUT function cfg
    return cyclomatic_complexity(gen_cfg(func))


def get_annotations(mod, func):
    # extract argument name and types of function that given by user as SUT
    var_typ = []
    exec(f"from {mod} import {func}")
    sig = inspect.signature(eval(func))
    for i in sig.parameters.values():
        b = str(i.annotation)
        strr = b[8:-2]
        var_typ.append((i.name, strr))
    return var_typ


def get_argument_and_type(path, mod, function):
    # input argument and their type
    sys.path.append(path)
    exec(f"from {mod} import {function}")
    arg = {}
    arguments = get_annotations(mod, function)
    for i, j in arguments:
        arg.update({i: j})
    return arg


def repair_path_file(file):
    # dot file repairing
    with open(file, "r") as f:
        lines = f.readlines()

    with open(file, "w") as f:
        for line in lines:
            new_line = "["
            for word in line[1:-2].split(","):
                if word == "1":
                    new_line += "start,"
                elif word == " 0":
                    new_line += "end"
                else:
                    new = int(word)
                    new_line += (str(new) + ",")
            if new_line[-1] == "d":
                new_line += "] \n"
            else:
                new_line = new_line[:-1]
                new_line += "] \n"
            f.write(new_line)


def pc_extract(prime_pathes, source):
    # extract condition of one prime path
    path_conditions = list()
    line_cond, _ = conditions(source)
    # from sbst get the line_cond list
    for num, pp in enumerate(prime_pathes):
        print(str(num + 1) + ". " + str(pp))
    given = int(input(
        Fore.GREEN + "Please select path to extract condition: " + Style.RESET_ALL))
    cond = prime_pathes[given - 1]
    for i in cond:
        for j in range(0, len(line_cond[i])):
            new_cond = line_cond[i][j]
            path_conditions.append(new_cond[:-1])
    return path_conditions


def pc_num_extract(prime_path, source):
    # path condition and number of each condition
    _, line_cond_num = conditions(source)
    return line_cond_num


def line_true_false(prime_pathes, output_dir):
    # in a prime path which line execute wgeb condition is true or false
    path_true = dict()
    path_false = dict()
    with open(output_dir + "/CFG/Digraph.gv", "r") as f:
        lines = f.readlines()
    triple = list()
    for line in lines:
        if "->" in line:
            num3 = line.find("label=") + 6
            sign = line[num3]
            num1 = line.find("->") - 3
            if line[num1].isdigit():
                init = line[num1:num1 + 2]
            else:
                init = line[num1 + 1]

            num2 = line.find("->") + 3
            if line[num2:num2 + 2].isdigit():
                dest = line[num2:num2 + 2]
            else:
                dest = line[num2]
            if sign == "T" or sign == "F":
                triple.append([init, dest, sign])
    for i in prime_pathes:
        true_line = list()
        false_line = list()
        count = 0
        while count != len(i) - 1:
            if [str(i[count]), str(i[count + 1]), "T"] in triple:
                true_line.append(i[count])
            elif [str(i[count]), str(i[count + 1]), "F"] in triple:
                false_line.append(i[count])
            count += 1
        path_true.update({str(i): true_line})
        path_false.update({str(i): false_line})
    return path_true, path_false


def reformat_path(path):
    str_list = list()

    i = 0
    j = 1
    z = 0
    while i < len(path):
        maxx = 0
        j = i + 1
        D = i
        kk = 0
        while j < len(path):
            if path[i] == path[j]:
                if D == i:
                    z = j - i + 1
                    D = D + 1
                while path[i:i + z - 1] == path[j:j + z - 1]:
                    kk = 1
                    string2 = ""
                    if len(path[j:j + z - 1]) != 1:
                        for k in path[j:j + z - 1]:
                            string2 += str(k) + ","
                        str_list.append(string2[:-1])
                    j = j + z - 1
                    maxx = j
            if kk == 1:
                j = len(path)
            else:
                j = j + 1
        if kk == 1:
            i = maxx - 1
        else:
            i += 1

    string1 = ""
    for i in path:
        string1 += str(i) + ","
    for i in str_list:
        string1 = string1.replace(i, "@").replace("@", i, 1).replace("@", "")
    result = list()
    for i in string1.split(","):
        if i.isdigit():
            result.append(int(i))
    return result


def and_or(code_str):
    # extract and/or between condition
    ans = list()
    ans2 = list()
    for line in code_str.split("\n"):
        stat = line.split("evaluate_condition")
        for i in stat:
            ans.append(i)
    for i in range(0, len(ans)):
        try:
            if ans[i][0] == "(":
                if ans[i][-1] == ")" or ans[i][-1] == ":" or ans[i][-2:] == "d " or ans[i][-2:] == "r ":
                    ans2.append(ans[i])
                else:
                    ans2.append(ans[i] + ans[i + 1])
        except:
            pass
    last_ans = dict()
    last_ans[1] = "and"
    for i in range(0, len(ans2)):
        if i + 2 <= len(ans2):
            if ans2[i][-4:-1] == "and":
                last_ans[i + 2] = "and"
            elif ans2[i][-3:-1] == "or":
                last_ans[i + 2] = "or"
            else:
                last_ans[i + 2] = "and"

    return last_ans


def extract_branches(path):
    br = list()
    branches = list()
    end_branches = list()
    final_branch = list()
    result = list()
    i = 0
    j = 1
    new = 0
    while i < len(path):
        D = 0
        br = []
        while j < len(path):
            br.append(path[j - 1])
            if path[i] == path[j]:
                D = 1
                branches.append(path[new:i])
                new = j
                branches.append(br)
            if D == 0:
                j += 1
            else:
                k = j
                j = len(path)
        if D == 1:
            i = k
            j = i + 1
        else:
            i += 1
            j = i + 1
        if i == len(path):
            branches.append(path[new:i])
    a = dict()
    for br in branches:
        if br != [] and str(br[0]) in a:
            a.update({str(br[0]): a[str(br[0])] + 1})
        elif br != [] and str(br[0]) not in a:
            a[str(br[0])] = 1

        if br != [] and br[0] == 1:
            first = br
        elif br != [] and br[-1] == 0:
            last = br

        elif br == []:
            pass
        else:
            end_branches.append(br)
    for i in end_branches:
        branch = []
        for j in i:
            if j not in branch:
                branch.append(j)
            else:
                pass
        final_branch.append(branch)
    for i in final_branch:
        result.append(first + i)
    return result


def extrac__dom_to_csv(list_data, name, output_path):
    # extract domain point of fiven path to the csv file
    file = output_path + f"/Domain/{name}.csv"
    if file:
        open(file, 'w').close()
    with open(file, 'w', newline='') as f:
        try:
            length = len(list_data[0])
            fieldnames = [f"arg{i}" for i in range(0, length)]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for i in list_data:
                dicti = {}
                for num, arg in enumerate(i):
                    dicti[fieldnames[num]] = arg
                writer.writerow(dicti)
        except:
            pass


def extract_genetic_testdata_to_csv(info, name, output_path):
    file = output_path + f"/testdata/{name}_genetic.csv"
    if file:
        open(file, 'w').close()
    with open(file, 'w', newline='') as f:
        try:
            length = len(info[0][0])
            fieldnames = [f"arg{i}" for i in range(0, length)]
            fieldnames.append("covered_path")
        except:
            pass
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for td in info:
            dicti = {}
            for num, arg in enumerate(td[0]):
                dicti[fieldnames[num]] = arg
            dicti["covered_path"] = td[2]
            writer.writerow(dicti)


def extract_aco_testdata_to_csv(info, name, output_path):
    print(info)
    file = output_path + f"/testdata/{name}_ACO.csv"
    if file:
        open(file, 'w').close()
    with open(file, 'w', newline='') as f:
        try:
            length = len(info[0][0])
            fieldnames = [f"arg{i}" for i in range(0, length)]
            fieldnames.append("covered_path")
        except:
            pass
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for td in info:
            dicti = {}
            for num, arg in enumerate(td[0]):
                dicti[fieldnames[num]] = arg
            dicti["covered_path"] = td[3]
            writer.writerow(dicti)


def extract_aco_mao_testdata_to_csv(info, name, output_path):
    file = output_path + f"/testdata/{name}_ACO_mao.csv"
    if file:
        open(file, 'w').close()
    with open(file, 'w', newline='') as f:
        try:
            length = len(info[0][0])
            fieldnames = [f"arg{i}" for i in range(0, length)]
            fieldnames.append("covered_path")
        except:
            pass
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for td in info:
            dicti = {}
            for num, arg in enumerate(td[0]):
                dicti[fieldnames[num]] = arg
            dicti["covered_path"] = td[3]
            writer.writerow(dicti)


def extract_convergence_info(info, name, output_path, algorithm):
    file = output_path + f"/testdata/{name}_convergence_{algorithm}.csv"
    fieldnames = list()
    if file:
        open(file, 'w').close()
    with open(file, 'w', newline='') as f:
        fieldnames.append("average_fitness")
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        dicti = {}
        for i in info:
            dicti["average_fitness"] = i
            writer.writerow(dicti)


def dom_type(argums):
    dom = list()
    types = list()
    for var, typ in argums.items():
        low = input(f"please enter low of range for {var}:  ")
        high = input(f"please enter high value of range for {var}:  ")
        dom.append([int(low), int(high)])
        types.append([str(typ)])
    return dom, types


def percentage(big_list, little_list):
    count = 0
    little = [list(x) for x in set(tuple(x) for x in little_list)]
    for i in little:
        if i in big_list:
            count += 1
    res_percentage = (count / len(big_list)) * 100
    return res_percentage


def domain_partitioning(var_bound):
    part_size = list()
    new_var_bound = list()
    partition_ratio = int(input("please enter partition ratio for input space:"))
    for i in var_bound:
        upper = (int(i[1]))
        part = (int(upper) - int(i[0]) + 1)
        while part % partition_ratio != 0:
            upper += 1
            part = (int(upper) - int(i[0]) + 1)
        part_size.append(int(part / partition_ratio))
        new_var_bound.append([i[0], upper])
    return part_size, new_var_bound, partition_ratio


def domain_partitioning_mao(var_bound):
    part_size = list()
    new_var_bound = list()
    partition_ratio = 1
    for i in var_bound:
        upper = (int(i[1]))
        part = (int(upper) - int(i[0]) + 1)
        while part % partition_ratio != 0:
            upper += 1
            part = (int(upper) - int(i[0]) + 1)
        part_size.append(int(part / partition_ratio))
        new_var_bound.append([i[0], upper])
    return part_size, new_var_bound, partition_ratio


def which_part(x, dims, part_size):
    part = list()
    argss = ""
    for i in range(0, dims):
        argss += f"x[{str(i)}],"
    argums = "[" + argss[:-1] + "]"
    result = eval(argums)
    for i in range(0, dims):
        if result[i] % part_size == 0:
            p = int(result[i] / part_size)
        else:
            p = int(result[i] / part_size) + 1
        part.append(p)
    return part
