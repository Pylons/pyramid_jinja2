import sys
import types

# True if we are running on Python 3.
PY3 = sys.version_info[0] == 3

if PY3: # pragma: no cover
    string_types = str,
    integer_types = int,
    class_types = type,
    text_type = str
    binary_type = bytes
    long = int
else: # pragma: no cover
    string_types = basestring,
    integer_types = (int, long)
    class_types = (type, types.ClassType)
    text_type = unicode
    binary_type = str

# TODO check if errors is ever used

def text_(s, encoding='latin-1', errors='strict'): # pragma: no cover
    if isinstance(s, binary_type):
        return s.decode(encoding, errors)
    return s # pragma: no cover

def bytes_(s, encoding='latin-1', errors='strict'): # pragma: no cover
    if isinstance(s, text_type):
        return s.encode(encoding, errors)
    return s

if PY3: # pragma: no cover
    def reraise(exc_info):
        etype, exc, tb = exc_info
        if exc.__traceback__ is not tb:
            raise exc.with_traceback(tb)
        raise exc
else: # pragma: no cover
    exec("def reraise(exc): raise exc[0], exc[1], exc[2]")

if PY3: # pragma: no cover
    from io import StringIO
    from io import BytesIO
else: # pragma: no cover
    from StringIO import StringIO
    BytesIO = StringIO
