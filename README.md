# Github Issues

WHY is it so hard to see all of the issues across all repos for a user on github?  

- JIRA is a b*tch to use and setup and it's so sloowwww  
- Linear is a cool app but doesn't support this functionality that I can find
- Github web doesn't support consolidating issues across repos
- Github Desktop seems mostly useless in general...

This is a simple python script that uses the github REST API to get all of the issues for a user.
Gets all of the open issues for all repos (private also if github token provided) for a user.  
Runs a flask server to serve flask-admin UI to view all of the issues.  
Temp storage in a sqlite db in memory while serving.

All this in ~100 lines of code 😎

## How To Use

1. Create `.env` file in the main dir
2. Add `GITHUB_TOKEN` to the `.env` file
3. Change the `GITHUB_USER` in `main.py` to the user you want to get the issues for.
4. Run `python main.py` (Install first in virtual env with poetry or pip)
5. Navigate browser to `http://127.0.0.1:5123/admin/issue/`

## Tech Stuff

- Github REST API
- Flask
- Flask-Admin
- peewee
- async calls to github api
- in memory sqlite db for temp storage while serving

## License

[MIT](https://tldrlegal.com/license/mit-license)
