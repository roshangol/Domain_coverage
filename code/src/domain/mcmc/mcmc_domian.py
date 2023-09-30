"""
mote carlo markov chain (mcmc) algorithm

for each state if new test case cover goal path hypothesis acceppt for that partition else hypothesis will be reject.



metropolis hasting algorithm:

P is goal distribution, Q is proposal distribution.
𑜅 = min {1, [P(θ*) / P(θ(t-1) )] * [Q(θ(t-1) | θ*)  / Q(θ* | θ(t-1) )]}
P = probablity of covering path.
Q = probablity neighboar point of present point in specific distribution. (if Q be symetric distribution then heisting metropolis covert to random walk metropolis )


goal distribution:

T(x) = {1     if distance from input path greater than 0
            {0     if distance from given path equal to 0

P(x) = p(T(x)= 0 | cov(x))


proposal distribution:

change of each state occure with random walk behaviour. this concept replace proposal distribution with
random walk behaviour to generate new candidate. random walk behaviour for poposal distribution maintain
with normal distribution:
                                            Q(x) = normal_distribution(x, sigma) for each dimention

another hand symetric feature of normal distribution.
this feature cause for removing Q(θ(t-1) | θ*) and Q(θ* | θ(t-1) ):
                                                                                                        𑜅 = min {1, P(θ*) / P(θ(t-1) )}

Component wise updating:
"""

__author__ = "Roshan Golmohammadi"


from ...test_tools import domain_partitioning, which_part
import sys
import numpy as np
import random
from operator import attrgetter


class agent:
    def __init__(self, data, T, prob):
        self.theta = [0] * T
        self.probablity = [0] * T
        self.theta[0] = data
        self.probablity[0] = prob
        # for score to guide we have:
        # if answer is accepted and point that detected by agent is not answer list +1
        # if answer is accepted and point that detected by agent is in anwer list 0
        # if answer is not accepted -1
        self.score = 0
        # for controling local trap
        self.threshold = 0


class mcmc_dom:
    def __init__(self, function, vartype, varbound,
                 algorithm_parameters={'test_budget': None,
                                       'max_chanin_long': 30,
                                       'agent_number': 10,
                                       'step_size': 2}):
        # data must be compatible with type of int and float
        self.goal_dist = function
        self.iteration = algorithm_parameters['max_chanin_long']
        self.step_size = algorithm_parameters["step_size"]
        self.dimension = len(vartype)
        self.vartype = vartype
        self.varbound = varbound
        self.agent_number = algorithm_parameters["agent_number"]
        self.answer_list = list()
        self.statistic = {"try": 0,
                          "failed_try": 0,
                          "acceped_try": 0,
                          "accepted_repeated": 0,
                          "accepted_new": 0}

    def report(self, count, total, status=''):
        bar_len = 50
        filled_len = int(round(bar_len * count / float(total)))

        percents = round(100.0 * count / float(total), 1)
        bar = '|' * filled_len + '_' * (bar_len - filled_len)

        sys.stdout.write('\r%s %s%s %s' % (bar, percents, '%', status))
        sys.stdout.flush()

    def initialize_agent(self):
        agents = list()
        for i in range(self.agent_number):
            data = list()
            for j in range(len(self.varbound)):
                low = self.varbound[j][0]
                hig = self.varbound[j][1]
                if self.vartype[j] == ["int"]:
                    rand = random.randint(low, hig)
                elif self.vartype[j] == ['float']:
                    rand = random.uniform(low, hig)
                data.append(rand)
            prob = self.goal_dist(data)
            agents.append(agent(data, self.iteration, prob))
        return agents

    def check_range(self, data):
        for i in range(len(self.varbound)):
            if data[i] < self.varbound[i][0] or data[i] > self.varbound[i][1]:
                return False
        return True

    def change_data(self, data):
        res = list()
        for i in range(len(self.vartype)):
            if self.vartype[i] == ["int"]:
                res.append(int(data[i]))
            else:
                res.append(data[i])
        return res

    def run_dom_mcmc(self):
        self.agents = self.initialize_agent()
        sigma = self.step_size
        T = self.iteration
        t = 0
        while t + 1 < T:
            self.report(t + 1, T)
            t = t + 1
            for i in range(len(self.agents)):
                self.statistic["try"] += 1
                t_star = list(np.random.normal(self.agents[i].theta[t - 1], sigma))
                t_star = self.change_data(t_star)
                rng_chk = self.check_range(t_star)
                p_new = self.goal_dist(t_star)
                p_old = self.agents[i].probablity[t - 1]
                if p_new == 0:
                    alpha = 0
                elif p_old == 0:
                    alpha = p_new
                else:
                    alpha = min(1, p_new / p_old)
                u = np.random.uniform(0, 1)
                if u > alpha and rng_chk:
                    self.agents[i].theta[t] = t_star
                    self.agents[i].probablity[t] = p_new
                    if t_star not in self.answer_list:
                        # print(t_star)
                        # self.answer_list.append(t_star)
                        self.agents[i].score += 1
                        # update statistic for inside point true
                        self.statistic["acceped_try"] += 1
                        # update statistic new point generation
                        if t_star not in self.answer_list:
                            self.answer_list.append(t_star)
                            self.statistic["accepted_new"] += 1
                        else:
                            self.statistic["accepted_repeated"] += 1
                else:
                    self.agents[i].theta[t] = self.agents[i].theta[t - 1]
                    self.agents[i].probablity[t] = self.agents[i].probablity[t - 1]
                    self.agents[i].score -= 1
                    # update statistic for ioutside point
                    self.statistic["failed_try"] += 1
            # update statistic new point generation
            self.search_guide(t)
        # save_statistic
        self.result_and_csv()
        return self.answer_list

    def search_guide(self, T):
        # agent with higher score and agent with lower considered in each step and weak agent trasmit to dense area which searched by high score agent
        # find maximum score agent and find minum score agent and set probablity and score and theta fore week
        # for tackle from local trap invitation to search area is restricted number of agent to contirbute (agent_area_num)
        min_score_obj = min(self.agents, key=attrgetter('score'))
        max_score_obj = max(self.agents, key=attrgetter('score'))
        max_indx = self.agents.index(max_score_obj)
        min_indx = self.agents.index(max_score_obj)
        if max_score_obj.threshold < 4:
            # exchange data of min_score_obj data with max_score_obj
            min_score_obj.theta[T] = max_score_obj.theta[T]
            max_score_obj.threshold += 1
            self.agents[max_indx] = max_score_obj
            self.agents[min_indx] = min_score_obj

    def result_and_csv(self):
        # save number of percentage of inside boundary and outside boundary point
        percision = self.statistic["acceped_try"] / self.statistic["try"]
        print("\npercision: ", percision)
        # print(self.statistic['accepted_new'])
        percentage_new_ponit = self.statistic["accepted_new"] / self.statistic["try"]
        print("percentage_new_point: ", percentage_new_ponit)
