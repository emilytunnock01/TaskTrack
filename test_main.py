import unittest
from main_file import db_connection, save_task_to_db, change_task_day

class TestTaskManager(unittest.TestCase):
    def setUp(self):
        # Set up the database schema before each test
        cursor = db_connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                content TEXT,
                day TEXT NOT NULL,
                status TEXT NOT NULL
            )
        ''')
        db_connection.commit()

    def tearDown(self):
        # Clear the tasks table after each test
        cursor = db_connection.cursor()
        cursor.execute("DELETE FROM tasks")
        db_connection.commit()

    def test_save_task_to_db(self):
        # Call the function to save a task
        save_task_to_db("Test Task", "This is a test task.", "Monday", "not-completed")

        # Verify the task is saved in the database
        cursor = db_connection.cursor()
        cursor.execute("SELECT title, content, day, status FROM tasks WHERE title = ?", ("Test Task",))
        task = cursor.fetchone()

        # Check that the task matches the input
        self.assertIsNotNone(task)
        self.assertEqual(task, ("Test Task", "This is a test task.", "Monday", "not-completed"))

    @unittest.mock.patch("task_manager.messagebox.showinfo")
    def test_change_task_day(self, mock_messagebox):
        # Insert a test task
        save_task_to_db("Test Task", "This is a test task.", "Monday", "not-completed")

        # Get the task ID
        cursor = db_connection.cursor()
        cursor.execute("SELECT id FROM tasks WHERE title = ?", ("Test Task",))
        task_id = cursor.fetchone()[0]

        # Call the function to change the task's day
        change_task_day(task_id, "Tuesday")

        # Verify the task's day is updated
        cursor.execute("SELECT day FROM tasks WHERE id = ?", (task_id,))
        updated_day = cursor.fetchone()[0]
        self.assertEqual(updated_day, "Tuesday")

        # Verify that messagebox was called with the correct message
        mock_messagebox.assert_called_once_with("Task Updated", "Task has been moved to Tuesday.")

if __name__ == "__main__":
    unittest.main()
