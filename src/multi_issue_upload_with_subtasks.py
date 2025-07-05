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
    last_id = None
    main_issue = None

    for row in rows:
        current_id = row['ID']

        # Check if we're dealing with a new main issue
        if current_id != last_id:
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

        # Assuming all rows, even those for main issues, can have subtask data
        if row['Subtask Summary'] and row['Subtask Description']:
            subtask_data = {
                'project': {'key': row['Project Key']},
                'summary': row['Subtask Summary'],
                'description': row['Subtask Description'],
                'issuetype': {'name': 'Sub-task'},
                'parent': {'id': main_issue['id']}
            }

            subtask = create_jira_subtask(subtask_data)
            subtask_url = f"{BASE_URL}/browse/{subtask['key']}"
            print(
                f"Subtask {row['Subtask Summary']} created with Key: {subtask['key']} and URL: {subtask_url} linked "
                f"to main issue {main_issue['key']}")

        last_id = current_id


if __name__ == '__main__':
    main()
