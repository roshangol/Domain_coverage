from src import domain_extraction


new = domain_extraction('C:/Users/Administrator/Desktop/domain/code/example', "expint.py", "expint", "C:/Users/Administrator/Desktop/domain/code/example/output")

new.boundary_point([1, 2, 3, 4, 5, 6, 7, 10, 13, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 21, 22, 23, 24, 25, 26, 27, 28, 29, 0], [11, 9.510431],
	algorithm_parameters={"length": [100, 150, 200, 50, 20, 30, 40, 60, 70, 80, 10, 5, 300], "budget": 100})
