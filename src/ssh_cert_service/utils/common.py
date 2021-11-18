import re
from datetime import timedelta, datetime


def validity_data(validity_request: int, validity_start: int, validity_end: int) -> str:
    """
    Check the validity time that the certificate will exprire

    :return: str with the correct validity strcuture
    """

    if not isinstance(validity_request, int):
        raise Exception("The validity request is not correct please check your inputs")

    output_to = f"+{validity_end}s"
    output_from = "always"

    if not validity_end or validity_request <= validity_end:
        # If the settings are empty it means forever
        output_to = f"+{validity_request}s" if validity_request else "forever"

    # Instace the current time plus the validity_start
    if validity_start:
        output_from = f"-{validity_start}s"

    return f"{output_from}:{output_to}"
