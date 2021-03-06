from datetime import timedelta

import pytest

MIN_VALIDITY = 0


def get_seconds(days: int = 0, seconds: int = 0, minutes: int = 0, hours: int = 0, weeks: int = 0):
    return int(
        timedelta(
            days=days,
            seconds=seconds,
            minutes=minutes,
            hours=hours,
            weeks=weeks,
        ).total_seconds()
    )


testdata = [
    # validity, min, max, expected result
    # +1d, always, +1d+2h, always:+93600s
    (get_seconds(days=1), MIN_VALIDITY, get_seconds(days=1, hours=2), "always:+86400s"),
    # +6m, always, +7m, always:+360s
    (get_seconds(minutes=6), MIN_VALIDITY, get_seconds(minutes=7), "always:+360s"),
    # +5m, always, +5m, always:+300s
    (get_seconds(minutes=5), MIN_VALIDITY, get_seconds(minutes=5), "always:+300s"),
    # +1h, always, +66m, always:+3600s
    (get_seconds(hours=1), MIN_VALIDITY, get_seconds(minutes=66), "always:+3600s"),
    # +1d, always, +3m, always:+180s
    (get_seconds(days=1), MIN_VALIDITY, get_seconds(minutes=3), "always:+180s"),
    # +3d, always, +3m, always:+180s
    (get_seconds(days=3), MIN_VALIDITY, get_seconds(minutes=3), "always:+180s"),
    # +1d, -2d, +2d, -172800s:+86400s
    (get_seconds(days=1), get_seconds(days=2), get_seconds(days=2), "-172800s:+86400s"),
    # +1d, always, forever, always:+86400s
    (get_seconds(days=1), get_seconds(), get_seconds(), "always:+86400s"),
    # +4d, -1d, +1d, -86400s:+86400s
    (get_seconds(days=4), get_seconds(days=1), get_seconds(days=1), "-86400s:+86400s"),
    # 0, 0, 0, always:forever
    (get_seconds(), get_seconds(), get_seconds(), "always:forever"),
    # 0, 0, 86400, always:+86400s
    (0, 0, 86400, "always:+86400s"),
    # +119s, -1m, +1m, -120s:+119s
    (119, 120, 120, "-120s:+119s"),
]


@pytest.mark.parametrize("value, min, max, expected", testdata)
def test_validity_data(value, min, max, expected):
    from ssh_cert_service.utils.common import validity_data

    validity = validity_data(value, min, max)

    assert validity is not None
    assert validity == expected


def test_validity_fail():
    from ssh_cert_service.utils.common import validity_data

    with pytest.raises(Exception):
        validity_data("forever", 0, 3600)

    with pytest.raises(Exception):
        validity_data(-1, -1, 86400)

    with pytest.raises(Exception):
        validity_data(-1, -1, -1)

    with pytest.raises(Exception):
        validity_data(0, 0, -1)
