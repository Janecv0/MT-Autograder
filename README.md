# MT-Autograder

Are you bored of marking students python homeworks? If your answer is yes this web app is for you.

## USAGE
### Check python version
> [!IMPORTANT]
> This code is written for python 3.10.+

### Clone repo
After copying or downloading this repo get into develop_api branch.
### Create virtual environment
```
python -m venv venv
```
### Activate it
```
.\venv\Scripts\activate.bat (for windows cmd)
```
### Install requirements
```
pip install -r .\req.txt
```
### Create .env

```
SECRET_KEY = ""
ALGORITHM = ""
ACCESS_TOKEN_EXPIRE_MINUTES = 
MAIL_USERNAME=""
MAIL_PASSWORD=""
MAIL_FROM=""
MAIL_SERVER=""

```

### Start uvicorn server
```
uvicorn main:app --reload
```
### Basic usage now possible
Create user (emails must be different from other users), you can have only one role (as of now) either `Student` or `Teacher`. This gives you different permissions. First make `Teacher` role, login using lock icon and create assignment (and upload test file - not implemented yet). Now you can login into `Student` account and create item (homework), where assignment id must be entered. After that you can upload homework file. Using test endpoint and adding assignment_id the homework will be tested, output will be shown and automatically added to your item in database. 

With `Teacher` account you can see and find all students and items. `Student` can only see info about himself and theirs items.

Each assignment file to test hw must start with this code for importing students code.
 ```
import importlib
import os
import json

with open("hw_name.json") as f:
    hw_name = json.load(f)

os.remove("hw_name.json")

try:
    HW = importlib.import_module(hw_name["filename"])
except ImportError:
    print(f"Failed to import module {hw_name}.")
 ```

Otherwise this test file is regular pytest code with naming convention `test_{whatever}_{number of points(only one int is allowed)}`

> [!TIP]
> Example
>```
>def test_1_5():
>    assert HW.add(1, 2) == 3
>```
>Where `test` is pytest prefix, `1` is name of test, `5` is number of points for passing it. 




## Goal
Server into which teacher logs in, upload assignment and see status of individual students on it. There is also place for students to upload their homeworks and get direct feedback from the system such as percentage, mark and errors, that come out during testing. 

## Work done
  
  ### Picking testing framework
  Out of : pytest, unittest, nose, doctest, Robot Framework. `Pytest` was picked.

  ### Running test from code with outcome capture
  Using `pytest` plugin `pytest-json-report` outcome is captured. From json file all needed data are taken.

  ### SQL database
  Using `sqlalchemy` SQL database is created. Files for this: `database.py`- database setup and `models.py`- table setup

  ### Picking back-end
  Out of: Flask, Django, FastAPI ->  `fastapi`

  ### Coding back-end
  Most of needed function almost done.