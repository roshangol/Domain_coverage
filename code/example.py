from src import domain_extraction
"""
new = domain_extraction('C:/Users/Administrator/Desktop/domain/code/example', "expint.py", "expint", "C:/Users/Administrator/Desktop/domain/code/example/output")

# new.report()

# print(new.simple_pathes)
# print(new.prime_pathes)
# print(new.prime_coverage)
# print(new.prime_req)


# new.extract_pdf()
# new.show_graph()
# new.code_instrument()

# extract PUT's path information like simple path, prime path and minimum execution path that cover all prime path and their requirement's

# new.extract_prime_path()
# new.extract_simple_path()
# new.extract_prime_path_coverage_bruteforce()
# new.extract_prime_path_coverage_setcover()



new.mcmc_domain([1, 2, 3, 4, 5, 6, 7, 10, 13, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 21, 22, 23, 24, 25, 26, 27, 28, 29, 0], algorithm_parameters={'test_budget': 600,
                                                 'max_chanin_long': 1500,
                                                 'agent_number': 15,
                                                 'step_size': 3})
"""
new = domain_extraction('C:/Users/Administrator/Desktop/domain/code/example', "gammaq.py", "gammaq", "C:/Users/Administrator/Desktop/domain/code/example/output")

new.mcmc_domain([1, 2, 3, 5, 6, 7, 8, 10, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 16, 17, 18, 19, 20, 21, 22, 16, 23, 0], algorithm_parameters={'test_budget': 600,
                                                 'max_chanin_long': 1500,
                                                 'agent_number': 15,
                                                 'step_size': 3})

