def int_to_roman(num: int) -> str:
    """Return the roman numeral equivalent of num."""
    val = [
        1000, 900, 500, 400,
        100, 90, 50, 40,
        10, 9, 5, 4,
        1
        ]
    syms = [
        "M", "CM", "D", "CD",
        "C", "XC", "L", "XL",
        "X", "IX", "V", "IV",
        "I"
        ]
    roman_num = ''
    i = 0
    while  num > 0:
        for _ in range(num // val[i]):
            roman_num += syms[i]
            num -= val[i]
        i += 1
    return roman_num

def int_to_letter(num) -> str:
    """Return the uppercase letter at the index num of the alphabet."""
    if 1 <= num <= 26:
        uppercase_letter = chr(num + 64)  # Adding 64 gives the ASCII value of 'A' for num=1
        return uppercase_letter
    else:
        return "?"

def f_range(start: float, stop: float, step: float):
    """Custom range for floats used in the creation of the grid. Python only has built in support for int ranges."""
    while start < stop:
        yield start
        start += step