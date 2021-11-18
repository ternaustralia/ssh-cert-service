import re
from datetime import timedelta, datetime


def validity_data(validity_request: int, validity_start: int, validity_end: int) -> str:
    """
    Check the validity time that the certificate will exprire

    :return: str with the correct validity strcuture
    """

    if not isinstance(validity_request, int):
        raise Exception("The validity request is not correct please check your inputs")

    current_time = datetime.today()

    # Work with timedelta and add the validity_request in seconds
    validity_request = timedelta(seconds=validity_request)

    if validity_request.total_seconds() <= validity_end:
        # Get the total of seconds between the difference of the current time and future time
        seconds = int(((current_time + validity_request) - current_time).total_seconds())
        output_to = f"+{seconds}s"
    # If the validity request fails then work with the settings values
    elif validity_end:
        output_to = f"+{validity_end}s"
    # If the settings are empty it means forever
    else:
        output_to = "forever"

    # Instace the current time plus the validity_start
    if validity_start:
        output_from = f"-{validity_start}s"
    # If the settings are empty it means always
    else:
        output_from = "always"

    return f"{output_from}:{output_to}"
