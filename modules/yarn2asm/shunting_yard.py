# based on gist FROM ollybritton https://gist.github.com/ollybritton/3ecdd2b28344b0b25c547cbfcb807ddc

# Shunting-yard Algorithm implemented in Python.
# Takes a string using infix notation and outputs it in postfix.
# For example: (5+4)*8 -> 5 4 + 8 *

import re
from collections import namedtuple

opinfo = namedtuple('Operator', 'precedence associativity')
operator_info = {
    # Brackets handled separately
    # 0 = low, 5 = high
    
    "and": opinfo(0, "L"),
    "&&": opinfo(0, "L"),
    "or": opinfo(0, "L"),
    "||": opinfo(0, "L"),
    "xor": opinfo(0, "L"),
    "^": opinfo(0, "L"),

    "eq": opinfo(1, "L"),
    "==": opinfo(1, "L"),
    "is": opinfo(1, "L"),
    "neq": opinfo(1, "L"),
    "!=": opinfo(1, "L"),

    "gt": opinfo(2, "L"),
    ">": opinfo(2, "L"),
    "lt": opinfo(2, "L"),
    "<": opinfo(2, "L"),
    "gte": opinfo(2, "L"),
    ">=": opinfo(2, "L"),
    "lte": opinfo(2, "L"),
    "<=": opinfo(2, "L"),

    "+": opinfo(3, "L"),
    "-": opinfo(3, "L"),

    "%": opinfo(4, "L"),
    "/": opinfo(4, "L"),
    "*": opinfo(4, "L"),

    "!": opinfo(5, "R"),
    "-u": opinfo(5, "R"),

}


def tokenize(input_string):
    matches = re.findall(r'and|or|xor|&&|\|\||eq|==|is|neq|!=|gt|lt|gte|lte|<=|>=|[\(\)+\-%\/*>=<^]|[$A-Za-z0-9]+', input_string)

    return matches


def shunt(tokens):
    tokens += ['end']
    previous_token = None
    operators = []
    output = []

    while len(tokens) != 1:
        current_token = tokens.pop(0)

        # if current_token == '-' and (len(output) == 0 or output[-1] in operator_info or len(operators) > 0 and operators[-1] == '('):
        if current_token == '-' and (previous_token == None or previous_token == '(' or previous_token in operator_info.keys()):
                # print("unary minus -u")
                operators.append("-u")

        elif current_token in operator_info.keys():
            # Is an operator
            # print("op", current_token)

            while True:
                if len(operators) == 0:
                    break

                satisfied = False

                if operators[-1] not in ["(", ")"]:
                    if operator_info[operators[-1]].precedence > operator_info[current_token].precedence:
                        # print("operator at top has greater precedence")
                        satisfied = True

                    elif operator_info[operators[-1]].precedence == operator_info[current_token].precedence:
                        if operator_info[operators[-1]].associativity == "left":
                            # print("equal precedence and has left associativity")
                            satisfied = True

                satisfied = satisfied and operators[-1] != "("

                if not satisfied:
                    break

                output.append(operators.pop())

            operators.append(current_token)

        elif current_token.isalnum():
            # Is a number or const
            # print("number", current_token)
            output.append(current_token)

        elif current_token[0] == '$':
            # Is a variable
            # print("var", current_token)
            output.append(current_token)

        elif current_token == "(":
            # Is left bracket
            # print("left", current_token)
            operators.append(current_token)

        elif current_token == ")":
            # Is right bracket
            # print("right", current_token)

            while True:
                if len(operators) == 0:
                    break

                if operators[-1] == "(":
                    break

                output.append(operators.pop())

            if len(operators) != 0 and operators[-1] == "(":
                operators.pop()

        previous_token = current_token

    output.extend(operators[::-1])

    return output


# tokens = tokenize("3 + 4 * 2 / ( 1 - 5 ) ^ 2 ^ 3")
# tokens = tokenize("-3 + 4 * -2 / - (- 1 - 5 )")
# tokens = tokenize("$partyHats > 0 and $partyHats <= 2")
# tokens = tokenize("100 + 200 / 10 - 3 * 10")
# print(" ".join(shunt(tokens)))
# Outputs 3 4 2 1 5 - 2 3 ^ ^ / * +

# devrait être 3 4 2 * 1 5 - / +