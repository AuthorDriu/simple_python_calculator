from icecream import ic
from sys import exit, argv
from enum import Enum

"""
Флаги для разного вывода:
    --log           выводит логи
    --test_tree     проводит тест простого дерева
    --test_lexer    проводит тест лексера
"""

ic.disable()

VARIABLES = {}

class Variable:
    def __init__(self, key):
        self.key = key

def assign(x, y):
    VARIABLES[x] = y
    return VARIABLES[x]

def get(x):
    if isinstance(x, float) or isinstance(x, int):
        return x
    if x not in VARIABLES.keys():
        VARIABLES[x] = 0
    return VARIABLES[x]

# Класс оператора
class Operator:
    def __init__(self, lambda_f):
        self.right: Operator = None
        self.left: Operator = None
        self.action = lambda_f

    def calc(self):
        ic()
        x1 = None
        x2 = None
        if ic(isinstance(self.left, Operator)):
            x1 = ic(self.left.calc())
        elif ic(isinstance(self.left, float) or isinstance(self.left, int)):
            x1 = ic(self.left)
        elif ic(isinstance(self.left, Variable)):
            x1 = ic(self.left.key)
        else:
            raise Exception("\033[31mLeft operand type is not supported <{}>\033[0m".format(type(self.left)))
        
        if ic(isinstance(self.right, Operator)):
            x2 = ic(self.right.calc())
        elif ic(isinstance(self.right, float) or isinstance(self.right, int)):
            x2 = ic(self.right)
        elif ic(isinstance(self.right, Variable)):
            x2 = ic(self.right.key)
        else:
            raise Exception("\033[31mRight operand type is not supported <{}>\033[0m".format(type(self.right)))

        return self.action(x1, x2)

class TokenType(Enum):
    OP_PLUS = 1,
    OP_MINUS = 2,
    OP_MUL = 3,
    OP_DIV = 4,
    OP_POW = 5,
    VAR = 6,
    NUM = 7,
    OPEN = 8,
    CLOSE = 9,
    ASSIGN = 10,

    SIMPLE_EXPR = 11,

    def get_token_name(token):
        tt = token.tt
        if tt == TokenType.OP_PLUS: return "OP_PLUS"
        if tt == TokenType.OP_MINUS: return "OP_MINUS"
        if tt == TokenType.OP_MUL: return "OP_MUL"
        if tt == TokenType.OP_DIV: return "OP_DIV"
        if tt == TokenType.OP_POW: return "OP_POW"
        if tt == TokenType.VAR: return "VAR"
        if tt == TokenType.NUM: return "NUM"
        if tt == TokenType.OPEN: return "OPEN"
        if tt == TokenType.CLOSE: return "CLOSE"
        if tt == TokenType.ASSIGN: return "ASSIGN"
        if tt == TokenType.SIMPLE_EXPR: return "SIMPLE_EXPR"
        return "???"

class Token:
    def __init__(self):
        self.tt = None
        self.value = None

class Lexer:
    def __init__(self, data: str):
        self.d = data
        self.token_list = []

    def gettl(self):
        oper_list = ("+-*=/^()", (TokenType.OP_PLUS, TokenType.OP_MINUS, TokenType.OP_MUL, TokenType.ASSIGN,
                                 TokenType.OP_DIV, TokenType.OP_POW, TokenType.OPEN, TokenType.CLOSE))
        value: str = ""
        for c in self.d:
            if c in oper_list[0] or c == " ":
                if value == "" and c == " ": continue
                
                # Добавление токена операнда
                if value != "":
                    self.token_list.append(Token())
                    self.token_list[-1].tt = TokenType.NUM if value.isnumeric() else TokenType.VAR
                    self.token_list[-1].value = value
                    value = ""
                    ic(self.token_list[-1].tt, self.token_list[-1].value)

                # Добавление токена оператора
                if c != " ":
                    self.token_list.append(Token())
                    self.token_list[-1].tt = ic(oper_list[1][ic(oper_list[0].find(ic(c)))])
                continue
            value += c
        
        if ic(value != ""):
            self.token_list.append(Token())
            self.token_list[-1].tt = TokenType.NUM if value.isnumeric() else TokenType.VAR
            self.token_list[-1].value = value
        
        return self.token_list

# Парсер. Возвращает дерево
class Parser:

    def __init__(self, token_list):
        self.tl = token_list

    def simplify(self):
            simple_expr = []
            to_simplify = []
            
            n = 0
            simpifying = False
            for tok in self.tl:
                ic(simple_expr, to_simplify)
                if tok.tt == TokenType.OPEN:
                    n += 1
                    if n == 1:
                        simpifying = True
                        continue
                if tok.tt == TokenType.CLOSE:
                    n -= 1
                    if n == 0:
                        simpifying = False
                        stok = Token()
                        stok.tt = TokenType.SIMPLE_EXPR
                        stok.value = Parser(to_simplify).simplify()
                        simple_expr.append(stok)
                        to_simplify = []
                        continue
                if simpifying:
                    to_simplify.append(tok)
                else:
                    simple_expr.append(tok)
            return simple_expr

    def create_node(self, left, right, lambda_f):
        oper = Operator(lambda_f)
        
        if isinstance(left, list) and len(left) == 1:
            left = left[0]
        if isinstance(right, list) and len(right) == 1:
            right = right[0]

        if isinstance(left, list):
            oper.left = Parser(left).parse()
        elif left.tt == TokenType.NUM:
            oper.left = float(left.value)
        elif left.tt == TokenType.VAR:
            oper.left = Variable(key=left.value)
        elif left.tt == TokenType.SIMPLE_EXPR:
            oper.left = Parser(left.value).parse()
        
        if isinstance(right, list):
            oper.right = Parser(right).parse()
        elif right.tt == TokenType.NUM:
            oper.right = float(right.value)
        elif right.tt == TokenType.VAR:
            oper.right = Variable(key=right.value)
        elif right.tt == TokenType.SIMPLE_EXPR:
            oper.right = Parser(right.value).parse()
        return oper
    
    def parse(self):
        ic()
        simplifyed_tl = self.simplify()
        if len(simplifyed_tl) == 1:
            tok = Token()
            tok.tt = TokenType.NUM
            tok.value = 0
            return self.create_node(simplifyed_tl[0], tok, lambda x, y: get(x) + get(y))

        # Проверка на присвоение 
        for i, tok in enumerate(simplifyed_tl):
            if tok.tt == TokenType.ASSIGN:
                return self.create_node(simplifyed_tl[:i:], simplifyed_tl[i+1::], lambda x, y: assign(x, get(y)))

        # Проверка на операции с приоритетом 1 (+, -)
        for i, tok in enumerate(simplifyed_tl):
            if tok.tt == TokenType.OP_PLUS:
                return self.create_node(simplifyed_tl[:i:], simplifyed_tl[i+1::], lambda x, y: get(x) + get(y))
            if tok.tt == TokenType.OP_MINUS:
                return self.create_node(simplifyed_tl[:i:], simplifyed_tl[i+1::], lambda x, y: get(x) - get(y))
        
        # Проверка на операции с приоритетом 2 (*, /)
        for i, tok in enumerate(simplifyed_tl):
            if tok.tt == TokenType.OP_MUL:
                return self.create_node(simplifyed_tl[:i:], simplifyed_tl[i+1::], lambda x, y: get(x) * get(y))
            if tok.tt == TokenType.OP_DIV:
                return self.create_node(simplifyed_tl[:i:], simplifyed_tl[i+1::], lambda x, y: get(x) / get(y))
        
        # Проверка на операции с приоритетом 3 (^)
        for i, tok in enumerate(simplifyed_tl):
            if tok.tt == TokenType.OP_POW:
                return self.create_node(simplifyed_tl[:i:], simplifyed_tl[i+1::], lambda x, y: get(x) ** get(y))
            

def __test_tree():
    ic("Testing tree \"5 + 76 / (33 + 43)\"")

    root: Operator = Operator(lambda x, y: x + y)
    root.left = 5
    root.right = Operator(lambda x, y: x / y)
    root.right.right = 76
    root.right.left = Operator(lambda x, y: x + y)
    root.right.left.right = 33
    root.right.left.left = 43

    print(ic(root.calc()))

def __test_lexer():
    ic("Testing lexer \"5 + 76 / (33 + 43)\"")
    for lex in Lexer("5 + 76 / (33 + 43)").gettl():
        print(TokenType.get_token_name(lex), end=" ")
    print()
    ic("Testing lexer \"x1+ 32 ^ (10 * x2)\"")
    for lex in Lexer("x1+ 32 ^ (10 * x2)").gettl():
        print(TokenType.get_token_name(lex), end=" ")
    print()
    ic("Testing lexer \"x72 = a * 32\"")
    for lex in Lexer("x72 = a * 32").gettl():
        print(TokenType.get_token_name(lex), end=" ")
    print()

def __test_parser_simplifier():
    ic("Testing simplifying \"10 + 15 * (3 * 7 - (3 + x1))\"")
    token_list = Lexer("10 + 15 * (3 * 7 - (3 + x1))").gettl()
    print("10 + 15 * (3 * 7 - (3 + x1))")
    print(ic(*[TokenType.get_token_name(tok) for tok in Parser(token_list).simplify()]))
    def print_simple(simple):
        print(ic(*[TokenType.get_token_name(tok) for tok in simple.value]))
        for tok in simple.value:
            if tok.tt == TokenType.SIMPLE_EXPR:
                print_simple(tok)
    for tok in Parser(token_list).simplify():
            if tok.tt == TokenType.SIMPLE_EXPR:
                print_simple(tok)

if '--log' in argv:
    ic.enable()
if "--test_tree" in argv:
    __test_tree()
    exit(0)
elif "--test_lexer" in argv:
    __test_lexer()
    exit(0)
elif "--test_simplifying" in argv:
    __test_parser_simplifier()
    exit(0)
else:
    try:
        while True:
            expression = input(">>> ")
            token_list = Lexer(expression).gettl()
            root = Parser(token_list).parse()
            print(root.calc())
    except KeyboardInterrupt:
        print("Exiting...")
        exit(1)
