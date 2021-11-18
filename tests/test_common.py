import pytest
from datetime import timedelta

VALIDITY = "+1d"
MIN_VALIDITY = 0

def get_seconds(
    days: int = 0,
    seconds: int = 0,
    minutes: int = 0,
    hours: int = 0,
    weeks: int = 0):
    return int(timedelta(
        days=days,
        seconds=seconds,
        minutes=minutes,
        hours=hours,
        weeks=weeks,
    ).total_seconds())


validity_settings = [
    get_seconds(days=1, hours=2), #0
    get_seconds(minutes=7),       #1
    get_seconds(minutes=5),       #2
    get_seconds(minutes=66),      #3
    get_seconds(minutes=3),       #4
    get_seconds(minutes=3),       #5
    get_seconds(days=2),          #6
    get_seconds(days=1),          #7
]

input_validity = [
    get_seconds(days=1),    #0
    get_seconds(minutes=6), #1
    get_seconds(minutes=5), #2
    get_seconds(hours=1),   #3
    get_seconds(days=1),    #4
    get_seconds(days=3),    #5
    get_seconds(days=1),    #6
    get_seconds(days=1),    #7
    get_seconds(days=4),    #8
]


testdata = [
    # validity, min, max, expected result
    # +1d, always, +1d+2h, always:+1440m
    (input_validity[0], MIN_VALIDITY, validity_settings[0], "always:+1440m"),
    # +6m, always, +7m, always:+6m
    (input_validity[1], MIN_VALIDITY, validity_settings[1], "always:+6m"),
    # +5m, always, +5m, always:+5m
    (input_validity[2], MIN_VALIDITY, validity_settings[2], "always:+5m"),
    # +1h, always, +66m, always:+60m
    (input_validity[3], MIN_VALIDITY, validity_settings[3], "always:+60m"),
    # +1d, always, +3m, always:+3m
    (input_validity[4], MIN_VALIDITY, validity_settings[4], "always:+3m"),
    # +3d, always, +3m, always:+3m
    (input_validity[5], MIN_VALIDITY, validity_settings[5], "always:+3m"),
    # +1d, -2d, +2d, -2880m:+1440m
    (input_validity[6], validity_settings[6], validity_settings[6], "-2880m:+1440m"),
    # +1d, always, forever, always:forever
    (input_validity[7], get_seconds(), get_seconds(), "always:forever"),
    # +4d, -1d, +1d, -1440m:+1440m
    (input_validity[8], validity_settings[7], validity_settings[7], "-1440m:+1440m"),
]


@pytest.mark.parametrize("value, min, max, expected", testdata)
def test_validity_data(value, min, max, expected):
    from ssh_cert_service.utils.common import validity_data

    validity = validity_data(value, min, max)

    assert validity is not None
    assert validity == expected
