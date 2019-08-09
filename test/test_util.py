import unittest

from omnilib import util


class TestMutableVariable(unittest.TestCase):
    def test_get_value(self):
        self.assertEqual(util.MutableVariable(1).get_value(), 1)

    def test_set_value(self):
        var = util.MutableVariable(1)
        self.assertEqual(var.get_value(), 1)
        var.set_value(2)
        self.assertEqual(var.get_value(), 2)

    def test_len(self):
        var = util.MutableVariable("test")
        self.assertEqual(len("test"), len(var))
        var = util.MutableVariable([1, 2, 3])
        self.assertEqual(len(var), 3)

    def test_getitem(self):
        var = util.MutableVariable([1, 2, 3])
        self.assertEqual(var[0], 1)
        self.assertEqual(var[1], 2)
        self.assertEqual(var[2], 3)

    def test_reversed(self):
        var = util.MutableVariable([1, 2, 3])
        for t in zip(reversed(var), reversed([1, 2, 3])):
            self.assertEqual(t[0], t[1])

    def test_rich_comparison_methods(self):
        # Test __eq__
        self.assertEqual(util.MutableVariable(1), 1)
        self.assertTrue(util.MutableVariable(1) == 1)
        self.assertFalse(util.MutableVariable(1) == 2)
        self.assertEqual(util.MutableVariable("Test"), "Test")
        self.assertTrue(util.MutableVariable("Test") == "Test")
        self.assertFalse(util.MutableVariable("Case") == "Test")
        self.assertEqual(util.MutableVariable(1), util.MutableVariable(1))
        self.assertTrue(util.MutableVariable(1) == util.MutableVariable(1))
        self.assertFalse(util.MutableVariable(1) == util.MutableVariable(2))

        # Test __lt__, __gt__
        self.assertTrue(util.MutableVariable(1) < util.MutableVariable(2))
        self.assertTrue(util.MutableVariable(1) > util.MutableVariable(0))
        self.assertFalse(util.MutableVariable(1) > util.MutableVariable(2))
        self.assertFalse(util.MutableVariable(1) < util.MutableVariable(0))

        # Test __ge__, __le__
        self.assertTrue(util.MutableVariable(1) <= util.MutableVariable(2))
        self.assertTrue(util.MutableVariable(1) >= util.MutableVariable(0))
        self.assertFalse(util.MutableVariable(1) >= util.MutableVariable(2))
        self.assertFalse(util.MutableVariable(1) <= util.MutableVariable(0))

        # Test __ne__
        self.assertTrue(util.MutableVariable(1) != util.MutableVariable(2))

    def test_bool(self):
        self.assertTrue(util.MutableVariable(True))
        self.assertFalse(util.MutableVariable(False))
        self.assertFalse(util.MutableVariable(None))

    def test_iterator(self):
        test_list = [1, 2, 3]
        var = util.MutableVariable([1, 2, 3])
        for i in range(len(var)):
            self.assertEqual(test_list[i], var[i])


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
