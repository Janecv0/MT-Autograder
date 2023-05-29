import pytest

def add(a,b):
    return a+b

def sub(a,b):
    return a-b

# Testing:
# use this test naming convention: test_<name of test>_<test weight>_<mandatory>
# eg. test_add_1_mandatory

@pytest.mark.skip(reason="no way of currently testing this")
def test_add_1():
    assert add(3,2) == 5

def test_add2_1_mandatory():
    assert add(3,3) == 6

def test_add3_3():
    assert add(2,2) == 5

def test_add4_4():
    assert add(0,2) == 2

def test_add5_4():
    assert add(0,2) == 2

def test_add6_2():
    assert add(1,2) == 2

def test_sub1_1():
    assert sub(3,2) == 1

def test_sub2_2(): 
    assert sub(3,3) == 0

def test_sub3_3(): 
    assert sub(2,-2) == 4


