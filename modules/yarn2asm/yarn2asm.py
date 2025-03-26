import sys
import re
import shlex
import shunting_yard
from pathlib import Path

NODE_END = 0
IN_HEADER = 1
IN_BODY = 2

fp = sys.argv[1]
ft = sys.argv[2]
filename = Path(fp).stem
blocks_stack = []
blocks = []
state = NODE_END

operator_asm = {
    "and": "AND_OPERATOR",
    "&&": "AND_OPERATOR",
    "or": "OR_OPERATOR",
    "||": "OR_OPERATOR",
    "xor": "XOR_OPERATOR",
    "^": "XOR_OPERATOR",

    "eq": "EQ_OPERATOR",
    "==": "EQ_OPERATOR",
    "is": "EQ_OPERATOR",
    "neq": "NEQ_OPERATOR",
    "!=": "NEQ_OPERATOR",

    "gt": "GT_OPERATOR",
    ">": "GT_OPERATOR",
    "lt": "LT_OPERATOR",
    "<": "LT_OPERATOR",
    "gte": "GTE_OPERATOR",
    ">=": "GTE_OPERATOR",
    "lte": "LTE_OPERATOR",
    "<=": "LTE_OPERATOR",

    "+": "ADD_OPERATOR",
    "-": "SUB_OPERATOR",

    "%": "MODULO_OPERATOR",
    "/": "DIVIDE_OPERATOR",
    "*": "MULTIPLY_OPERATOR",

    "!": "NEGATION_OPERATOR",
    "-u": "COMPL_OPERATOR",

}

def get_indentation(line):
    indentation = 0
    for c in line:
        if c == ' ':
            indentation += 1
        else:
            return indentation
    return indentation

def expr_to_asm(expr):
    output = ""
    tokens = shunting_yard.shunt(shunting_yard.tokenize(" ".join(expr)))    
    for token in tokens:
        if token in operator_asm.keys():
            output += f', {operator_asm[token]}'
        elif token[0] == '$':
            output += f', VARIABLE, LOW({token[1:]}), HIGH({token[1:]})'
        else:
            output += f', CONST_VALUE, {token}'
            
    return output


def parse_header_line(line):
    global node
    global state
    matches = re.findall("^title: *(.*) *$", line)
    if matches:
        blocks[blocks_stack[-1]]["title"] = matches[0]
        return

    matches = re.search("---", line)
    if matches:
        state = IN_BODY
        return

def parse_body_line(line):
    global node
    global state

    indentation = get_indentation(line)

    matches = re.findall("-> (.*)", line)
    if matches:
        if blocks[blocks_stack[-1]]["type"] == "choice" and blocks[blocks_stack[-1]]["indentation"] == indentation:
            blocks_stack.pop()

        blocks[blocks_stack[-1]]["lines"].append({"type":"CHOICE_ENTRY", "target":f'.block_{len(blocks)}', "value":matches[0]})
        blocks_stack.append(len(blocks))
        blocks.append({"type":"choice", "title":f'block_{len(blocks)}', "indentation":indentation, "lines":[]})
        return

    matches = re.search("===", line)
    if matches:
        blocks_stack.clear()
        state = NODE_END
        return

    matches = re.findall("<<(.*)>>", line)
    if matches:
        cmd_args = shlex.split(matches[0])

        if cmd_args[0] in ["elseif", "else", "endif"]:
            while blocks[blocks_stack[-1]]["type"] != "condition":
                blocks_stack.pop()
            blocks_stack.pop()

        if cmd_args[0] in ["if", "else", "elseif"]:
            blocks[blocks_stack[-1]]["lines"].append({"type":"COMMAND", "target":f'.block_{len(blocks)}', "value":matches[0]})
            blocks_stack.append(len(blocks))
            blocks.append({"type":"condition", "title":f'block_{len(blocks)}', "indentation":indentation, "lines":[]})
        elif cmd_args[0] == "endif":
            pass
        else:
            blocks[blocks_stack[-1]]["lines"].append({"type":"COMMAND", "value":matches[0]})
        return

    text = line.strip()
    matches = re.search(r'^([^:]*)\s*:\s(.*)$', text)
    if matches:
        blocks[blocks_stack[-1]]["lines"].append({"type":"TXT", "character":matches.groups()[0], "value":matches.groups()[1]})
    else:
        blocks[blocks_stack[-1]]["lines"].append({"type":"TXT", "character":None, "value":text})

def print_line(line, f):
    if line["type"] == "COMMAND":
        cmd_args = shlex.split(line["value"])
        print(f'  db {line["type"]}_{cmd_args[0].upper()}', end='', file=f)
        if cmd_args[0] in ["declare", "set"]:
            print(f', {cmd_args[1].strip('$')}', end='', file=f)
            print(expr_to_asm(cmd_args[3:]), end='', file=f)
            print(', COMMAND_END', file=f)
        elif cmd_args[0] in ["if", "elseif"]:
            print(f', LOW({line["target"]}), HIGH({line["target"]})', end='', file=f)
            print(expr_to_asm(cmd_args[1:]), end='', file=f)
            print(', COMMAND_END', file=f)
        elif cmd_args[0] in ["else"]:
            print(f', LOW({line["target"]}), HIGH({line["target"]})', file=f)
        elif cmd_args[0] in ["endif"]:
            print("", file=f)
        elif cmd_args[0] == "jump":
            print(f', BANK({filename}_{cmd_args[1]}), LOW({filename}_{cmd_args[1]}), HIGH({filename}_{cmd_args[1]})', file=f)
        else:
            for arg in cmd_args[1:]:
                print(f', {arg}', end='', file=f)
            print(', COMMAND_END', file=f)
    elif line["type"] == "CHOICE_ENTRY":
        print(f'  db {line["type"]}, LOW({line["target"]}), HIGH({line["target"]}), \"{line["value"].strip()}<END>\"', file=f)
    elif line["type"] == "CHOICE_END":
        print(f'  db {line["type"]}', file=f)
    elif line["type"] == "TXT":
        if line["character"] != None:
            print(f'  db {line["type"]}, \"<CHARACTER>\", {line["character"].replace(' ', '_')}, \"{line["value"].strip()}<END>\"', file=f)
        else:
            print(f'  db {line["type"]}, \"{line["value"].strip()}<END>\"', file=f)
    else:
        print("unhandled line type")
        exit


with open(fp, 'r') as f:
    for line in f:
        if state == NODE_END and not line.isspace():
            state = IN_HEADER
            blocks_stack.append(len(blocks))
            blocks.append({"type":"node", "title":None, "lines":[], "indentation":0})

        if state == IN_HEADER:
            parse_header_line(line)
        elif state == IN_BODY:
            parse_body_line(line)

if len(blocks_stack) > 0:
    print("todo error message, stack not empty at end", len(blocks_stack))
    exit

with open(ft, 'w') as f:
    print(f'Print to : {ft}')  # Python 3.x
    previous_block = None

    print('include "yarn.inc"\n', file=f)

    for block in blocks:
        if block["type"] == "node":
            if previous_block != None:
                print("", file=f)

            print(f'SECTION "{filename}.{block["title"]}", ROMX', file=f)
            print(f'{filename}_{block["title"]}::', file=f)

            for line in block["lines"]:
                print_line(line, f)
                
            print("  db RETURN", file=f)
        else:
            print(f'.{block["title"]}', file=f)

            for line in block["lines"]:
                print_line(line, f)

            print("  db RETURN", file=f)
        previous_block = block