import re

def validity_data(validity: str, min: str, max: str) -> str:
    """
    Check the validity data and return the correct values

    :return: str with the correct validity strcuture
    """
    default = f"-{min}:+{max}"
    if not validity:
        return default

    # Match regex for the validity structure -1d:+1d
    regex = r'\-(\d+)([dwm])\:\+(\d+)([dwm])'
    result = re.search(regex, validity, re.IGNORECASE)

    # If the regex does not match the four values return default
    if not result or len(result.groups()) != 4:
        return default

    r_compare = r'(\d+)([dwm])'
    compare = re.search(r_compare, min, re.IGNORECASE)

    min_value = int(result.group(1))
    min_len = result.group(2)

    # Compare the coming data with the defined min validity in the system
    if min_value > int(compare.group(1)) or min_len != compare.group(2):
        return default

    compare = re.search(r_compare, max, re.IGNORECASE)
    max_value = int(result.group(3))
    max_len = result.group(4)

    # Compare the coming data with the defined max validity in the system
    if max_value > int(compare.group(1)) or max_len != compare.group(2):
        return default

    # If nothing fails return the request validity
    return validity


