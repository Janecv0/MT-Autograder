from HW import add


def test_add_positive_numbers_1():
    assert add(3, 5) == 8


def test_add_negative_numbers_1():
    assert add(-3, -5) == -8


def test_add_mixed_numbers_1():
    assert add(2, -5) == -3


def test_add_zero_1():
    assert add(0, 0) == 0


def test_add_large_numbers_1():
    assert add(10**10, 10**10) == 2 * 10**10
