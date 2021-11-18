import pytest

VALIDITY = "+1d"
MIN_VALIDITY = "always"

testdata = [
    # validity, min, max, expected result
    ("+1d", MIN_VALIDITY, "+1d", "always:+1d"),
    ("+6m", MIN_VALIDITY, "+7dm", "always:+6m"),
    ("+6m", MIN_VALIDITY, "+66m", "always:+6m"),
    # FIXME: 1h < 66m .... is 66m even allowed? or should this turn into 1h6m ?
    ("+1h", MIN_VALIDITY, "+66mh", "always:+1h"),
    # FIXME: +1d < 3m .... should not fail
    ("+1d", MIN_VALIDITY, "+3md", "always:+1d"),
    # FIXME: validity and max should use the same format
    ("+3d", MIN_VALIDITY, "+4md", "always:+3d"),
    # FIXME: API allows passing min validity let's see what happens
    #        which format to use value or max?
    ("+1d", "-2d", "+2d", "-2d:+1d"),
    ("+1d", "-2d", "+2d", "-2d:+1d"),
    ("+1d", "always", "forever", "always:forever"),
    ("+4d", "-2dmhw", "+2mhdw", "-2d:+2m"),
]


@pytest.mark.parametrize("value, min, max, expected", testdata)
def test_validity_data(value, min, max, expected):
    from ssh_cert_service.utils.common import validity_data

    validity = validity_data(value, min, max)

    assert validity is not None
    assert validity == expected
