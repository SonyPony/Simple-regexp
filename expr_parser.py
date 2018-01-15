# coding=utf-8
from fa_generator import FAGenerator, FiniteAutomat
from lexer import Lexer, TokenType, Token
from expr import ExprTokenType, ExprPrecedence, Expression


class UnknownTokenComparisonError(Exception):
    pass

class TokenMismatchError(Exception):
    pass

class Parser:
    def _update_precedence_table(self, table):
        self._precedence_table = dict()
        convert_func = lambda x: ExprTokenType(x) if x == "$" else ExprPrecedence(x) if x in ("<", ">", "=") else TokenType(x)

        for row_key, row in table.items():
            e_key = convert_func(row_key)
            self._precedence_table[e_key] = dict()

            for col, prec in row.items():
                self._precedence_table[e_key][convert_func(col)] = convert_func(prec)


    def __init__(self, source=""):
        self._lexer = Lexer(source)

        # [top][input]
        self._precedence_table = {
            TokenType.META_CONCANATE: {
                TokenType.META_CONCANATE:       ExprPrecedence.REDUCE,
                TokenType.META_OR:              ExprPrecedence.SHIFT,
                TokenType.META_QUANTIFIER_0_N:  ExprPrecedence.SHIFT,
                TokenType.LEFT_BRACKET:         ExprPrecedence.SHIFT,
                TokenType.RIGHT_BRACKET:        ExprPrecedence.REDUCE,
                TokenType.IDENTIFIER:           ExprPrecedence.SHIFT,
                ExprTokenType.META_DOLAR:       ExprPrecedence.REDUCE
            },

            TokenType.META_OR: {
                TokenType.META_CONCANATE:       ExprPrecedence.REDUCE,
                TokenType.META_OR:              ExprPrecedence.REDUCE,
                TokenType.META_QUANTIFIER_0_N:  ExprPrecedence.SHIFT,
                TokenType.LEFT_BRACKET:         ExprPrecedence.SHIFT,
                TokenType.RIGHT_BRACKET:        ExprPrecedence.REDUCE,
                TokenType.IDENTIFIER:           ExprPrecedence.SHIFT,
                ExprTokenType.META_DOLAR:       ExprPrecedence.REDUCE
            },

            TokenType.META_QUANTIFIER_0_N: {
                TokenType.META_CONCANATE:       ExprPrecedence.REDUCE,
                TokenType.META_OR:              ExprPrecedence.REDUCE,
                TokenType.META_QUANTIFIER_0_N:  ExprPrecedence.REDUCE,
                TokenType.LEFT_BRACKET:         ExprPrecedence.SHIFT,
                TokenType.RIGHT_BRACKET:        ExprPrecedence.REDUCE,
                TokenType.IDENTIFIER:           ExprPrecedence.REDUCE,
                ExprTokenType.META_DOLAR:       ExprPrecedence.REDUCE
            },

            TokenType.LEFT_BRACKET: {
                TokenType.META_CONCANATE:       ExprPrecedence.SHIFT,
                TokenType.META_OR:              ExprPrecedence.SHIFT,
                TokenType.META_QUANTIFIER_0_N:  ExprPrecedence.SHIFT,
                TokenType.LEFT_BRACKET:         ExprPrecedence.SHIFT,
                TokenType.RIGHT_BRACKET:        ExprPrecedence.SAME,
                TokenType.IDENTIFIER:           ExprPrecedence.SHIFT,
                ExprTokenType.META_DOLAR:       ExprPrecedence.NONE
            },

            TokenType.RIGHT_BRACKET: {
                TokenType.META_CONCANATE:       ExprPrecedence.REDUCE,
                TokenType.META_OR:              ExprPrecedence.REDUCE,
                TokenType.META_QUANTIFIER_0_N:  ExprPrecedence.REDUCE,
                TokenType.LEFT_BRACKET:         ExprPrecedence.REDUCE,
                TokenType.RIGHT_BRACKET:        ExprPrecedence.REDUCE,
                TokenType.IDENTIFIER:           ExprPrecedence.REDUCE,
                ExprTokenType.META_DOLAR:       ExprPrecedence.REDUCE
            },

            TokenType.IDENTIFIER: {
                TokenType.META_CONCANATE:       ExprPrecedence.REDUCE,
                TokenType.META_OR:              ExprPrecedence.REDUCE,
                TokenType.META_QUANTIFIER_0_N:  ExprPrecedence.REDUCE,
                TokenType.LEFT_BRACKET:         ExprPrecedence.SHIFT,
                TokenType.RIGHT_BRACKET:        ExprPrecedence.REDUCE,
                TokenType.IDENTIFIER:           ExprPrecedence.NONE,
                ExprTokenType.META_DOLAR:       ExprPrecedence.REDUCE
            },

            ExprTokenType.META_DOLAR: {
                TokenType.META_CONCANATE:       ExprPrecedence.SHIFT,
                TokenType.META_OR:              ExprPrecedence.SHIFT,
                TokenType.META_QUANTIFIER_0_N:  ExprPrecedence.SHIFT,
                TokenType.LEFT_BRACKET:         ExprPrecedence.SHIFT,
                TokenType.RIGHT_BRACKET:        ExprPrecedence.NONE,
                TokenType.IDENTIFIER:           ExprPrecedence.SHIFT,
                ExprTokenType.META_DOLAR:       ExprPrecedence.NONE
            },
        }

    @staticmethod
    def top_term(stack: list):
        stack_size = len(stack)
        for i, expr in enumerate(reversed(stack)):
            if isinstance(expr, Token) or expr == ExprTokenType.META_DOLAR:
                return expr, stack_size - i -1

    @staticmethod
    def check_token(token, expected_token):
        def _(token, expected_token):
            if isinstance(expected_token, TokenType):
                return isinstance(token, Token) and token.type == expected_token
            if expected_token == Expression:
                return isinstance(token, Expression)
            if isinstance(expected_token, ExprPrecedence):
                return token == expected_token
            else:
                raise UnknownTokenComparisonError
        try:
            if not _(token, expected_token):
                raise TokenMismatchError
            return token
        except UnknownTokenComparisonError:
            raise TokenMismatchError

    @staticmethod
    def reduce(stack: list, new_expr):
        r_stack = reversed(stack)
        for t in r_stack:
            if t == ExprPrecedence.SHIFT:
                break
            stack.pop()
        stack.pop()
        stack.append(new_expr)

    def rule_id(self, stack):
        it = iter(reversed(stack))

        try:
            identifier = Parser.check_token(next(it), TokenType.IDENTIFIER)
            Parser.check_token(next(it), ExprPrecedence.SHIFT)
        except TokenMismatchError:
            return False

        new_expr = Expression(FAGenerator.load_c(identifier.data))
        Parser.reduce(stack, new_expr)

        return True

    def rule_concat(self, stack):
        it = iter(reversed(stack))

        try:
            expr_1 = Parser.check_token(next(it), Expression)
            Parser.check_token(next(it), TokenType.META_CONCANATE)
            expr_2 = Parser.check_token(next(it), Expression)
            Parser.check_token(next(it), ExprPrecedence.SHIFT)
        except TokenMismatchError:
            return False

        new_expr = Expression(FAGenerator.concanate(expr_2.automat, expr_1.automat))
        Parser.reduce(stack, new_expr)

        return True

    def rule_or(self, stack):
        it = iter(reversed(stack))

        try:
            expr_1 = Parser.check_token(next(it), Expression)
            Parser.check_token(next(it), TokenType.META_OR)
            expr_2 = Parser.check_token(next(it), Expression)
            Parser.check_token(next(it), ExprPrecedence.SHIFT)
        except TokenMismatchError:
            return False

        new_expr = Expression(FAGenerator.union(expr_2.automat, expr_1.automat))
        Parser.reduce(stack, new_expr)

        return True


    def rule_brackets(self, stack):
        it = iter(reversed(stack))

        try:
            Parser.check_token(next(it), TokenType.RIGHT_BRACKET)
            expr = Parser.check_token(next(it), Expression)
            Parser.check_token(next(it), TokenType.LEFT_BRACKET)
            Parser.check_token(next(it), ExprPrecedence.SHIFT)
        except TokenMismatchError:
            return False

        new_expr = Expression(expr.automat)
        Parser.reduce(stack, new_expr)

        return True

    def rule_quan_0_N(self, stack):
        it = iter(reversed(stack))

        try:
            Parser.check_token(next(it), TokenType.META_QUANTIFIER_0_N)
            expr = Parser.check_token(next(it), Expression)
            Parser.check_token(next(it), ExprPrecedence.SHIFT)
        except TokenMismatchError:
            return False

        new_expr = Expression(FAGenerator.iterate(expr.automat))
        Parser.reduce(stack, new_expr)

        return True

    def _check_rules(self, stack):
        rules = (self.rule_id, self.rule_quan_0_N, self.rule_concat, self.rule_brackets, self.rule_or)

        for single_rule in rules:
            if single_rule(stack):
                return True
        return False

    def _precedence(self, a, b):
        if isinstance(a, Token):
            a = a.type
        if isinstance(b, Token):
            b = b.type
        return self._precedence_table[a][b]

    def parse(self):
        stack = [ExprTokenType.META_DOLAR]
        loaded = next(self._lexer, ExprTokenType.META_DOLAR)
        top_term = None

        while loaded != ExprTokenType.META_DOLAR or top_term != ExprTokenType.META_DOLAR:
            top_term, top_term_i = Parser.top_term(stack)
            precedence = self._precedence(top_term, loaded)

            if precedence == ExprPrecedence.SAME:
                stack.append(loaded)
                loaded = next(self._lexer, ExprTokenType.META_DOLAR)

            elif precedence == ExprPrecedence.SHIFT:
                stack.insert(top_term_i + 1, ExprPrecedence.SHIFT)
                stack.append(loaded)
                loaded = next(self._lexer, ExprTokenType.META_DOLAR)

            elif precedence == ExprPrecedence.REDUCE:
                if self._check_rules(stack):
                    pass
                else:
                    print("Syntax error.")
                    return

            else:
                print("Syntax error.")
                return
            top_term, top_term_i = Parser.top_term(stack)

        return stack[-1].automat

    @property
    def source(self) -> str:
        return self._lexer.source

    @source.setter
    def source(self, v: str) -> None:
        self._lexer.source = v
