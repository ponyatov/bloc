
import pytest

from metaL import *

class TestFrame:
    
    def setup(self):
        self.hello = Frame('Hello') // Frame('World') << Frame('slot')

    def test_empty(self):
        assert Frame('').test() == '\n<frame:>'

    def test_hello(self):
        assert self.hello.test() == \
            '\n<frame:Hello>\n\tslot = <frame:slot>\n\t<frame:World>'
        
    def test_operators(self):
        assert self.hello['slot'].test() == '\n<frame:slot>'

class TestPrimitive:

    def test_symbol(self):
        assert Sym('test').test() == '\n<sym:test>'

class TestParser:
    
    def setup(self):
        self.lexer = lex.lex()
        self.lexer.input('`symbol -01 +02.30 -04e+5 0xDeadBeef 0b1101')
    
    def test_parser(self):
        assert self.lexer.token().test() == '\n<sym:`>'
        assert self.lexer.token().test() == '\n<sym:symbol>'
        assert self.lexer.token().test() == '\n<int:-1>'
        assert self.lexer.token().test() == '\n<num:2.3>'
        assert self.lexer.token().test() == '\n<num:-400000.0>'
        assert self.lexer.token().test() == '\n<hex:0xdeadbeef>'
        assert self.lexer.token().test() == '\n<bin:0b1101>'

class TestInterpreter:
    
    def setup(self):
        self.lexer = lex.lex()

    def test_numbers(self):
        vm.dropall()
        M('`symbol -01 +02.30 -4e+5 0xDeadBeef 0b1101 \ number literals')
        assert vm.test(voc=False) == '\n<vm:metaL>\n\t<sym:symbol>\n\t<int:-1>'+\
                                     '\n\t<num:2.3>\n\t<num:-400000.0>'+\
                                     '\n\t<hex:0xdeadbeef>\n\t<bin:0b1101>'
