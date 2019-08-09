class MutableVariable(object):
    """Container for any value that is meant to be edited at runtime from
    multiple sites

    The contained value may or may not be mutable itself. The MutableVariable
    object then becomes the source of truth for the contained value.

    Example Use-Case: Used by Probe Resource to expose a mutable value to HTTP
    Server.
    """

    def __init__(self, value):
        self._value = value

    def get_value(self):
        return self._value

    def set_value(self, value):
        self._value = value

    def __len__(self):
        return len(self._value)

    def __getitem__(self, offset):
        return self._value[offset]

    def __reversed__(self):
        return reversed(self._value)

    def __eq__(self, other):
        return self._value == other

    def __lt__(self, other):
        return self._value < other

    def __gt__(self, other):
        return self._value > other

    def __le__(self, other):
        return self._value <= other

    def __ge__(self, other):
        return self._value >= other

    def __bool__(self):
        return self._value.__bool__()

    def __iter__(self):
        return self._value.__iter__()
