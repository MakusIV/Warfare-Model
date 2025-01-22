#import sys
#print(sys.path)
import unittest
from Persistence.Source.Task import Task


class TestTask(unittest.TestCase):
    def test_init(self):
        task = Task(params={'action': {'id': 'WrappedAction', 'params': {'value': 1, 'name': 'test'}}}, number=1, auto=True, id='task_id', enabled=True)
        self.assertEqual(task.params, {'action': {'id': 'WrappedAction', 'params': {'value': 1, 'name': 'test'}}})
        self.assertEqual(task.number, 2)
        self.assertTrue(task.auto)
        self.assertEqual(task.id, 'task_id')
        self.assertTrue(task.enabled)        
       

    def test_toString(self):
        task = Task(params={'action': {'id': 'WrappedAction', 'params': {'value': 1, 'name': 'test'}}}, number=1, auto=True, id='task_id', enabled=True)
        expected_string = "number: 1, auto: True, id: task_id, enabled: True\naction:\n id: WrappedAction\n value: 1, name: test"
        self.assertEqual(task.toString(), expected_string)

    def test_params_setter(self):
        task = Task()
        task.params = {'action': {'id': 'WrappedAction', 'params': {'value': 1, 'name': 'test'}}}
        self.assertEqual(task.params, {'action': {'id': 'WrappedAction', 'params': {'value': 1, 'name': 'test'}}})

    def test_invalid_params(self):
        with self.assertRaises(Exception):
            Task(params={'invalid_key': 'invalid_value'})

    def test_invalid_number(self):
        with self.assertRaises(Exception):
            Task(number='invalid_number')

    def test_invalid_auto(self):
        with self.assertRaises(Exception):
            Task(auto='invalid_auto')

    def test_invalid_id(self):
        with self.assertRaises(Exception):
            Task(id=123)

    def test_invalid_enabled(self):
        with self.assertRaises(Exception):
            Task(enabled='invalid_enabled')

if __name__ == '__main__':
    unittest.main()