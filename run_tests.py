import io
import tarfile
import json
import os
import docker
import re

re_points = re.compile(r"_\d+")
re_numeric = re.compile(r"\d+")


def run_tests(test_n: int, user: int):
    """
    Run tests for a specific homework assignment.

    Args:
        test_n (int): The test number.
        user (int): The user ID.

    Returns:
        dict: A dictionary containing the test results.

    Raises:
        FileNotFoundError: If the homework file or test file does not exist.

    """
    # Rest of the code...


def run_tests(test_n: int, user: int):

    HW_folder = "./HW"
    json_filename = f"HW_{test_n}_{user}_report.json"
    json_filename_with_path = os.path.join(HW_folder, json_filename)
    hw_filename = f"HW_{test_n}_{user}.py"
    hw_filename_with_path = os.path.join(HW_folder, hw_filename)
    test_filename = f"test_HW_{test_n}.py"
    test_filename_with_path = os.path.join("TESTS", test_filename)

    if not os.path.isfile(hw_filename_with_path):
        print(f"File {hw_filename_with_path} does not exist")

    elif not os.path.isfile(test_filename_with_path):
        print(f"File {test_filename_with_path} does not exist")

    else:
        create_and_run_container(
            test_filename_with_path, hw_filename_with_path, json_filename, []
        )

    os.replace(json_filename, json_filename_with_path)

    with open(json_filename_with_path) as f:
        report_data = json.load(f)

    results = how_did_we_do(report_data["tests"], False)

    return results


def print_summary(test):
    """
    Print the summary of a test.

    Args:
        test (dict): The test dictionary.
    """

    if test["outcome"] == "passed":
        print(f"✅ {test['nodeid']}")
    elif test["outcome"] == "failed":
        print(f"❌ {test['nodeid']}")
        print(f"  {test['call']['crash']['message']}")


def get_points_from_test(test):
    """
    Extracts the pass points, fail points, and error message from a test.

    Args:
        test (dict): A dictionary representing a test.

    Returns:
        tuple: A tuple containing the pass points, fail points, and error message.

    Raises:
        ValueError: If the test name is invalid.

    """
    pass_point, fail_point = 0, 0
    error_message = ""
    try:
        if test["outcome"] == "passed":
            pass_point = re_points.findall(test["nodeid"])[-1]
            if pass_point is not None:
                pass_point = int(re_numeric.findall(pass_point)[0])
        elif test["outcome"] == "failed":
            fail_point = re_points.findall(test["nodeid"])[-1]
            if fail_point is not None:
                fail_point = int(re_numeric.findall(fail_point)[0])
                error_message = test["call"]["crash"]["message"]
            else:
                error_message = "Invalid test name, contact the teacher."
    except ValueError:
        return 0, 0, "Invalid test name, contact the teacher."

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
    """
    Calculate the total pass points and fail points from a list of tests.

    Args:
        tests (list): A list of test dictionaries.

    Returns:
        tuple: A tuple containing the total pass points and fail points.
    """

    pass_points, fail_points = 0, 0
    error_messages = []
    for test in tests:
        pass_point, fail_point, error_message = get_points_from_test(test)
        pass_points += pass_point
        fail_points += fail_point
        if error_message != "":
            error_messages.append(error_message)
    return pass_points, fail_points, error_messages


def how_did_we_do(tests, print_to_terminal: bool):
    """
    Calculate the mark, pass points, and failed points from a list of tests.

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


def create_and_run_container(
    test_file: str, HW_file: str, json_filename: str, packages_to_install: list
):
    """
    Create a Docker container and run the tests inside it.

    Args:
        test_file (str): path to the test file
        HW_file (str): path to the HW file
        json_filename (str): json file name
        packages_to_install (list): list of packages to install
    """

    client = docker.from_env()

    # Define the base Docker image
    base_image = "python:latest"

    # Create a new rootless Docker container
    container = client.containers.create(
        base_image,
        command="tail -f /dev/null",  # Keep the container running
        detach=True,
        privileged=False,
    )

    try:
        # Copy the Python file into the container
        container.put_archive("/", create_tar(test_file, 0))
        container.put_archive("/", create_tar(HW_file, 1))

        # Get file name from the path
        test_file = test_file.split("\\")[-1]
        HW_file = HW_file.split("\\")[-1]

        # Start the container
        container.start()

        # Install required packages inside the container
        for package in packages_to_install:
            install_command = f"pip install {package}"
            container.exec_run(install_command)

        container.exec_run("pip install pytest")
        container.exec_run("pip install pytest-json-report --upgrade")

        # Execute the Python file inside the container

        container.exec_run(
            f"pytest test_HW.py -q --json-report --json-report-file={json_filename}"
        )

        # Get the report.json file from the container
        bits, _ = container.get_archive(f"/{json_filename}")
        bits_data = b"".join(bits)

        # Convert the bits to a tarfile
        tar_file = tarfile.open(fileobj=io.BytesIO(bits_data))

        # Extract the report.json file from the tarfile
        tar_file.extractall()

    except Exception as e:
        print(e)

    # Stop and remove the container
    container.stop()
    container.remove()


def create_tar(file_path: str, is_HW: bool) -> bytes:
    """Create a tar archive from a file.

    Args:
        file_path (str): file name

    Returns:
        bytes: tar archive as bytes
    """

    with open(file_path, "rb") as file:
        file_data = file.read()
    tarstream = io.BytesIO()
    tar = tarfile.TarFile(fileobj=tarstream, mode="w")
    if is_HW:
        tarinfo = tarfile.TarInfo(name="HW.py")
    else:
        tarinfo = tarfile.TarInfo(name="test_HW.py")
    tarinfo.size = len(file_data)
    tar.addfile(tarinfo, io.BytesIO(file_data))
    tar.close()
    return tarstream.getvalue()
