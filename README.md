# MT-Autograder

Are you bored of marking students python homeworks? If your answer is yes this web app is for you.

## USAGE
### Check python version
> [!IMPORTANT]
> This code is written for python 3.10.+

### Install docker
For testing docker is needed. [You can get it here](https://docs.docker.com/get-docker/).

Also pull latest python image: ```docker pull python ```

### Clone repo
After copying or downloading this repo get into main branch for deployment, other for development
### Create virtual environment
```
python -m venv venv
```
### Activate it
```
.\venv\Scripts\activate.bat 
```
(for windows cmd)

```
source .venv/Scripts/activate
```
(for linux terminal)
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
### Seed the DB
Run `seed.py` it creates db, with dummy users, classes, assignments, etc.

### Start uvicorn server
```
uvicorn main:app
```

Or you can use this for development, don't use it for deployment it's less stable.
```
uvicorn main:app --reload
```

### Try it!
Go to ```http://127.0.0.1:8000/``` and try it yourself. There are multiple users to try:

| login    | password |
|----------|----------|
| admin    | 1234     |
| teacher  | 1234     |
| student1 | 1234     |
| student2 | 1234     |
| student3 | 1234     |


### Basic usage now possible
Login to the website using one of logins above. Depending on what user(role) did you choose, you can try different things.

Role: Student

After you login, you are automatically redirected to page that shows all classes that you were enrolled in. You can click on class name, which will send you to list od assignments of that class. There is also a button that will show you status of assignments that you should do. You can click either on link to github or on name of assignment, which will redirect you to form in which you can submit and test your solution and see outcome including pytest error messages .

Role: Teacher

With `Teacher` account you can have no classes yet, but you can see classes in navigational panel Classes. As a teacher you can do everything that student can and more. Multiple buttons should show up such as: Create New Assignments, Enroll to this class and Enrolled users (list of students in this class).

Role: Super teacher
You can under Admin dropdown menu create new class. Otherwise same as Teacher

Role: Admin
You can do ANYTHING YOU WANT, jk. You can change roles of user or pop them from DB.

### Assignment test file
Each assignment file to test hw must start with this code for importing students code.
 ```
from HW import __name_of_function_
 ```

Otherwise this test file is regular pytest code with naming convention `test_{whatever}_{number of points(can be more then one int)}`

> [!TIP]
> Example
>```
>def test_1_5():
>    assert HW.add(1, 2) == 3
>```
>Where `test` is pytest prefix, `1` is name of test, `5` is number of points for passing it. 

### See student results
As teacher you can see results of students with press of button in assignment info, you can also see their code.



## Goal
Server into which teacher logs in, upload assignment and see status of individual students on it. There is also place for students to upload their homeworks and get direct feedback from the system such as percentage, mark and errors, that come out during testing.