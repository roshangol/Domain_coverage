import ast
import os
import astor
from collections import defaultdict

line_cond = defaultdict(list)
line_cond_num = defaultdict(list)
imports = list()


class BranchTransformer(ast.NodeTransformer):
    branch_num = 0

    def visit_FunctionDef(self, node):
        node.name = node.name + "_instrumented"
        return self.generic_visit(node)

    def visit_Compare(self, node):
        line_cond[node.lineno].append(astor.to_source(node))

        if node.ops[0] in [ast.Is, ast.IsNot, ast.In, ast.NotIn]:
            return node

        self.branch_num += 1
        line_cond_num[node.lineno].append(self.branch_num)
        return ast.Call(func=ast.Name("evaluate_condition", ast.Load()),
                        args=[ast.Num(self.branch_num), ast.Str(node.ops[0].__class__.__name__), node.left,
                              node.comparators[0]], keywords=[], starargs=None, kwargs=None)


def save_as_instrumented_python(instrumented, input_file, name, path):
    out_path = path + "/Code/" + f"{name}_instrumented.py"
    evalue_dir = os.path.dirname(os.path.abspath(__file__))
    cov_dir = evalue_dir[:-11]
    imports = import_count(path + "/Code", input_file)
    extra = max_line(path, input_file, name)

    with open(out_path, "w") as file:
        for i in imports:
            file.write(i)
        file.write("import sys\n")
        file.write("sys.path.append(r'{a}')\n".format(a=evalue_dir))
        file.write("sys.path.append(r'{a}')\n".format(a=cov_dir))
        file.write("from runner import evaluate_condition\n")
        file.write("from Coverage import cover_decorator\n")      # fix problem
        file.write("\n")
        file.write("@cover_decorator\n")
        ins = instrumented.replace("True", "True is True")
        file.write(f"{ins}")
        for i in extra:
            file.write(i)

def max_line(input_path, file, func):
    ffile = open(input_path + "/Code/" + file + ".py", "r")
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
    extra = lines[max_number:]    
    return extra

def instrument_extraction(source, input_file, func_name, path):
    node = ast.parse(source)
    BranchTransformer().visit(node)
    node = ast.fix_missing_locations(node)
    save_as_instrumented_python(astor.to_source(node), input_file, func_name, path)


def conditions(source):
    global line_cond
    global line_cond_num
    line_cond = defaultdict(list)
    line_cond_num = defaultdict(list)
    node = ast.parse(source)
    BranchTransformer().visit(node)
    node = ast.fix_missing_locations(node)
    return line_cond, line_cond_num


def import_count(path, mod):
    imports = list()
    count = 0
    tree = ast.parse(open(f'{path}/{mod}.py').read())
    for i in ast.walk(tree):
        if i.__class__.__name__ == "Import":
            imports.append(astor.to_source(i))
            count += 1
    return imports
