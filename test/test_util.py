import unittest

from omnilib import util


class TestSingleton(unittest.TestCase):
    def test_object(self):
        class SingletonExample(metaclass=util.Singleton):
            pass

        obj_1 = SingletonExample()
        obj_2 = SingletonExample()
        self.assertTrue(obj_1 is obj_2)

    def test_constructor(self):
        class SingletonExample(metaclass=util.Singleton):
            def __init__(self, msg):
                self.msg = msg

        obj_1 = SingletonExample("msg1")
        obj_2 = SingletonExample("msg2")        # Should not overwrite "msg1"
        self.assertEqual(obj_1.msg, "msg1")
        self.assertEqual(obj_2.msg, "msg1")

    def test_method(self):
        class SingletonExample(metaclass=util.Singleton):
            def __init__(self, msg):
                self.msg = msg

            def return_msg(self):
                return self.msg

        obj_1 = SingletonExample("msg1")
        obj_2 = SingletonExample("msg2")        # Should not overwrite "msg1"
        self.assertEqual(obj_1.return_msg(), "msg1")
        self.assertEqual(obj_2.return_msg(), "msg1")


if __name__ == '__main__':
    unittest.main()
