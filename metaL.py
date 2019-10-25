
import os,sys
from graphviz import Digraph

# Marvin Minsky's extended frame model
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

    # stack manipulations

    ## ( a b -- a )
    def pop(self):
        return self.nest.pop(-1)
    ## ( a b -- b )
    def pip(self):
        return self.nest.pop(-2)
    ## ( a b -- a b )
    def top(self):
        return self.nest[-1]
    ## ( a b -- a b )
    def tip(self):
        return self.nest[-2]
    ## ( a b -- )
    def dropall(self):
        self.nest = [] ; return self    

# class Frame:

    # method returns simplified tree dump for py.tests
    def test(self,voc=True):
        return self.dump(voc=voc,test=True)

# `Primitive` scalar data types
# close to low-level (hardware or implementation language)
class Prim(Frame):
    def eval(self,ctx): # to itself
        ctx // self

# `Symbol` names other objects
class Sym(Prim): pass

# text `String` (multiline)
class Str(Prim): pass

# floating point `Number`
class Num(Prim):
    def __init__(self,V):
        Prim.__init__(self,float(V))

# `Integer` numbers
class Int(Num):
    def __init__(self,V):
        Prim.__init__(self,int(V))

# `Hex`adecimal machine number
class Hex(Int):
    def __init__(self,V):
        Prim.__init__(self,int(V[2:],0x10))
    def _val(self):
        return hex(self.val)

# `Bin`ary string/number
class Bin(Int):
    def __init__(self,V):
        Prim.__init__(self,int(V[2:],0x02))
    def _val(self):
        return bin(self.val)

# data `Container`s
class Cont(Frame): pass

# ordered variable-size `Vector`
class Vector(Cont): pass

# LIFO: push/pop interface
class Stack(Cont): pass

# FIFO: put/get interface
class Queue(Cont): pass

# associative array
class Dict(Cont): pass

# single-element
class Set(Cont): pass

# classes subset required to implement EDS: Executable Data Structure (c)
class Active(Frame): pass

# VM `Command` which wraps Python function(context)
class Cmd(Active):
    # use function name as .val
    def __init__(self,F):
        Active.__init__(self,F.__name__)
        self.fn = F
    # apply stored function to context
    def eval(self,ctx):
        self.fn(ctx)        

# context = virtual machine
# represents FORTH-like execution context: vocabulary + stack + set of commands works over VM state
class VM(Active):
    ## operator methods specially dedicated for wrapping Python functions
    def __setitem__(self,key,F):
        if callable(F): self[key] = Cmd(F) ; return self
        else: return Active.__setitem__(self,key,F)
    def __lshift__(self,F):
        if callable(F): return self << Cmd(F)
        else: return Active.__lshift__(self,F)

# `Sequence`: every element in nest[] executes one by one on a single provided context
class Seq(Active,Vector): pass

# global FORTH-like virtual machine

vm = VM('metaL') ; vm['vm'] = vm

# BYE ( -- ) stop system
def BYE(ctx): sys.exit(0)
vm << BYE

# debug

# ? ( -- ) print current VM stack and continue execution
def Q(ctx): print(ctx.dump(voc=False))
vm['?'] = Q

# ?? ( -- ) print full VM state and stop the system
def QQ(ctx): print(ctx) ; BYE(ctx)
vm['??'] = QQ

# stack operations

# . ( a b c -- ) drop all data from the stack
def DOT(ctx): ctx.dropall()
vm['.'] = DOT

# no-syntax parser

import ply.lex as lex

tokens = ['sym','num','int','hex','bin']

t_ignore = ' \t\r\n'
t_ignore_comment = r'[\#\\].*'

def t_hex(t):
    r'0x[0-9a-fA-F]+'
    return Hex(t.value)

def t_bin(t):
    r'0b[01]+'
    return Bin(t.value)

def t_num(t):
    r'[+\-]?[0-9]+\.[0-9]*([eE][+\-][0-9]+)?'
    return Num(t.value)

def t_num_exp(t):
    r'[+\-]?[0-9]+[eE][+\-][0-9]+'
    return Num(t.value)

def t_int(t):
    r'[+\-]?[0-9]+'
    return Int(t.value)

def t_sym(t):
    r'(`)|[^ \t\r\n\#\\]+'
    return Sym(t.value)

def t_error(t): raise SyntaxError(t)

# interpreter

## ( -- str:token )
def WORD(ctx):
    token = ctx.lexer.token()
    if token: ctx // token
    return token
vm['`'] = WORD

## ( str:token -- some:object | notfound:token )
def FIND(ctx):
    token = ctx.pop()
    try: ctx // ctx[token.val] ; return True
    except KeyError: ctx // token ; return False

## ( any:object -- ... )
def EVAL(ctx):
    ctx.pop().eval(ctx)

## ( str -- )
def INTERP(ctx):
    ctx.lexer = lex.lex() ; ctx.lexer.input(ctx.pop().val)
    while True:
        if not WORD(ctx): break
        if isinstance(ctx.top(),Sym):
            if not FIND(ctx): raise SyntaxError(ctx.top())
        EVAL(ctx)

# run commands from Jupyter as strings
def M(cmd=''):
    vm // Str(cmd) ; INTERP(vm)

# system init

if __name__ == '__main__':
    with open(sys.argv[0][:-3]+'.ini') as ini: # process metaL.ini
        M(ini.read())
