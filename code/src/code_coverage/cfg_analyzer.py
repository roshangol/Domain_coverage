import networkx as nx
import matplotlib.pyplot as plt
from .path_finder import simple_paths, prime_paths, change_str_list, change_str_listoflist, change_str_listoflistoflist
from .prime_path_coverage import prime_path_coverage_bruteforce, prime_path_coverage_superset


class cfg_coverage:

    def __init__(self, file_path_name, first_node, last_node):
        # initialize object with reading first and last node and construct graph from file
        self.graph = nx.drawing.nx_pydot.read_dot(file_path_name)
        self.first = str(first_node)
        self.last = str(last_node)

    def graph_nodes(self):
        # This function return all nodes in your CFG
        res = change_str_list(list(self.graph.nodes()))
        return res

    def graph_edge(self):
        # This function return all edges in your CFG
        res = change_str_listoflist(list(self.graph.edges()))
        return res

    def edge_pair(self):
        # this function return two edge who are continusly connect to each other in CFG
        edges = list()
        self.pairs = list()
        for edge in self.graph_edge():
            edges.append(edge)
        for i in edges:
            for j in edges:
                if i == j:
                    continue
                else:
                    if i[1] == j[0]:
                        self.pairs.append([i[0], i[1], j[1]])
        return self.pairs

    def cyclomatic_complexity(self):
        # cyclomatic number of CFG show the minimum number of basis path
        scyclomatic = len(self.graph_edge()) - len(self.graph_nodes()) + 2
        return scyclomatic

    def simple_path(self):
        # simple path defined in offutt book tou find link in git repository
        simples = simple_paths(self.graph)
        res = change_str_listoflist(simples)
        return res

    def prime_path(self):
        # return list of all prime path
        primes = prime_paths(self.graph, self.first, self.last)
        res = change_str_listoflist(primes)
        return res

    def prime_path_coverage_bruteforce(self):
        # bruteforce method define in article in repo.
        # res_tp return minimum execution path which cover all prime path's
        # res_tr return list of test requirement satisfied with test path's in list res_tp.
        tp, tr = prime_path_coverage_bruteforce(self.graph, self.first, self.last)
        res_tp = change_str_listoflist(tp)
        res_tr = change_str_listoflistoflist(tr)
        return res_tp, res_tr

    def prime_path_coverage_setcoverage(self):
        # set coverage super test requirement based  method define in article in repo.
        # res_tp return minimum execution path which cover all prime path's
        # res_tr return list of test requirement satisfied with test path's in list res_tp.
        tp, tr = prime_path_coverage_superset(self.graph, self.first, self.last)
        res_tp = change_str_listoflist(tp)
        res_tr = change_str_listoflistoflist(tr)
        return res_tp, res_tr

    def draw_cfg(self):
        # draw input graph files as networkx graph
        nx.draw(self.graph, with_labels=True)
        plt.show()
