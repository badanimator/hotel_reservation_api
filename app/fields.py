from marshmallow import fields, ValidationError
import phonenumbers
from phonenumbers import format_number, PhoneNumberFormat
import humanize
from datetime import datetime
import re
from app.constant import Regex


class HumanTime(fields.Field):
    def _serialize(self, value, attr, obj, **kwargs):
        if value and isinstance(value, datetime):
            return humanize.naturaltime(value)
        return None
    
class EmailField(fields.Field):
    def _deserialize(self, value, attr, data, **kwargs):
        if not re.match(Regex.EMAIL, value):
            raise ValidationError("Not a valid email address.")
        
        return value.strip().lower()

    def _serialize(self, value, attr, obj, **kwargs):
        return value

class PhoneNumberField(fields.Field):
    def _deserialize(self, value, attr, data, **kwargs):
        try:
            number = phonenumbers.parse(value, "GH")
            fullnumber = format_number(number, PhoneNumberFormat.E164)
            if not phonenumbers.is_valid_number(number):
                raise ValidationError("Invalid phone number.")
            return fullnumber
        except Exception:
            raise ValidationError("Invalid phone number format.")

    def _serialize(self, value, attr, obj, **kwargs):
        try:
            number = phonenumbers.parse(value, "GH")
            fullnumber = format_number(number, PhoneNumberFormat.E164)
            return fullnumber
        except Exception:
            return value  # fallback
    