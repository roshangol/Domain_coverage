import sys


class Coverage():
    path = list()

    def __init__(self, name):
        self.name = name
        self.path = list()

    def __enter__(self):
        Coverage.path = []
        sys.settrace(self.trace_calls)

    def __exit__(self, *args, **kwargs):
        # Stop tracing all events
        # sys.settrace =
        pass

    def trace_calls(self, frame, event, arg):
        # We want to only trace our call to the decorated function
        if event != 'call':
            return
        elif frame.f_code.co_name != self.name:
            return
        # return the trace function to use when you go into that
        # function call
        return self.trace_lines

    def trace_lines(self, frame, event, arg):
        # If you want to print local variables each line
        # keep the check for the event 'line'
        # If you want to print local variables only on return
        # check only for the 'return' event
        if event not in ['line', 'return']:
            return
        co = frame.f_code
        func_name = co.co_name
        line_no = frame.f_lineno
        filename = co.co_filename
        local_vars = frame.f_locals
        Coverage.path.append(line_no)
        # print ('  {0} {1} {2} locals: {3}'.format(func_name,
        #                                          event,
        #                                          line_no,
        #                                          local_vars))


def cover_decorator(func):
    def decorated_func(*args, **kwargs):
        end_path = list()
        with Coverage(func.__name__):
            return_value = func(*args, **kwargs)
            paths = Coverage.path[:-1]

            if paths[0] == 1:
                minus = int(paths[1])
                end_path.append(1)
                for i in paths[1:]:
                    end_path.append(int(i) - minus + 2)
            else:
                minus = int(paths[0])
                end_path.append(1)
                for i in paths:
                    end_path.append(int(i) - minus + 2)
            end_path.append(0)
        # print(end_path)
        return end_path, return_value
    return decorated_func
