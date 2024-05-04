from HW import add


def test_add_positive_numbers():
    assert add(3, 5) == 8

def test_add_negative_numbers():
    assert add(-3, -5) == -8

def test_add_mixed_numbers():
    assert add(2, -5) == -3

def test_add_zero():
    assert add(0, 0) == 0

def test_add_large_numbers():
    assert add(10**10, 10**10) == 2 * 10**10
