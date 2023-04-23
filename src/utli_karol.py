"""
This file contains some useful functions needed in my implementation
"""


def cleanup(line: [], lim: int = 16):
    """
    Formats the input
    Args:
        line: list of int obtained from input
        lim: upper limit of acceptable input, depended on the size of circuit, should be a power of 2

    Returns:
        list of the inputs, where all negative numbers, and number exceeding lim are skipped
    """
    return [num for num in line if 0 <= num < lim]


def private_func(name: str):
    """ Function done on private data, on the side of each parties.
        In the case of this exercise, the function returns max of given list.
        Execution starts with prompts.
        TODO: Accept input from file.
    Args:
        name: name of the party, used for convenience.

    Returns:
        local_max: maximum value of the input in cleaned binary form
                (e.i. without '0b' and filled with proceeding zeros).

    """
    print(f"Hello, this is {name}.")
    print("This program will compute max of given numbers.")
    print("Enter numbers seperated by spaces, end with new line.")
    print("Each number should be at most four bits, so less than 16.")

    line = [*map(int, input().split())]
    line = cleanup(line)
    local_max = bin(max(line))[2:].zfill(4)
    return local_max
