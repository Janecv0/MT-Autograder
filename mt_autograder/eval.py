
def eval(test_dict:dict, weights_used:list):
    over_all_score = 0
    for weight in weights_used:
        over_all_score += score_counter(test_dict[weight], weight)

    return over_all_score


def score_counter(tests, test_weight):
    score = 0
    if len(tests) > 0:
        for _ in tests:
            score += int(test_weight)
    return score

def get_grade(score):
    if score >= 90:
        return 'A'
    elif score >= 80:
        return 'B'
    elif score >= 70:
        return 'C'
    elif score >= 60:
        return 'D'
    elif score >= 50:
        return 'E'
    else:
        return 'F'
    

