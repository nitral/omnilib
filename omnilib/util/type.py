class Singleton(type):
    """Singleton type to be used as a metaclass for Singleton classes.

    Usage:
        class MySingletonClass(metaclass=Singleton):
            def __init__(self):
                pass
            def method_a(self):
                pass

        obj1 = MySingletonClass()
        obj2 = MySingletonClass()
        assertTrue(obj1 == obj2)
    """

    # Mapping from Singleton subclasses to their singleton objects
    _subclass_instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._subclass_instances:
            cls._subclass_instances[cls] = super(
                Singleton, cls).__call__(*args, **kwargs)
        return cls._subclass_instances[cls]
