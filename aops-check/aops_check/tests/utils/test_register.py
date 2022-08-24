import unittest

from aops_check.utils.register import Register

register = Register()


class RegisterTestCase(unittest.TestCase):
    def test_register_should_return_registered_class_when_is_normal(self):
        @register.register('1')
        class Test1(Register):
            @staticmethod
            def run():
                return "test1"

        @register.register('2')
        class Test2(Register):
            @staticmethod
            def run():
                return "test2"

        self.assertEqual(len(register.dict), 2)
        self.assertEqual(register.build('1').run(), 'test1')

    def test_register_should_raise_error_when_input_target_is_callable(self):
        def test():
            return 1

        self.assertRaises(ValueError, register.register, test)


if __name__ == '__main__':
    unittest.main()
