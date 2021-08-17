import unittest
from parser import Parser
from lexer import Lexer
from classes import *

#TODO: move this
class TokenKind(Enum):
    EOF = -1
    DEF = -2
    EXTERN = -3
    IDENTIFIER = -4
    NUMBER = -5
    OPERATOR = -6

Token = namedtuple('Token', 'kind value')

class TestLexer(unittest.TestCase):
    def _assert_toks(self, toks, kinds):
        """Assert that the list of toks has the given kinds."""
        self.assertEqual([t.kind.name for t in toks], kinds)

    def test_lexer_simple_tokens_and_values(self):
        l = Lexer('a+1')
        toks = list(l.tokens())
        self.assertEqual(toks[0], Token(TokenKind.IDENTIFIER, 'a'))
        self.assertEqual(toks[1], Token(TokenKind.OPERATOR, '+'))
        self.assertEqual(toks[2], Token(TokenKind.NUMBER, '1'))
        self.assertEqual(toks[3], Token(TokenKind.EOF, ''))

        l = Lexer('.1519')
        toks = list(l.tokens())
        self.assertEqual(toks[0], Token(TokenKind.NUMBER, '.1519'))

    def test_token_kinds(self):
        l = Lexer('10.1 def der extern foo (')
        self._assert_toks(
            list(l.tokens()),
            ['NUMBER', 'DEF', 'IDENTIFIER', 'EXTERN', 'IDENTIFIER',
             'OPERATOR', 'EOF'])

        l = Lexer('+- 1 2 22 22.4 a b2 C3d')
        self._assert_toks(
            list(l.tokens()),
            ['OPERATOR', 'OPERATOR', 'NUMBER', 'NUMBER', 'NUMBER', 'NUMBER',
             'IDENTIFIER', 'IDENTIFIER', 'IDENTIFIER', 'EOF'])

    def test_skip_whitespace_comments(self):
        l = Lexer('''
            def foo # this is a comment
            # another comment
            \t\t\t10
            ''')
        self._assert_toks(
            list(l.tokens()),
            ['DEF', 'IDENTIFIER', 'NUMBER', 'EOF'])


class TestParser(unittest.TestCase):
    def _flatten(self, ast):
        """Test helper - flattens the AST into a nested list."""
        if isinstance(ast, NumberExprAST):
            return ['Number', ast.val]
        elif isinstance(ast, VariableExprAST):
            return ['Variable', ast.name]
        elif isinstance(ast, BinaryExprAST):
            return ['Binop', ast.op,
                    self._flatten(ast.lhs), self._flatten(ast.rhs)]
        elif isinstance(ast, CallExprAST):
            args = [self._flatten(arg) for arg in ast.args]
            return ['Call', ast.callee, args]
        elif isinstance(ast, PrototypeAST):
            return ['Proto', ast.name, ' '.join(ast.argnames)]
        elif isinstance(ast, FunctionAST):
            return ['Function',
                    self._flatten(ast.proto), self._flatten(ast.body)]
        else:
            raise TypeError('unknown type in _flatten: {0}'.format(type(ast)))

    def _assert_body(self, toplevel, expected):
        """Assert the flattened body of the given toplevel function"""
        self.assertIsInstance(toplevel, FunctionAST)
        self.assertEqual(self._flatten(toplevel.body), expected)

    def test_basic(self):
        ast = Parser().parse_toplevel('2')
        self.assertIsInstance(ast, FunctionAST)
        self.assertIsInstance(ast.body, NumberExprAST)
        self.assertEqual(ast.body.val, '2')

    def test_basic_with_flattening(self):
        ast = Parser().parse_toplevel('2')
        self._assert_body(ast, ['Number', '2'])

        ast = Parser().parse_toplevel('foobar')
        self._assert_body(ast, ['Variable', 'foobar'])

    def test_expr_singleprec(self):
        ast = Parser().parse_toplevel('2+ 3-4')
        self._assert_body(ast,
            ['Binop',
                '-', ['Binop', '+', ['Number', '2'], ['Number', '3']],
                ['Number', '4']])

    def test_expr_multiprec(self):
        ast = Parser().parse_toplevel('2+3*4-9')
        self._assert_body(ast,
            ['Binop', '-',
                ['Binop', '+',
                    ['Number', '2'],
                    ['Binop', '*', ['Number', '3'], ['Number', '4']]],
                ['Number', '9']])

    def test_expr_parens(self):
        ast = Parser().parse_toplevel('2*(3-4)*7')
        self._assert_body(ast,
            ['Binop', '*',
                ['Binop', '*',
                    ['Number', '2'],
                    ['Binop', '-', ['Number', '3'], ['Number', '4']]],
                ['Number', '7']])

    def test_externals(self):
        ast = Parser().parse_toplevel('extern sin(arg)')
        self.assertEqual(self._flatten(ast), ['Proto', 'sin', 'arg'])

        ast = Parser().parse_toplevel('extern Foobar(nom denom abom)')
        self.assertEqual(self._flatten(ast),
            ['Proto', 'Foobar', 'nom denom abom'])

    def test_funcdef(self):
        ast = Parser().parse_toplevel('def foo(x) 1 + bar(x)')
        self.assertEqual(self._flatten(ast),
            ['Function', ['Proto', 'foo', 'x'],
                ['Binop', '+',
                    ['Number', '1'],
                    ['Call', 'bar', [['Variable', 'x']]]]])


if __name__ == '__main__':
    # dump the AST
    p = Parser()
    print(p.parse_toplevel('def bina(a b) a + b').dump())