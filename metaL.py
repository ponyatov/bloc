
import os,sys
import tempfile
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

    ## dump

    # callback for print
    def __repr__(self):
        return self.dump()
    # full tree-form dump
    def dump(self,depth=0,prefix='',voc=True,stack=True,test=False):
        # subtree header
        tree = self._pad(depth) + self.head(prefix,test)
        # infty recursion block
        if not depth: Frame._dumped = []
        if self in Frame._dumped: return tree + ' _/'
        else: Frame._dumped.append(self)
        # slot{}s
        if voc:
            for i in self.slot:
                tree += self.slot[i].dump(depth+1,prefix='%s = '%i,test=test)
        # nest[]ed as subtrees
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
    # tree dump padding
    def _pad(self,depth):
        return '\n' + '\t' * depth
    # .val dump must be tunable for strings, numbers,..
    def _val(self):
        return '%s' % self.val

    ## plot
    
    # node shapes and styles can be overloaded to show node class graphically
    def _shape(self): return 'box'
    def _style(self): return 'rounded'
    
    # recursive traversal with graphviz callings
    def plot(self,dot=None,depth=0,parent=None,link='',color='black',xdot=False):
        # init in recursion root
        if not dot: dot = Digraph(format='dot',graph_attr={'rankdir':'LR'})
        # nodes must be linked by id(node) only
        dot.node("%s"%id(self),label='%s:%s'%(self.type,self._val()),shape=self._shape(),style=self._style())
        # draw edge if parent exists
        if parent: dot.edge('%s'%id(parent),'%s'%id(self),color=color,label='%s'%link)
        # infty recursion block
        if not depth: Frame._plotted = []
        if self in Frame._plotted: return dot
        else: Frame._plotted.append(self)
        # draw slots with blue
        for i in self.slot:
            self.slot[i].plot(dot,depth+1,parent=self,link=i,color='blue')
        # draw nests with red and number index
        idx = 0
        for j in self.nest:
            j.plot(dot,depth+1,parent=self,link=idx,color='red'); idx += 1
        # plot in recursion root
        if not depth:
            if xdot:
                with tempfile.NamedTemporaryFile(prefix='plot',suffix='.dot',dir='.',delete=None) as tf:
                    tf.write(dot.pipe()) ; tf.close()
                    os.system('xdot %s' % tf.name)
                    os.remove(tf.name)
        # return plot for Jupyter
        return dot

    ## operators

    # A[key]
    def __getitem__(self,key):
        return self.slot[key]
    # A[key] = B
    def __setitem__(self,key,that):
        if isinstance(that,Frame): self.slot[key] = that
        elif callable(that): self.slot[key] = Cmd(that)
        elif isinstance(that,str): self.slot[key] = Str(that)
        else: raise TypeError((that,type(that)))
        return self
    # A << B --> A[B.val] = B
    def __lshift__(self,that):
        if isinstance(that,Frame): self[that.val] = that
        elif callable(that): self[that.__name__] = Cmd(that)
        else: raise TypeError((that,type(that)))
        return self
    # A // B
    def __floordiv__(self,that):
        if isinstance(that,Frame): self.nest.append(that)
        elif isinstance(that,int): self.nest.append(Int(that))
        elif isinstance(that,str): self.nest.append(Str(that))
        else: raise TypeError((that,type(that)))
        return self

    ## stack manipulations

    # ( a b -- a )
    def pop(self):
        return self.nest.pop(-1)
    # ( a b -- b )
    def pip(self):
        return self.nest.pop(-2)
    # ( a b -- a b )
    def top(self):
        return self.nest[-1]
    # ( a b -- a b )
    def tip(self):
        return self.nest[-2]
    # ( a b -- )
    def dropall(self):
        self.nest = [] ; return self    

    ## iterator/generator methods for Yield Prolog unification work

    def __iter__(self):
        for i in self.nest: yield i

    # method returns simplified tree dump for py.tests
    def test(self,voc=True):
        return self.dump(voc=voc,test=True)

# `Primitive` scalar data types
# close to low-level (hardware or implementation language)
class Prim(Frame):
    # all primitives evaluates to itself
    def eval(self,ctx):
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

## metaprogramming
class Meta(Frame): pass
class Module(Meta): pass
class Plugin(Module): pass
class Fn(Meta): pass
class Var(Meta): pass
class Type(Meta): pass

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
    ## VM evals to itself without nested computation
    def eval(self,ctx):
        ctx // self

# `Sequence`: every element in nest[] executes one by one on a single provided context
class Seq(Active,Vector): pass

# global FORTH-like virtual machine

vm = VM('metaL') ; vm['vm'] = vm

# BYE ( -- ) stop system
def BYE(ctx): sys.exit(0)
vm << BYE

## debug

# ? ( -- ) print current VM stack and continue execution
def Q(ctx): print(ctx.dump(voc=False))
vm['?'] = Q

# ?? ( -- ) print full VM state and stop the system
def QQ(ctx): print(ctx) ; BYE(ctx)
vm['??'] = QQ

# w? ( -- ) dump VM state without exit
def QW(ctx): print(ctx.dump(voc=True))
vm['?w'] = QW

## manipulations

def EQ(ctx): addr = ctx.pop() ; ctx[addr.val] = ctx.pop()
vm['='] = EQ

## plot

## ( a -- ) plot a
def Qp(ctx): ctx.pop().plot(xdot=True)
vm['?p'] = Qp

## stack operations

# . ( a b c -- ) drop all data from the stack
def DOT(ctx): ctx.dropall()
vm['.'] = DOT

## no-syntax parser

import ply.lex as lex

tokens = ['sym','str','num','int','hex','bin']

t_ignore = ' \t\r\n'
t_ignore_comment = r'[\#\\].*'

# string parsing

states = (('str','exclusive'),)

t_str_ignore = ''

def t_str(t):
    r"'"
    t.lexer.push_state('str') ; t.lexer.string = ''
def t_str_str(t):
    r"'"
    t.lexer.pop_state() ; return Str(t.lexer.string)
def t_str_any(t):
    r"."
    t.lexer.string += t.value

# other tokens

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

def t_ANY_error(t): raise SyntaxError(t)

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
    vm // cmd ; INTERP(vm)

# system init

if __name__ == '__main__':
    with open(sys.argv[0][:-3]+'.ini') as ini: # process metaL.ini
        M(ini.read())
