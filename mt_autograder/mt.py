import subprocess
from regex_output import output_regex, sort_by_weight, get_mandatory_tests
from eval import eval, get_grade

log_name = "pytest.log"

# command to execute pytest and redirect the output
command = f"pytest -v -s --log-file={log_name}"

# execute the command and capture the output
result = subprocess.run(command, shell=True, capture_output=True, text=True)

# print the captured output (mostly for debugging purposes)
# print(result.stdout)

# write the captured output to a file
with open(f"{log_name}", "w") as log_file:
    log_file.write(result.stdout)

regex_output = output_regex(f'{log_name}')

if regex_output == {}:
    print("No tests run")
    exit()

# if no mandatory tests passed then score is 0
mandatory_tests = get_mandatory_tests(regex_output['FAILED'])
if len(mandatory_tests) > 0:
    print(f"Mandatory tests not passed{mandatory_tests}")
    exit()

# sort tests by weight
[sorted_by_weight_passed, weights_used_passed]= sort_by_weight(regex_output['PASSED'])
[sorted_by_weight_failed, weights_used_failed]= sort_by_weight(regex_output['FAILED'])

# calculate score
passed_score = eval(sorted_by_weight_passed, weights_used_passed)
failed_score = eval(sorted_by_weight_failed, weights_used_failed)
over_all_score = (passed_score/(passed_score+failed_score))*100

# print results
print(f"passed_score: {passed_score}, failed_score: {failed_score}, over_all_score: {over_all_score:.2f} %, grade: {get_grade(over_all_score)}")