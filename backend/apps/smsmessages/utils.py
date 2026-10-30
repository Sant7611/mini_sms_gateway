import re
import math

GSM_BASIC = set(
    "@£$¥èéùìòÇ\nØø\rÅåΔ_ΦΓΛΩΠΨΣΘΞÆæßÉ"
    " !\"#¤%&'()*+,-./0123456789:;<=>?¡"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÑÜ§¿"
    "abcdefghijklmnopqrstuvwxyzäöñüà"
)

GSM_EXTENDED = set("^{}\\[~]|€\f")


def normalize_phone(phone):
    pattern = r"(?:\+977|977)?(9[78][0-9]{8})"

    match = re.fullmatch(pattern, phone.strip())

    if not match:
        raise ValueError("Invalid Phone NUmber")

    return match.group(1)


def detect_encoding(message):

    if all(char in GSM_BASIC or char in GSM_EXTENDED for char in message):
        return "gsm7"

    return "unicode"


def calculate_parts(message):

    if not message or not message.strip():
        raise ValueError("SMSMessage cannot be empty")

    encoding = detect_encoding(message)

    if encoding == "gsm7":
        length = sum(2 if char in GSM_EXTENDED else 1 for char in message)
        single_limit = 160
        multi_limit = 153

    else:
        length = len(message.encode("utf-16-be")) // 2
        single_limit = 70
        multi_limit = 67

    if length <= single_limit:
        return 1

    return math.ceil(length / multi_limit)


def calculate_sms_cost(*, message, recipients):

    if not message or not message.strip():
        raise ValueError("SMSMessage cannot be empty")

    recipients_count = len(recipients)
    
    if recipients_count <= 0:
        raise ValueError("Recipients must not be empty")

    parts = calculate_parts(message)

    total_cost = parts * recipients_count

    return {
        "parts": parts,
        "cost_per_recipient": parts,
        "total_cost": total_cost,
    }
