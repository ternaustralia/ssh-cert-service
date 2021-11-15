from ssh_cert_service.utils.common import validity_data

VALIDITY = "-1d:+1d"

def test_validity_data():
    validity = validity_data(VALIDITY, "1d", "1d")

    assert validity is not None
    assert validity == VALIDITY

def test_fail_validity_data():
    value = "-4w:+6m"
    validity = validity_data(value, "1d", "1d")

    assert validity is not None
    assert validity != value

def test_different_validity_data():
    value = "-4d:+6m"
    validity = validity_data(value, "5d", "66m")

    assert validity is not None
    assert validity == "-4d:+6m"
