import csv
from atlassian import Jira

BASE_URL = 'https://your-jira-instance-url'
jira = Jira(
    url=BASE_URL,
    username='your-username',
    password='your-api-token'
)


def read_csv(file_path):
    with open(file_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        return list(reader)


def create_jira_issue(issue_data):
    return jira.issue_create(fields=issue_data)


def create_jira_subtask(subtask_data):
    return jira.issue_create(fields=subtask_data)


def main():
    rows = read_csv('path_to_your_csv_file.csv')
    for row in rows:
        issue_data = {
            'project': {'key': row['Project Key']},
            'summary': row['Summary'],
            'description': row['Description'],
            'issuetype': {'name': row['Issue Type']}
        }

        # Create the main issue in Jira
        main_issue = create_jira_issue(issue_data)

        # Construct the issue URL
        issue_url = f"{BASE_URL}/browse/{main_issue['key']}"
        print(f"Issue {row['Summary']} created with Key: {main_issue['key']} and URL: {issue_url}")

        # Check if Subtask Summary and Subtask Description are present
        if row['Subtask Summary'] and row['Subtask Description']:
            # Create a subtask and link it to the main issue
            subtask_data = {
                'project': {'key': row['Project Key']},
                'summary': row['Subtask Summary'],
                'description': row['Subtask Description'],
                'issuetype': {'name': 'Sub-task'},  # Assuming the issuetype for subtasks is named 'Sub-task'
                'parent': {'id': main_issue['id']}
            }

            subtask = create_jira_subtask(subtask_data)
            subtask_url = f"{BASE_URL}/browse/{subtask['key']}"
            print(f"Subtask {row['Subtask Summary']} created with Key: {subtask['key']} and URL: {subtask_url} linked to main issue {main_issue['key']}")


if __name__ == '__main__':
    main()
