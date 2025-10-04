import re
import secrets
import string
from datetime import datetime

import bcrypt
import pandas as pd


def generate_password(length=8):
    chars = string.ascii_letters + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))


def hash_password(plain_password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(plain_password.encode('utf-8'), salt).decode('utf-8')


def set_allocation_status(serial_no: str):
    allocation_status = "UNASSIGNED"

    if serial_no == "Refunded":
        allocation_status = "REFUNDED"
    return allocation_status


def clean_address(address):
    if not address:
        return ""
    cleaned = re.sub(r'\s+', ' ', address)

    cleaned = re.sub(r'\s*,\s*', ', ', cleaned)

    cleaned = re.sub(r',\s*,+', ', ', cleaned)

    cleaned = cleaned.strip(" ,")

    return cleaned


def clean_mobile_number(number):
    if pd.isna(number):
        return ""
    number = str(number).strip()
    if number.endswith(".0"):
        number = number[:-2]
    number = number.strip()

    if number.startswith("+88"):
        number = number[3:]

    return number


def normalize_entry(entry):
    hajj_year = datetime.now().year + 1
    plain_password = generate_password()
    hashed_password = hash_password(plain_password)

    nid_value = entry.get("NID") or entry.get("nid") or None
    if nid_value is not None:
        nid_value = str(nid_value).strip()

    return {
        "name_bn": entry.get("Name (Bengali)", "").strip() if entry.get("Name (Bengali)") else entry.get("name_bn"),
        "name_en": entry.get("Name (English)", "").strip() if entry.get("Name (English)") else entry.get("name_en"),
        "father_name": entry.get("Father's Name") or entry.get("father_name"),
        "spouse_name": entry.get("Spouse Name") or entry.get("spouse_name"),
        "occupation": entry.get("Occupation") or entry.get("occupation"),
        "nid": nid_value,
        "voucher": entry.get("Voucher") or entry.get("voucher"),
        "type": entry.get("Type") or entry.get("type"),
        "listed_in": entry.get("Listed In") or entry.get("listed_in"),
        "mother_name": entry.get("Mother Name") or entry.get("mother_name"),
        "date_of_birth": entry.get("Date of Birth") or entry.get("date_of_birth"),
        "gender": entry.get("Gender") or entry.get("gender"),
        "management": entry.get("Management") or entry.get("management"),
        "mobile_no": clean_mobile_number(entry.get("Mobile") or entry.get("mobile_no")),
        "passport_address": clean_address(entry.get("Passport Address") or entry.get("passport_address")),
        "present_address": clean_address(entry.get("Present Address") or entry.get("present_address")),
        "permanent_address": clean_address(entry.get("Permanent Address") or entry.get("permanent_address")),
        "tracking_id": entry.get("Tracking ID") or entry.get("tracking_id"),
        "serial_no": entry.get("Serial No") or entry.get("serial_no"),
        "registration_status": "PREREGISTERED",
        "is_assigned": False,
        "hajj_year": hajj_year,
        "group_name": entry.get("Group Name") or entry.get("group_name"),
        "password": hashed_password,
        "preliminary_password": plain_password,
        "allocation_status": set_allocation_status(entry.get("Serial No") or entry.get("serial_no")),
        "vaccination_center": None,
        "nominee_info": None,
        "passport_copy": None,
        "package_id": None,
        "comment_on_package": None,
        "is_active": True
    }

def normalize_nid(val):
    if pd.isna(val) or str(val).lower() in ["none", "nan", "null", ""]:
        return ""
    return str(val).strip()