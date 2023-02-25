#! /usr/bin/python3

import sys, os

class BFError(Exception):
    pass

OPERATIONS = "<>+-.,[]"

def standard_output(one_byte: int):
    print(bytearray([one_byte]).decode(), end="")

def standard_input() -> int:
    return os.read(sys.stdin.fileno(), 1)[0]

def list_input(l: list) -> int:
    return l.pop()

def execute(code: str, memsize=30000, strict_overflow=False, out=standard_output, inp=standard_input, callback=lambda memory, datapointer, instrpointer: None):

    brackets_depth = [-1]*len(code)
    current_depth = 0
    for i, c in enumerate(code):
        if c == '[':
            brackets_depth[i] = current_depth
            current_depth += 1
        if c == ']':
            current_depth -= 1
            brackets_depth[i] = current_depth
    if current_depth != 0:
        raise BFError("-: Brackets instructions ('[' and ']') does not match.")

    memory = bytearray([0]*memsize)
    datapointer = 0
    instrpointer = 0

    next_closing_cache = [-1]*len(code)
    prev_opening_cache = [-1]*len(code)

    callback(memory, datapointer, instrpointer)

    while 0 <= instrpointer <= len(code)-1:
        op = code[instrpointer]
        if op == '>':
            if datapointer+1 <= len(memory)-1:
                datapointer += 1
            elif strict_overflow:
                raise BFError(f"{instrpointer+1}: Cannot move data pointer forward, memory too small.")
        if op == '<':
            if datapointer-1 >= 0:
                datapointer -= 1
            elif strict_overflow:
                raise BFError(f"{instrpointer+1}: Cannot move data pointer backward when it's on the first cell.")
        if op == '+':
            if memory[datapointer] <= 254:
                memory[datapointer] += 1
            elif strict_overflow:
                raise BFError(f"{instrpointer+1}: Cannot increment 255.")
        if op == '-':
            if memory[datapointer] >= 1:
                memory[datapointer] -= 1
            elif strict_overflow:
                raise BFError(f"{instrpointer+1}: Cannot decrement 0.")
        if op == '.':
            out(memory[datapointer])
        if op == ',':
            val = inp()
            if 0 <= val <= 255:
                memory[datapointer] = val
            elif strict_overflow:
                raise BFError(f"{instrpointer+1}: Read number is too large to form a byte.")

        if op == '[':
            if memory[datapointer] == 0:
                if next_closing_cache[instrpointer] != -1:
                    instrpointer = next_closing_cache[instrpointer]
                else:
                    instrpointer_ = instrpointer
                    while code[instrpointer_] != ']' or brackets_depth[instrpointer_] != brackets_depth[instrpointer]:
                        instrpointer_ += 1
                    next_closing_cache[instrpointer] = instrpointer_
                    prev_opening_cache[instrpointer_] = instrpointer
                    instrpointer = instrpointer_
                instrpointer -= 1
        if op == ']':
            if memory[datapointer] != 0:
                if prev_opening_cache[instrpointer] != -1:
                    instrpointer = prev_opening_cache[instrpointer]
                else:
                    instrpointer_ = instrpointer
                    while code[instrpointer_] != '[' or brackets_depth[instrpointer_] != brackets_depth[instrpointer]:
                        instrpointer_ -= 1
                    prev_opening_cache[instrpointer] = instrpointer_
                    next_closing_cache[instrpointer_] = instrpointer
                    instrpointer = instrpointer_
                instrpointer -= 1
        
        instrpointer += 1
        
        callback(memory, datapointer, instrpointer)


def parse_error(err):
    err = str(err)
    i = 0
    while err[i] in "0123456789":
        i += 1
    if i == 0:
        return None, err[2:].strip()
    else:
        return int(err[:i].strip()), err[i+1:].strip()

if __name__ == "__main__":

    if len(sys.argv) <= 1 or sys.argv[1] == "--help":
        print(f"Filename not specified. Usage: {sys.argv[0]} <filename>")
        exit(1)
    
    filename = sys.argv[1]

    try:
        with open(filename, "r") as f:
            code = f.read()
    except FileNotFoundError:
        print(f"File {filename} not found.")
        exit(1)

    try:
        execute(code)
    except BFError as err:
        num, text = parse_error(err)
        if num is None:
            print(f"Error: {text}")
        else:
            print(f"Error: Character {num}: {text}")
        exit(1)
