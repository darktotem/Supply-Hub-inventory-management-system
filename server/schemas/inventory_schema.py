from marshmallow import Schema, fields, validate


class InventorySchema(Schema):
    id = fields.Int(dump_only=True)

    product_name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=150)
    )

    category = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=100)
    )

    quantity = fields.Int(
        required=True,
        validate=validate.Range(min=0)
    )

    threshold = fields.Int(
        required=True,
        validate=validate.Range(min=0)
    )

    price = fields.Float(
        required=True,
        validate=validate.Range(min=0)
    )