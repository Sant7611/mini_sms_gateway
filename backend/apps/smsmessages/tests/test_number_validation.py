import pytest

from apps.smsmessages.utils import normalize_phone


@pytest.mark.parametrize(
    "phone, expected",
    [
        ("9841234567", "9841234567"),
        ("9801122334", "9801122334"),
        ("9761234567", "9761234567"),
        ("+9779801122334", "9801122334"),
        ("9779761234567", "9761234567"),
        (" +9779801122334 ", "9801122334"),
    ],
)
def test_phone_number_validation(phone, expected):
    assert normalize_phone(phone) == expected


@pytest.mark.parametrize(
    "phone",
    [
        "9612345678",  
        "984123456",   
        "98412345678", 
        "abcdefghij",  
    ],
)
def test_invalid_phone_numbers(phone):
    with pytest.raises(ValueError):
        normalize_phone(phone)
        
        