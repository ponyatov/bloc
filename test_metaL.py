
import pytest

from metaL import *

def test_hello():
    assert (
        Frame('Hello') // Frame('World') << Frame('slot') ).test() == \
        '\n<frame:Hello>\n\tslot = <frame:slot>\n\t<frame:World>'
