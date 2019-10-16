
import os,sys
from graphviz import Digraph

class Frame:
    def __init__(self,V):
        # type/class tag
        # this field is required for literal parsing by PLY library 
        self.type = self.__class__.__name__.lower()
        # scalar data value in implementation language type
        # mostly names the frame, but also can store things like numbers and strings
        self.val  = V
        # slots = attributes = string-keyed associative array
        self.slot = {}
        # ordered storage = AST nested elemens = vector = stack = queue
        self.nest = []

# class Frame:

    # dump and plot
    
    # callback for print
    def __repr__(self):
        return self.dump()
    # full tree-form dump
    def dump(self,depth=0,prefix='',voc=True,stack=True,test=False):
        # subtree header
        tree = self._pad(depth) + self.head(prefix=prefix,test=test)
        # infty recursion block
        if not depth: Frame._dumped = []
        if self in Frame._dumped: return tree + ' _/'
        else: Frame._dumped.append(self)
        # slots
        if voc:
            for i in self.slot:
                tree += self.slot[i].dump(depth+1,prefix='%s = '%i,test=test)
        # nested as subtrees
        if stack:
            for j in self.nest:
                tree += j.dump(depth+1,test=test)
        # resulting subtree
        return tree
    # short-form dump: <T:V> header only
    def head(self,prefix='',test=False):
        header = '%s<%s:%s>' % (prefix,self.type,self._val())
        if not test: header += ' @%x' % id(self)
        return header
    # pad tree with tabs with given depth
    def _pad(self,depth):
        return '\n' + '\t' * depth
    # .val can be non-string and must be overloaded in some frame classes
    def _val(self):
        return '%s' % self.val

# class Frame:

    # operators
    
    # A[key]
    def __getitem__(self,key):
        return self.slot[key]
    # A[key] = B
    def __setitem__(self,key,that):
        self.slot[key] = that ; return self
    # A << B --> A[B.val] = B
    def __lshift__(self,that):
        self[that.val] = that ; return self
    # A // B
    def __floordiv__(self,that):
        self.nest.append(that) ; return self

# class Frame:

    # method returns simplified tree dump for py.tests
    def test(self):
        return self.dump(test=True)

# primitive scalar data types
# close to low-level (hardware or implementation language)
class Primitive(Frame):
    def eval(self,ctx): # to itself
        ctx // self

# names other objects
class Symbol(Primitive): pass

# text string (multiline)
class String(Primitive): pass

# floating point number
class Number(Primitive): pass

# integer numbers
class Integer(Number): pass
# hexadecimal machine number
class Hex(Integer): pass
# binary string/number
class Bin(Integer): pass

# data containers
class Container(Frame): pass

# ordered variable-size vector
class Vector(Container): pass

# LIFO: push/pop interface
class Stack(Container): pass

# FIFO: put/get interface
class Queue(Container): pass

# associative array
class Dict(Container): pass

# single-element
class Set(Container): pass

# classes subset required to implement EDS: Executable Data Structure (c)
class Active(Frame): pass

# VM command which wraps Python function(context)
class Cmd(Active): pass

# global FORTH-like virtual machine

vm = VM('metaL')

# system init

if __name__ == '__main__':
    with open(sys.argv[0][:-3]+'.ini') as ini: # process metaL.ini
        vm // String(ini.read()) ; INTERP(vm)
