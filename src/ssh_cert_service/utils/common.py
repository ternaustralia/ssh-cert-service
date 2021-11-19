def validity_data(validity_request: int, validity_start: int, validity_end: int) -> str:
    """
    Check the validity time that the certificate will exprire

    :return: str with the correct validity strcuture
    """

    if not isinstance(validity_request, int):
        raise Exception("The validity request is not correct please check your inputs")

    if validity_start < 0 or validity_end < 0:
        raise Exception("The validity_start or validity_end cannot be negative values.")

    output_from = "always"
    #!a ^ !b => forever
    if not validity_request and not validity_end:
        output_to = "forever"
    #a ^ !b => a or #a < b => a
    elif (not validity_end and validity_request) or (validity_request and validity_request <= validity_end) :
        output_to = f"+{validity_request}s"
    #!a or a > b => b
    else:
        output_to = f"+{validity_end}s"

    # Instace the current time plus the validity_start
    if validity_start:
        output_from = f"-{validity_start}s"

    return f"{output_from}:{output_to}"
