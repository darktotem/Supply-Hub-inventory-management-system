from marshmallow import Schema, fields, validate


class CustomerSchema(Schema):
    customer_name = fields.Str(
        required=True,
        validate=validate.Length(min=1),
    )
    contact = fields.Str(
        required=True,
        validate=validate.Regexp(
            r"^[0-9+\s-]{9,15}$",
            error="Enter a valid phone number.",
        ),
    )


class OrderSchema(Schema):
    customer_id = fields.Int(required=True)
    product_id = fields.Int(required=True)
    quantity = fields.Int(
        required=True,
        validate=validate.Range(min=1, error="Quantity must be at least 1."),
    )