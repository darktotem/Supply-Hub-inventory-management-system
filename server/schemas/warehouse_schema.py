from marshmallow import Schema, fields, validate


class WarehouseProductSchema(Schema):
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


class WarehouseProductUpdateSchema(Schema):
    product_name = fields.Str(
        validate=validate.Length(min=1, max=150)
    )

    category = fields.Str(
        validate=validate.Length(min=1, max=100)
    )

    quantity = fields.Int(
        validate=validate.Range(min=0)
    )

    threshold = fields.Int(
        validate=validate.Range(min=0)
    )

    price = fields.Float(
        validate=validate.Range(min=0)
    )


warehouse_product_schema = WarehouseProductSchema()
warehouse_product_update_schema = WarehouseProductUpdateSchema()