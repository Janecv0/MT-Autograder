import subprocess
import json
from subprocess import DEVNULL


# Run pytest with --json-report option
def run_tests(test_n: int, user: str):
    """Run the tests and return the grade and the points."""

    # give the filename to the test file for the import
    json_filename = f"{user}_HW_{test_n}_report.json"
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

    # Read the report file
    with open(json_filename) as f:
        report_data = json.load(f)

    return how_did_we_do(report_data["tests"], False)


# Print the summary
def print_summary(test):
    if test["outcome"] == "passed":
        print(f"✅ {test['nodeid']}")

    elif test["outcome"] == "failed":
        print(f"❌ {test['nodeid']}")
        print(f"  {test['call']['crash']['message']}")


def get_points_from_test(test):
    pass_point, fail_point = 0, 0

    if test["outcome"] == "passed":
        pass_point = int(test["nodeid"][-1])

    elif test["outcome"] == "failed":
        fail_point = int(test["nodeid"][-1])

    return pass_point, fail_point


def mark_test(pass_points, fail_points, letter_grade=False):
    """ECTS grading system"""
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
    pass_points, fail_points = 0, 0
    for test in tests:
        pass_point, fail_point = get_points_from_test(test)
        pass_points += pass_point
        fail_points += fail_point
    return pass_points, fail_points


def how_did_we_do(tests, print_to_terminal: bool):
    pass_points, fail_points = get_test_points(tests)

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
    }


if __name__ == "__main__":
    print(run_tests(1, "fake"))
