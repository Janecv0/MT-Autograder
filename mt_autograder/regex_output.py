import re

def output_regex(file_name:str):
    # load log file into a string
    with open(file_name, 'r') as myfile:
        data=myfile.read()

    # regexes
    re_collected = re.compile(r'collected\s')
    re_eq = re.compile(r'\s\s==')
    re_items = re.compile(r'items\s\s')
    re_colon = re.compile(r'::')
    re_new_line = re.compile(r'\n')
    re_ws = re.compile(r'\s')

    # regex match
    match = re_collected.search(data)
    match2 = re_eq.search(data)

    # tests with whitespaces and numebr of tests
    tests_run = data[match.span()[1]:match2.span()[0]+2]
    number_of_tests = int(tests_run[0])

    if number_of_tests == 0:
        return {}

    match3 = re_items.search(tests_run)

    # tests without whitespaces
    tests = tests_run[match3.span()[1]:]

    test_with_results = []

    for _ in range(number_of_tests):
        # divide tests
        match4 = re_colon.search(tests)
        match5 = re_new_line.search(tests)
        test_with_results.append(tests[match4.span()[1]:match5.span()[0]])
        tests = tests[match5.span()[1]:]


    test_dict = {}

    for test in test_with_results:
        # for each run in test_with_results list devide into test name and result
        match6 = re_ws.search(test)
        test_name = test[:match6.span()[0]]
        test_result = test[match6.span()[1]:]

        # make dictionary with test result as key and list of test_name as value
        if test_result in test_dict:
            test_dict[test_result].append(test_name)
        else:
            test_dict[test_result] = [test_name]

    print(test_dict)
    return test_dict

def get_mandatory_tests(test_dict:dict):
    # get test which include '_mandatory' in test name
    re_mandatory = re.compile(r'_mandatory')
    mandatory_tests = []
    for test in test_dict:
        match = re_mandatory.search(test)
        if match:
            mandatory_tests.append(test)
    return mandatory_tests

def sort_by_weight(test_dict:dict):
    # sort test_dict by weight
    re_weight = re.compile(r'_\d')

    passed_test_dict_sorted = {}
    score_used = []

    for test in test_dict:
        match = re_weight.search(test)
        weight = test[match.span()[0]+1]
        
        if weight in passed_test_dict_sorted:
            passed_test_dict_sorted[weight].append(test)
        else:
            passed_test_dict_sorted[weight] = [test]
            score_used.append(weight)

    return [passed_test_dict_sorted, score_used]




