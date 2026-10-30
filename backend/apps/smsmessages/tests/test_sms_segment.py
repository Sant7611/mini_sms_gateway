import pytest

from apps.smsmessages.utils import calculate_parts

@pytest.mark.parametrize(
    "message, expected_parts",
    [
        ("A" * 160, 1),
        ("A" * 161, 2),
        ("A" * 307, 3),
        ("{" * 81, 2),
        ("न" * 70, 1),
        ("न" * 71, 2),
        ("A" * 69 + "😊", 2),
    ],
)
def test_calculate_parts(message, expected_parts):
    assert calculate_parts(message) == expected_parts