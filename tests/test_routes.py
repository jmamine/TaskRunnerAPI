import unittest

from app import app


class TaskRoutesTestCase(unittest.TestCase):
    def setUp(self):
        """Set up test variables."""
        self.app = app
        self.app.config.from_object('config.TestingConfig')
        self.app.config['SERVER_NAME'] = '127.0.0.1:5000'
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        """Tear down test variables."""
        self.app_context.pop()

    def test_handle_python_task(self):
        response = self.client.post('/task/py', json={'code': 'print("Hello, World!")'})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('result', data)

    def test_handle_shell_task(self):
        response = self.client.post('/task/sh', json={'code': 'echo "Hello, World!"'})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('result', data)

    def test_list_tasks_route(self):
        response = self.client.get('/task')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIsInstance(data, list)

    def test_manage_task_route(self):
        create_response = self.client.post('/task/py', json={'code': 'print("Hello, World!")'})
        self.assertEqual(create_response.status_code, 200)
        task_id = create_response.get_json().get('task_id')
        self.assertIsNotNone(task_id)

        manage_response = self.client.put(f'/task/{task_id}', json={'action': 'stop'})
        self.assertEqual(manage_response.status_code, 200)

    def test_stop_task_route(self):
        create_response = self.client.post('/task/py', json={'code': 'print("Hello, World!")'})
        self.assertEqual(create_response.status_code, 200)
        task_id = create_response.get_json().get('task_id')
        self.assertIsNotNone(task_id)

        stop_response = self.client.put(f'/task/{task_id}', json={'action': 'stop'})
        self.assertEqual(stop_response.status_code, 200)

    def test_task_schedule_route(self):
        create_response = self.client.post('/task/py', json={'code': 'print("Hello, World!")'})
        self.assertEqual(create_response.status_code, 200)
        task_id = create_response.get_json().get('task_id')
        self.assertIsNotNone(task_id)

        schedule_response = self.client.post('/task/schedule', json={'task_id': task_id, 'time': '2024-12-31T23:59:59'})
        self.assertEqual(schedule_response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
