"""GRmenu usage example: a calculator with a "Hard Mode" submenu.

Run it with: python example_calculator.py
"""
import math
import sys

import numpy as np

from GRmenu import GRmenu, GRSubMenu


class Calculator:

    def __init__(self):
        self.operator = "operator"
        self.nums = []

    def calculate(self, operator: str, nums=[]):
        self.operator = operator
        return self._operate(nums)

    def set_operator(self, operator: str):
        self.operator = operator

    def recolect(self):
        self.nums = []
        while True:
            try:
                num = float(input("Enter a number (or type 'done' to finish): "))
                self.nums.append(num)
            except ValueError:
                break
        return self.nums

    def _operate(self, nums=[]):
        if self.operator == "+":
            return self.add(nums)
        elif self.operator == "-":
            return self.subtract(nums)
        elif self.operator == "*":
            return self.multiply(nums)
        elif self.operator == "/":
            return self.divide(nums)
        else:
            raise ValueError("Invalid operator")

    def add(self, nums=[]):
        return sum(nums)

    def subtract(self, nums=[]):
        result = nums[0]
        for num in nums[1:]:
            result -= num
        return result

    def multiply(self, nums=[]):
        result = 1
        for num in nums:
            result *= num
        return result

    def divide(self, nums=[]):
        result = nums[0]
        for num in nums[1:]:
            if num == 0:
                raise ValueError("Cannot divide by zero")
            result /= num
        return result


class HardMode():
    def __init__(self, operator: str):
        if operator not in ["pow", "sqrt", "log", "fact", "inv", "det", "matmul"]:
            raise ValueError("Invalid operator")
        self.operator = operator

    def _operate(self, nums=[]):
        if self.operator == "pow":
            return self.power(nums)
        elif self.operator == "sqrt":
            return self.square_root(nums)
        elif self.operator == "log":
            return self.logarithm(nums)
        elif self.operator == "fact":
            return self.factorial(nums)
        elif self.operator == "inv":
            return self.matrix_inverse(nums)
        elif self.operator == "det":
            return self.matrix_determinant(nums)
        elif self.operator == "matmul":
            return self.matrix_multiply(nums[0], nums[1])
        else:
            raise ValueError("Invalid operator")

    def power(self, nums=[]):
        result = nums[0]
        for num in nums[1:]:
            result **= num
        return result

    def square_root(self, nums=[]):
        return [math.sqrt(num) for num in nums]

    def logarithm(self, nums=[]):
        return [math.log(num) for num in nums]

    def factorial(self, nums=[]):
        return [math.factorial(int(num)) for num in nums]

    def matrix_inverse(self, matrix):
        return np.linalg.inv(matrix)

    def matrix_determinant(self, matrix):
        return np.linalg.det(matrix)

    def matrix_multiply(self, matrix1, matrix2):
        return np.dot(matrix1, matrix2)


calculator = Calculator()


def read_matrix(name="matrix"):
    print(f"Enter the {name} row by row (numbers separated by spaces). Empty line to finish:")
    rows = []
    while True:
        line = input("> ").strip()
        if line == "":
            break
        rows.append([float(x) for x in line.split()])
    return rows


def _show_result(result):
    print(f"Result: {result}")
    input("Press Enter to return to the menu...")


def _show_error(error):
    print(f"Error: {error}")
    input("Press Enter to return to the menu...")


def exit_program():
    print("Goodbye!")
    sys.exit()


# --- Basic operations (Calculator) ------------------------------------------

def add_op():
    nums = calculator.recolect()
    _show_result(calculator.calculate("+", nums))


def subtract_op():
    nums = calculator.recolect()
    _show_result(calculator.calculate("-", nums))


def multiply_op():
    nums = calculator.recolect()
    _show_result(calculator.calculate("*", nums))


def divide_op():
    nums = calculator.recolect()
    try:
        result = calculator.calculate("/", nums)
    except ValueError as e:
        _show_error(e)
        return
    _show_result(result)


# --- Hard Mode, as a submenu -------------------------------------------------

def power_op():
    nums = calculator.recolect()
    _show_result(HardMode("pow")._operate(nums))


def square_root_op():
    nums = calculator.recolect()
    _show_result(HardMode("sqrt")._operate(nums))


def logarithm_op():
    nums = calculator.recolect()
    try:
        result = HardMode("log")._operate(nums)
    except ValueError as e:
        _show_error(e)
        return
    _show_result(result)


def factorial_op():
    nums = calculator.recolect()
    _show_result(HardMode("fact")._operate(nums))


def matrix_inverse_op():
    matrix = read_matrix("matrix")
    try:
        result = HardMode("inv")._operate(matrix)
    except np.linalg.LinAlgError as e:
        _show_error(e)
        return
    _show_result(result)


def matrix_determinant_op():
    matrix = read_matrix("matrix")
    _show_result(HardMode("det")._operate(matrix))


def matrix_multiply_op():
    m1 = read_matrix("first matrix")
    m2 = read_matrix("second matrix")
    try:
        result = HardMode("matmul")._operate([m1, m2])
    except ValueError as e:
        _show_error(e)
        return
    _show_result(result)


if __name__ == "__main__":
    # Hard Mode is a GRSubMenu: it's passed directly (no tuple) inside the
    # options list of the menu that contains it. Its panel opens
    # automatically on the right as soon as that row is highlighted (right
    # arrow or Enter moves focus in, left arrow moves back).
    hard_mode = GRSubMenu([
        ("Power", power_op, "Raises the first number to the following ones"),
        ("Square root", square_root_op, "Square root of each number"),
        ("Logarithm", logarithm_op, "Natural logarithm of each number"),
        ("Factorial", factorial_op, "Factorial of each number (integers)"),
        ("Matrix inverse", matrix_inverse_op, "Inverse of a square matrix"),
        ("Matrix determinant", matrix_determinant_op, "Determinant of a square matrix"),
        ("Matrix multiply", matrix_multiply_op, "Product of two matrices"),
    ], name="Hard Mode")

    menu = GRmenu(
        functions=[
            ("Add", add_op, "Adds all the entered numbers"),
            ("Subtract", subtract_op, "Subtracts the numbers in the entered order"),
            ("Multiply", multiply_op, "Multiplies all the entered numbers"),
            ("Divide", divide_op, "Divides the numbers in the entered order"),
            hard_mode,
            ("Exit", exit_program, "Closes the calculator"),
        ],
        title="Calculator",
        subtitle="A simple calculator with a hard mode",
        banner="CALC",
        center=True,
        divider=True,
        font=1,
        searchable=True,
        style=9,
        animate="rgb",
    )
    menu.draw()
