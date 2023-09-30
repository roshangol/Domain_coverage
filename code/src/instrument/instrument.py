import sys
import inspect
from .instrumentation import instrument_extraction


def code_instrumentation(input_path, input_file, function, output_path):
    sys.path.append(input_path)
    exec(f"from {input_file} import {function}")
    source = inspect.getsource(eval(f"{function}"))
    instrument_extraction(source, input_file, function, output_path)
