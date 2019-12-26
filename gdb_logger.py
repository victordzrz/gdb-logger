import re
import json
from pyparsing import *
from pygdbmi.gdbcontroller import GdbController
from pprint import pprint


def _get_value_grammar(debug=False):
    ParserElement.enablePackrat()

    def my_parse_action(element, name):
        def parse_action(tokens):
            print('-----'+name+'-----')
            print(tokens.dump())
            print()
        element.setParseAction(parse_action)

    lb = Literal('{').suppress()
    rb = Literal('}').suppress()
    integer = pyparsing_common.signed_integer
    real = pyparsing_common.real
    number = real | integer
    string = Word(alphanums)
    variable = pyparsing_common.identifier

    right_hand = Forward()
    eq = Literal('=').suppress()
    key_value = Dict(Group(variable + eq + right_hand))
    dict_exp = lb + Dict(delimitedList(key_value)) + rb

    list_of_dict = delimitedList(Group(dict_exp))
    list_of_int = delimitedList(number)
    list_of_string = delimitedList(string)
    list_exp = Forward()
    list_of_list = delimitedList(list_exp)

    any_list = list_of_list | list_of_dict | list_of_string | list_of_int
    list_exp <<= (lb + any_list + rb)

    right_hand <<= list_exp | dict_exp | number | string
    if debug:
        my_parse_action(number, 'number')
        my_parse_action(right_hand, 'right_hand')
        my_parse_action(key_value, 'key_value')
        my_parse_action(list_of_dict, 'list_of_dict')
    return right_hand


VALUE_GRAMMAR = _get_value_grammar()


class BaseBreakpoint():
    def __init__(self):
        self.id = None

    def to_gdb(self):
        pass

    def insert(self, gdb_controller):
        gdb_controller.run_gdbmi(self.to_gdb())
        responses = gdb_controller.get_responses_until([('done', 'result')])
        while responses[-1]['payload'] is None:
            responses = gdb_controller.get_responses_until(
                [('done', 'result')])
        self.id = responses[-1]['payload']['bkpt']['number']


class LineBreakpoint(BaseBreakpoint):

    def __init__(self, filespec, line):
        self.file = filespec
        self.line = line

    def to_gdb(self):
        return '-break-insert --source {filespec} --line {line}'.format(filespec=self.file, line=self.line)


class FunctionBreakpoint(BaseBreakpoint):
    def __init__(self, filespec, function_name):
        self.file = filespec
        self.function_name = function_name

    def to_gdb(self):
        return '-break-insert --source {filespec} --function {function}'.format(filespec=self.file, function=self.function_name)


class LogPoint():

    def __init__(self, alias, expression):
        self.alias = alias
        self.expression = expression
        self.value = None

    def to_gdb(self):
        return '-data-evaluate-expression {expression}'.format(expression=self.expression)

    def populate(self, gdb_controller):
        gdb_controller.run_gdbmi(self.to_gdb())
        responses = gdb_controller.get_responses_until([('done', 'result')])
        self.value = LogPoint._parse_payload(responses[-1]['payload']['value'])

    @staticmethod
    def _parse_payload(payload):
        result = VALUE_GRAMMAR.parseString(payload)
        if '{' in payload:
            if '=' in payload:
                return result.asDict()
            else:
                return result.asList()
        return result.asList()[0]


class GdbWrapper():
    def __init__(self):
        self.gdbmi = GdbController()
        self.verbose = False

    def run_gdbmi(self, command, extra_time=0):
        if self.verbose:
            print(command)
        self.gdbmi.write(command, timeout_sec=extra_time, read_response=False)

    def yield_responses(self):
        responses = []
        while True:
            if len(responses) > 0:
                yield responses.pop()
            else:
                new_responses = self.gdbmi.get_gdb_response(
                    timeout_sec=0, raise_error_on_timeout=False)
                if new_responses:
                    responses.extend(new_responses)

    def get_responses_until(self, message_type_list):
        responses = []
        for response in self.yield_responses():
            responses.append(response)
            if self.verbose:
                pprint(response)
            if (response['message'], response['type']) in message_type_list:
                return responses

    def load_executable(self, path_to_executable):
        self.run_gdbmi('-file-exec-and-symbols ' +
                       path_to_executable, extra_time=5)
        self.insert_breakpoint(FunctionBreakpoint('main.cpp', 'main'))
        self.exec_run()
        self.get_responses_until([('stopped', 'notify')])

    def insert_breakpoint(self, breakpoint):
        breakpoint.insert(self)

    def populate_logpoint(self, logpoint):
        logpoint.populate(self)

    def exec_continue(self):
        self.run_gdbmi('-exec-continue')

    def exec_finish(self):
        self.run_gdbmi('-exec-finish')

    def exec_next(self):
        self.run_gdbmi('-exec-next')

    def exec_run(self):
        self.run_gdbmi('-exec-run')

    def run_until_breakpoint(self):
        self.exec_continue()
        self.get_responses_until([('stopped', 'notify')])


def main():
    gdb = GdbWrapper()
    gdb.load_executable('./toy-c/build/toy_c')
    lb = LineBreakpoint('main.cpp', 7)
    lb2 = LineBreakpoint('main.cpp', 5)
    lb2 = LineBreakpoint('main.cpp', 12)
    point = LogPoint('input', 'input.params_array')
    point2 = LogPoint('i', 'i')
    point3 = LogPoint('array', 'input.array')
    gdb.insert_breakpoint(lb)
    gdb.insert_breakpoint(lb2)
    gdb.run_until_breakpoint()
    gdb.run_until_breakpoint()
    gdb.run_until_breakpoint()
    for i in range(0, 900):
        gdb.populate_logpoint(point)
        gdb.populate_logpoint(point2)
        print(point2.value)
        # gdb.populate_logpoint(point3)
        gdb.run_until_breakpoint()


if __name__ == "__main__":
    main()
