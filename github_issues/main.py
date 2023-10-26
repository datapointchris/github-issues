import asyncio
import itertools
import os

import flask_admin as admin
import httpx
import peewee
from dotenv import load_dotenv
from flask import Flask, redirect
from flask_admin.contrib.peewee import ModelView

load_dotenv()

GITHUB_USER = 'datapointchris'
TOKEN = os.environ['GITHUB_TOKEN']
HEADERS = {'Authorization': f'Bearer {TOKEN}', 'X-GitHub-Api-Version': '2022-11-28'}
APP_DEBUG = True
APP_PORT = 5123

db = peewee.SqliteDatabase('file::memory:?cache=shared', check_same_thread=False)


class Issue(peewee.Model):
    repo = peewee.CharField()
    title = peewee.CharField()
    body = peewee.TextField()
    labels = peewee.TextField()
    milestone = peewee.TextField(null=True)
    created_at = peewee.DateTimeField()
    number = peewee.IntegerField()
    assignees = peewee.TextField(null=True)
    url = peewee.CharField()

    class Meta:
        database = db


class IssueAdmin(ModelView):
    page_size = 100
    can_create = False
    can_delete = False
    can_edit = False
    column_searchable_list = ('title', 'body')
    column_filters = ('repo', 'labels', 'milestone')
    column_sortable_list = ('title', 'created_at', 'repo', 'labels')


def get_repos_for_user(username, headers=None):
    repos_url = f'https://api.github.com/users/{username}/repos'
    repos = httpx.get(repos_url, headers=headers)
    return repos.json()


async def get_issues_for_repo(repo, headers=None):
    async with httpx.AsyncClient(headers=headers) as client:
        issues = []
        if repo_issues := await client.get(repo['url'] + '/issues'):
            for issue in repo_issues.json():
                issue_fields = ['title', 'number', 'created_at', 'url']
                d = {field: issue[field] for field in issue_fields}
                d['labels'] = [label['name'] for label in issue['labels']]
                d['assignees'] = [assignee['login'] for assignee in issue['assignees']] if issue['assignees'] else None
                d['milestone'] = issue['milestone']['title'] if issue['milestone'] else None
                d['body'] = issue['body'].split('\n')[0]
                d['repo'] = repo['name']
                issues.append(d)
        return issues


async def get_all_issues_for_user(username, headers=None):
    repos = get_repos_for_user(username, headers)
    issues = await asyncio.gather(*[get_issues_for_repo(repo, headers) for repo in repos])
    flattened_issues = list(itertools.chain.from_iterable(issues))
    return flattened_issues


app = Flask(__name__)
app.config['FLASK_ADMIN_SWATCH'] = 'darkly'
app.config['FLASK_ADMIN_FLUID_LAYOUT'] = True


@app.route('/')
def index():
    return redirect('/admin')


ad = admin.Admin(app, name='Admin', template_mode='bootstrap3')
ad.add_view(IssueAdmin(Issue))


def main():
    Issue.create_table()
    issues = asyncio.run(get_all_issues_for_user(GITHUB_USER, HEADERS))
    Issue.insert_many(issues).execute()

    app.run(debug=APP_DEBUG, port=APP_PORT)


if __name__ == '__main__':
    main()
