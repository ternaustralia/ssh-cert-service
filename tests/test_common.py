from ssh_cert_service.utils.common import validity_data

VALIDITY = "+1d"
MIN_VALIDITY = "always"

def test_validity_data():
    validity = validity_data(VALIDITY, MIN_VALIDITY, "1d")

    assert validity is not None
    assert validity == f"{MIN_VALIDITY}:{VALIDITY}"

def test_fail_validity_data():
    value = "+6m"
    validity = validity_data(value, MIN_VALIDITY, "1d")

    assert validity is not None
    assert validity != f"{MIN_VALIDITY}:{value}"

def test_different_validity_data():
    value = "+6m"
    validity = validity_data(value, MIN_VALIDITY, "66m")

    assert validity is not None
    assert validity == f"{MIN_VALIDITY}:{value}"
