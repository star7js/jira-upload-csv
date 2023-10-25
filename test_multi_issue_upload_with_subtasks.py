import unittest
from unittest.mock import mock_open, patch, Mock
import multi_issue_upload_with_subtasks  # Replace with the actual name of your script


class TestJiraScript(unittest.TestCase):

    # Test for read_csv function
    @patch('builtins.open', new_callable=mock_open,
           read_data='Project Key,Summary,Description,Issue Type\nTest,Ticket 1,Description 1,Task')
    def test_read_csv(self, mock_open_instance):
        rows = multi_issue_upload_with_subtasks.read_csv('dummy.csv')
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['Project Key'], 'Test')
        # ... more assertions based on your CSV structure

    # Test for create_jira_issue function
    @patch.object(multi_issue_upload_with_subtasks.jira, 'issue_create', return_value={'key': 'TEST-123', 'id': '001'})
    def test_create_jira_issue(self, mock_issue_create):
        issue_data = {
            'project': {'key': 'Test'},
            'summary': 'Ticket 1',
            'description': 'Description 1',
            'issuetype': {'name': 'Task'}
        }
        response = multi_issue_upload_with_subtasks.create_jira_issue(issue_data)
        mock_issue_create.assert_called_once_with(fields=issue_data)
        self.assertEqual(response['key'], 'TEST-123')
        # ... more assertions if needed

    # Test for create_jira_subtask function (similar to the one above)
    @patch.object(multi_issue_upload_with_subtasks.jira, 'issue_create', return_value={'key': 'TEST-124', 'id': '002'})
    def test_create_jira_subtask(self, mock_issue_create):
        subtask_data = {
            'project': {'key': 'Test'},
            'summary': 'Subtask 1',
            'description': 'Subtask Description 1',
            'issuetype': {'name': 'Sub-task'},
            'parent': {'id': '001'}
        }
        response = multi_issue_upload_with_subtasks.create_jira_subtask(subtask_data)
        mock_issue_create.assert_called_once_with(fields=subtask_data)
        self.assertEqual(response['key'], 'TEST-124')
        # ... more assertions if needed


if __name__ == '__main__':
    unittest.main()
