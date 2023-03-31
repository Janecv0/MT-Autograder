### MT-Autograder
  
## Possible Frameworks:

    pytest, unittest, nose, doctest, Robot Framework => pytest

## Possible architecture:
Ask the user for the folder location where the student's code and test files are stored.
  
With use of the `os` module navigate to the folder and list all the .py files in the folder.
  
For each .py file in the folder, use `pytest` to run the tests in the associated test file(s). Might use the `subprocess` module to run pytest as a subprocess. Capture the output of pytest so you can analyze it later.
  
Determine the score for each student based on the results of the tests. User assigns weights to each test based on their importance.
  
Store the scores in a dictionary or database so they can be easily retrieved and analyzed later.
  
To check for cheating, we could use a plagiarism checker library such as `pycode_similar` or `codechecker`. Need to look at this.


## Goal:
  User gives path to folder with n student files and test file (with argparse)
  
  All teacher given test are tried and if specified other test (such as plagiathorism or efficiency) run through
  
  Test are running in safe container (docker) to prevent malicius code damage
  
  Record of each student score (html or csv)
  
  (make json with scores for each student, for end of semester summary html or csv)
