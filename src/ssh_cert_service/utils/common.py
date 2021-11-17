import re

def validity_data(validity: str, min: str, max: str) -> str:
    """
    Check the validity data and return the correct values

    :return: str with the correct validity strcuture
    """

    # System should define acceptable values such as 'minutes, hours, days, weeks'
    #       By default if something fails it will take the first of the list
    r_compare = r'[\+|\-](\d+)([mhdw]+)'

    # Check that the defined min is correct
    if min != 'always':
        min_r = re.search(r_compare, min, re.IGNORECASE)
        if not min_r:
            raise Exception("The Min configuration is incorrect pleas check value again")
        min = min_r.group()

    # Check that the defined max is correct
    if max != 'forever':
        max_r = re.search(r_compare, max, re.IGNORECASE)
        if not max_r:
            raise Exception("The Max configuration is incorrect pleas check value again")
        max = max_r.group()
    else:
        # If settings max is forever the is not need to check anything else
        return f"{min}:{max}"

    # Instance default output
    default = f"{min}:{max}"

    if not validity:
        return default

    # Match regex for the validity structure -1d:+1d
    regex = r'\+(\d+)([dwmh])'
    result = re.search(regex, validity, re.IGNORECASE)

    # If the regex does not match the two (int & str) values return default
    if not result or len(result.groups()) != 2:
        return default

    sys_value = int(max_r.group(1))
    sys_len = [char for char in max_r.group(2)]

    max_value = int(result.group(1))
    max_len = result.group(2)

    # Compare the coming data with the defined max validity in the system
    if max_len not in sys_len or max_value > sys_value:
        return default

    # If nothing fails return the request validity
    return f"{min}:{validity}"
