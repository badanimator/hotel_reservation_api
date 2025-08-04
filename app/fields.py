from marshmallow import fields, ValidationError
import phonenumbers
from phonenumbers import format_number, PhoneNumberFormat
import humanize




class HumanTime(fields.Field):
    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return None
        return humanize.naturaltime(value)
    

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
    