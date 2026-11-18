from marshmallow import Schema, fields, validate, ValidationError
from decimal import Decimal


class InvoiceSchema(Schema):

=======
class InvoiceSchema(Schema):
    id = fields.Int(dump_only=True)
    receipt_number = fields.Str(dump_only=True)
    date_created = fields.DateTime(dump_only=True)
    status = fields.Str(dump_only=True)
=======
    amount_paid = fields.Decimal(dump_only=True, as_string=True, places=2)
    balance_due = fields.Function(lambda inv: str(inv.total - inv.amount_paid), dump_only=True)

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
=======
        validate=validate.Range(min=Decimal("0.01")),
    )
    quantity = fields.Int(required=True, validate=validate.Range(min=1))
    total = fields.Decimal(as_string=True, places=2) 

    customer_id = fields.Int(required=True, validate=validate.Range(min=1))
    product_id = fields.Int(required=True, validate=validate.Range(min=1))
    sale_id = fields.Int(required=True, validate=validate.Range(min=1))


class PaymentSchema(Schema):
    id = fields.Int(dump_only=True)
    invoice_id = fields.Int(dump_only=True)
    paid_at = fields.DateTime(dump_only=True)
    amount = fields.Decimal(required=True, as_string=True, places=2, validate=validate.Range(min=Decimal("0.01")))
    method = fields.Str(load_default="cash", validate=validate.OneOf(["cash", "mpesa", "bank", "card"]))
    reference = fields.Str(allow_none=True, validate=validate.Length(max=64))


invoice_schema = InvoiceSchema()
invoices_schema = InvoiceSchema(many=True)
payment_schema = PaymentSchema()
payments_schema = PaymentSchema(many=True)
