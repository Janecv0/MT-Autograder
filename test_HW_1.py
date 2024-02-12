import importlib
import os
import json

with open('hw_name.json') as f:
    hw_name = json.load(f)

os.remove('hw_name.json')

try:
    HW = importlib.import_module(hw_name['filename'])
except ImportError:
    print(f"Failed to import module {hw_name}.")


def test_1_5():
    assert HW.add(1, 2) == 3


def test_2_3():
    assert HW.add(1, 3) == 4


def test_3_3():
    assert HW.add(1, 4) == 4
