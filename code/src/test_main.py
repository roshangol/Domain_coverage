import inspect
import sys
import os
import threading
import time
import csv
from shutil import copyfile
from colorama import Fore, Style
from .test_tools import show_graph, extract_pdf, extract_dot, repair_path_file, pc_extract, pc_num_extract, \
    max_line, get_argument_and_type, percentage
from .code_coverage import cfg_coverage
from .instrument import code_instrumentation
from .domain import mcmc_dom, boundary_points
from .runner import run


class domain_extraction:
    def __init__(self, input_path, input_file, func, output_path):
        self.input_path = input_path
        self.file = input_file[:-3]
        self.function = func
        self.output_path = output_path
        self.directories()
        self.instrumented_file = self.function + "_instrumented"
        self.instrumented_function = self.function + "_instrumented"
        self.get_code()
        self.get_function()
        self.extract_dot()
        self.arg_input = input_file
        self.code_instrument()
        self.arg_func = func
        self.arg = {}
        thread = threading.Thread(target=self.path_info)
        thread.daemon = True
        thread.start()
        time.sleep(2)

    def extract_info(self):
        # basic input info of class
        return self.input_path, self.file, self.function, self.output_path

    def get_code(self):
        # read program under test source code as input to adopted source code style
        sys.path.append(self.input_path)
        exec(f"from {self.file} import {self.function}")
        self.source = inspect.getsource(
            eval(f"{self.function}"))
        return (self)

    def get_function(self):
        # function name returned
        self.func = f"{self.function}"
        return self

    def directories(self):
        # create report directories on output path
        os.makedirs(self.output_path + "/Code", exist_ok=True)
        os.makedirs(self.output_path + "/report", exist_ok=True)
        os.makedirs(self.output_path + "/CFG", exist_ok=True)
        os.makedirs(self.output_path + "/Domain", exist_ok=True)
        os.makedirs(self.output_path + "/path", exist_ok=True)
        src = self.input_path + f"/{self.file}.py"
        dst = self.output_path + f"/Code/{self.file}.py"
        copyfile(src, dst)

    def code_instrument(self):
        # inject new code to orginal input to extract runtime information of program under test
        code_instrumentation(self.input_path, self.file, self.function, self.output_path)

    def extract_dot(self):
        # ecxtract dot file format of control flow graph of program under test
        path = self.output_path + "/CFG"
        extract_dot(self.source, path)

    def show_graph(self):
        # ecxtract networkx and plot format of control flow graph of program under test
        show_graph(self.source)

    def extract_pdf(self):
        # ecxtract pdf file format of control flow graph of program under test
        path = self.output_path + "/CFG"
        extract_pdf(self.source, path)

    def path_info(self):
        # return all simle path, primre path and minimum path for coverage all prime paths with two algorithm
        # TODO:
        # - article sitation
        gv_path = self.output_path + "/CFG/Digraph.gv"
        self.cfg_dot = cfg_coverage(gv_path, 1, 0)
        self.simple_pathes = self.cfg_dot.simple_path()
        self.prime_pathes = self.cfg_dot.prime_path()
        self.prime_coverage, self.prime_req = self.cfg_dot.prime_path_coverage_bruteforce()
        self.prime_coverage1, self.prime_req1 = self.cfg_dot.prime_path_coverage_setcoverage()
        print("\n" + Fore.RED + "path information generated" + Style.RESET_ALL)
        return self

    def extract_simple_path(self):
        # extract simple path of program under test
        simple_file = self.output_path + "/path/simplepathes.txt"
        if simple_file:
            open(simple_file, 'w').close()
        with open(simple_file, "a") as f:
            for i in self.simple_pathes:
                f.write(str(i) + "\n")

    def extract_prime_path(self):
        # extract prime paths of program under test
        # TODO:
        # prime path defination on offout
        prime_file = self.output_path + "/path/primepathes.txt"
        if prime_file:
            open(prime_file, 'w').close()
        with open(prime_file, "a") as f:
            for i in self.prime_pathes:
                f.write(str(i) + "\n")

    def extract_prime_path_coverage_bruteforce(self):
        # extract minimum path need to cover all prime paths(brute force method)
        prime_coverage = self.output_path + "/path/prime_coverage_bruteforce.txt"
        prime_req_file = self.output_path + "/path/prime_cov_requirement_bruteforce.txt"
        if prime_coverage:
            open(prime_coverage, 'w').close()
        if prime_req_file:
            open(prime_req_file, 'w').close()
        with open(prime_coverage, "a") as f:
            for i in self.prime_coverage:
                f.write(str(i) + "\n")

        with open(prime_req_file, "a") as f:
            for i in self.prime_req:
                f.write(str(i) + "\n")

    def extract_prime_path_coverage_setcover(self):
        # extract minimum path need to cover all prime paths(setcover method)
        prime_coverage = self.output_path + "/path/prime_coverage_setcover.txt"
        prime_req_file = self.output_path + "/path/prime_cov_requirement_setcover.txt"
        if prime_coverage:
            open(prime_coverage, 'w').close()
        if prime_req_file:
            open(prime_req_file, 'w').close()
        with open(prime_coverage, "a") as f:
            for i in self.prime_coverage1:
                f.write(str(i) + "\n")

        with open(prime_req_file, "a") as f:
            for i in self.prime_req1:
                f.write(str(i) + "\n")

    def report(self):
        # create report csv file of function name, line of code(loc), count of arguments, count of prime paths, and minimum prime path
        report_file = self.output_path + "/report/report.csv"
        loc = max_line(self.input_path, self.file, self.function)
        arg = len(get_argument_and_type(self.input_path, self.file, self.function))
        prims = len(self.prime_pathes)
        minprim = len(self.prime_coverage)
        if report_file:
            open(report_file, 'w').close()
        with open(report_file, 'w', newline='') as file:
            fieldnames = ['function_name', 'LoC', '#arg', '#prime_path', '#min_execution_path']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow({'function_name': self.function, 'LoC': loc, '#arg': arg, '#prime_path': prims,
                            '#min_execution_path': minprim})
        return loc, arg, prims, minprim

    def mcmc_domain(self, p_path, algorithm_parameters):
        print(p_path)
        ind_path = self.prime_coverage.index(p_path)
        requirement = self.prime_req[ind_path]
        aa = run(mcmc_dom, "mcmc_domain", self.input_path, self.file, self.function,
                 self.output_path, self.source, self.prime_pathes, requirement, p_path, '', algorithm_parameters)
        dom_point = aa.execute()
        points = ["points"]
        with open(f'{self.output_path}/Domain/{self.function}_mcmc_domain.csv', 'w', newline='') as f:
            write = csv.writer(f, delimiter=',')
            write.writerow(points)
            write.writerows(dom_point)

    def boundary_point(self, b_path, test_data, algorithm_parameters):
        ind_path = self.prime_coverage.index(b_path)
        requirement = self.prime_req[ind_path]
        aa = run(boundary_points, "boundary_points", self.input_path, self.file, self.function,
                 self.output_path, self.source, self.prime_pathes, requirement, b_path, test_data, algorithm_parameters)
        aa.execute()


def delete_file():
    pt = os.path.dirname(os.path.abspath(__file__))
    os.remove(f"{pt}/False")
    os.remove(f"{pt}/Trues")
