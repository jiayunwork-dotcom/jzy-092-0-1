"""入参校验:任一参数不为正都必须带原因报错。"""

import pytest

from app import validation

BASE = dict(c0=100.0, flow=10.0, q0=50.0, k_th=0.005, mass=2000.0)


@pytest.mark.parametrize("field", validation.FIELDS)
@pytest.mark.parametrize("bad", [0.0, -1.0, -0.5])
def test_non_positive_rejected(field, bad):
    payload = {**BASE, field: bad}
    with pytest.raises(validation.ValidationError, match=field):
        validation.validate_case(payload)


@pytest.mark.parametrize("field", validation.FIELDS)
def test_missing_field_rejected(field):
    payload = {k: v for k, v in BASE.items() if k != field}
    with pytest.raises(validation.ValidationError, match=field):
        validation.validate_case(payload)


@pytest.mark.parametrize("field", validation.FIELDS)
@pytest.mark.parametrize(
    "bad", ["100", None, True, [1.0], float("nan"), float("inf")]
)
def test_non_numeric_or_nonfinite_rejected(field, bad):
    payload = {**BASE, field: bad}
    with pytest.raises(validation.ValidationError, match=field):
        validation.validate_case(payload)


def test_zero_feed_concentration_rejected():
    with pytest.raises(validation.ValidationError, match="c0"):
        validation.validate_case({**BASE, "c0": 0.0})


def test_non_dict_rejected():
    with pytest.raises(validation.ValidationError):
        validation.validate_case([1, 2, 3])


def test_valid_payload_normalized_and_extras_ignored():
    params = validation.validate_case({**BASE, "name": "x", "points": 50})
    assert params == {k: float(v) for k, v in BASE.items()}


def test_threshold_bounds():
    for bad in (0.0, 1.0, -0.1, 1.5):
        with pytest.raises(validation.ValidationError):
            validation.validate_threshold(bad)
    assert validation.validate_threshold(0.1) == pytest.approx(0.1)


def test_points_bounds():
    for bad in (1, 0, -3, 2.5, "100"):
        with pytest.raises(validation.ValidationError):
            validation.validate_points(bad)
    assert validation.validate_points(400) == 400
    assert validation.validate_points(400.0) == 400
