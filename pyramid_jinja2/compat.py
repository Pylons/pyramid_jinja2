import sys
import types

# True if we are running on Python 3.
PY3 = sys.version_info[0] == 3

if PY3:
    string_types = str,
    integer_types = int,
    class_types = type,
    text_type = str
    binary_type = bytes
    long = int
else:
    string_types = basestring,
    integer_types = (int, long)
    class_types = (type, types.ClassType)
    text_type = unicode
    binary_type = str

# TODO check if errors is ever used

def text_(s, encoding='latin-1', errors='strict'):
    if isinstance(s, binary_type):
        return s.decode(encoding, errors)
    return s

def bytes_(s, encoding='latin-1', errors='strict'):
    if isinstance(s, text_type):
        return s.encode(encoding, errors)
    return s

if PY3:
    from io import StringIO
    from io import BytesIO
else:
    from StringIO import StringIO
    BytesIO = StringIO
