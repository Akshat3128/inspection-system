from marshmallow import Schema, fields, validates, ValidationError
import re

class InspectionSchema(Schema):
    vehicle_number = fields.Str(required=True)
    damage_report = fields.Str(required=True)
    image_url = fields.Url(required=True)

    @validates("image_url")
    def validate_image_url(self, value):
        if not re.match(r".*\.(jpg|jpeg|png)$", value, re.IGNORECASE):
            raise ValidationError("Image URL must end with .jpg, .jpeg or .png")
