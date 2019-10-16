
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
        assert Symbol('test').test() == '\n<symbol:test>'
