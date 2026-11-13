from marshmallow import Schema, fields, validate, ValidationError
from decimal import Decimal


class InvoiceSchema(Schema):

    id = fields.Int(dump_only=True)
    receipt_number = fields.Str(dump_only=True)
    date_created = fields.DateTime(dump_only=True)
    status = fields.Str(dump_only=True)

    unit_price = fields.Decimal(
        required=True,
        as_string=True,
        places=2,
        validate=validate.Range(min=Decimal("0.01"))
    )
    quantity = fields.Int(required=True, validate=validate.Range(min=1))

    customer_id = fields.Int(required=True, validate=validate.Range(min=1))
    product_id = fields.Int(required=True, validate=validate.Range(min=1))


invoice_schema = InvoiceSchema()
invoices_schema = InvoiceSchema(many=True)