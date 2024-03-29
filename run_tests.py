import subprocess
import json
from subprocess import DEVNULL


def run_tests(test_n: int, user: int):
    """Run the tests and return the grade and the points.

    Args:
        test_n (int): The assignmment number.
        user (str): The user's name.

    Returns:
        dict: A dictionary containing the mark, pass points, and failed points.
    """

    json_filename = f"HW_{test_n}_{user}_report.json"
    hw_filename = f"HW_{test_n}_{user}"
    with open("hw_name.json", "w") as f:
        json.dump({"filename": hw_filename}, f)

    subprocess.run(
        [
            "pytest",
            f"test_HW_{test_n}.py",
            "-q",
            "--json-report",
            f"--json-report-file={json_filename}",
        ],
        stdout=DEVNULL,
        stderr=DEVNULL,
    )

    with open(json_filename) as f:
        report_data = json.load(f)

    return how_did_we_do(report_data["tests"], False)


def print_summary(test):
    """Print the summary of a test.

    Args:
        test (dict): The test dictionary.
    """

    if test["outcome"] == "passed":
        print(f"✅ {test['nodeid']}")
    elif test["outcome"] == "failed":
        print(f"❌ {test['nodeid']}")
        print(f"  {test['call']['crash']['message']}")


def get_points_from_test(test):
    """Get the pass points and fail points from a test.

    Args:
        test (dict): The test dictionary.

    Returns:
        tuple: A tuple containing the pass points and fail points.
    """

    pass_point, fail_point = 0, 0
    error_message = ""

    if test["outcome"] == "passed":
        pass_point = int(test["nodeid"][-1])
    elif test["outcome"] == "failed":
        fail_point = int(test["nodeid"][-1])
        error_message = test["call"]["crash"]["message"]

    return pass_point, fail_point, error_message


def mark_test(pass_points, fail_points, letter_grade=False):
    """Calculate the mark based on pass points and fail points.

    Args:
        pass_points (int): The total pass points.
        fail_points (int): The total fail points.
        letter_grade (bool, optional): Whether to return a letter grade. Defaults to False.

    Returns:
        str or float: The mark or letter grade.
    """

    if (pass_points + fail_points) == 0:
        return None
    else:
        grade = pass_points / (pass_points + fail_points)
        if letter_grade:
            if grade >= 0.9:
                return "A"
            elif grade >= 0.8:
                return "B"
            elif grade >= 0.7:
                return "C"
            elif grade >= 0.6:
                return "D"
            elif grade >= 0.51:
                return "E"
            else:
                return "F"
        else:
            return round(grade * 100, 2)


def get_test_points(tests):
    """Calculate the total pass points and fail points from a list of tests.

    Args:
        tests (list): A list of test dictionaries.

    Returns:
        tuple: A tuple containing the total pass points and fail points.
    """

    pass_points, fail_points = 0, 0
    error_message = []
    for test in tests:
        pass_point, fail_point, error_message = get_points_from_test(test)
        pass_points += pass_point
        fail_points += fail_point
    return pass_points, fail_points, error_message


def how_did_we_do(tests, print_to_terminal: bool):
    """Calculate the mark, pass points, and failed points from a list of tests.

    Args:
        tests (list): A list of test dictionaries.
        print_to_terminal (bool): Whether to print the summary to the terminal.

    Returns:
        dict: A dictionary containing the mark, pass points, and failed points.
    """

    pass_points, fail_points, error_message = get_test_points(tests)

    if print_to_terminal:
        for test in tests:
            print_summary(test)
        print(
            f"Grade: {mark_test(pass_points,fail_points,False)}, total_points: {pass_points} passed, {fail_points} failed"
        )

    return {
        "mark": mark_test(pass_points, fail_points, False),
        "pass_points": pass_points,
        "failed_points": fail_points,
        "error_message": error_message,
    }


if __name__ == "__main__":
    print(run_tests(1, "fake"))
