from marshmallow import Schema, fields, validate

class SupplySchema(Schema):
    id = fields.Int(dump_only=True)

    name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=120)
    )

    contact_person = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=120)
    )

    phone = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=20)
    )

    email = fields.Email(
        required=True
    )

    address = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=255)
    )

class SupplyOrderSchema(Schema):
    product_id = fields.Int(
        required=True,
        validate=validate.Range(min=1)
    )

    supplier_id = fields.Int(
        required=True,
        validate=validate.Range(min=1)
    )

    quantity = fields.Int(
        required=True,
        validate=validate.Range(min=1)
    )

    date_of_order = fields.Date(
        required=True
    )

class CancelOrderStatusSchema(Schema):
    status = fields.Str(
        required=True,
        validate=validate.Oneof(['Cancelled'])
    )

class SupplyHistorySchema(Schema):
    id = fields.Int(dump_only=True)

    product_id = fields.Int(
        dump_only=True
    )

    supplier_id = fields.Int(
        dump_only=True
    )

    quantity = fields.Int(
        dump_only=True
    )

    date_of_order = fields.Date(
        dump_only=True
    )

    date_of_delivery = fields.Date(
        allow_none=True,
        dump_only=True
    )

    status = fields.Str(
        dump_only=True
    )

    supplier = fields.Nested(SupplySchema, dump_only=True)

supply_schema = SupplySchema()
supply_order_schema = SupplyOrderSchema()
cancel_order_status_schema = CancelOrderStatusSchema()
supply_history_schema = SupplyHistorySchema(many=True)