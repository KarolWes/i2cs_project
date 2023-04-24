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


def private_func(name: str = "", bit_size: int = 16, file_read: bool = False, filename=None, data: list = []):
    """ Function done on private data, on the side of each parties.
        In the case of this exercise, the function returns max of given list.
        Function accepts the input from file or from console.
        In the later case, execution starts with prompts.
    Args:
        name: name of the party, used for convenience. (default is empty)
        bit_size: length of the numbers (in bits) allowed on input (default is 16)
        file_read: boolean determining if input is obtained from file or from console (default is false -> console)
        filename: path to the file with input data (only analysed when file_read is set to true)
        data: list of data to performa calculations on.
            If not empty, result is calculated on it, otherwise data is from input.
            Default is empty
    Returns:
        line: array of inputs
        local_max: maximum value of the input in cleaned binary form
                (i.e. without '0b' and filled with leading zeros).

    """
    if len(data) == 0:
        if not file_read:  # console
            print(f"Hello, this is {name}.")
            print("This program will compute max of given numbers.")
            print("Enter numbers seperated by spaces, end with new line.")
            print(f"Each number should be at most four bits, so less than {2 ** bit_size}.")
            line = [*map(int, input().split())]
        else:  # file
            try:
                f = open(filename, "r")
                print("Reading data from file")
                line = list(map(int, f.read().split(" ")))

            except FileNotFoundError:
                print("File does not exist")
                exit(10)
    else: # passed data
        line = data
    # common part, cleanup and calculation
    line = cleanup(line, lim=2 ** bit_size)
    local_max = bin(max(line))[2:].zfill(bit_size)
    return line, local_max


def circuit_output_to_int(d: dict):
    """
    Converts output from the circuit (after OT processing) and converts it to a number
    Args:
        d: dictionary of outputs {no_of_wire:bit}

    Returns:
        integer value of output
    """
    return int("".join(str(d[k]) for k in d.keys()), 2)
