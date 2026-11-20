import random
from decimal import Decimal

from app import app
from extensions import db

from models.customer import Customer
from models.customer_history import CustomerHistory
from models.inventory import Inventory
from models.invoice import Invoice, Payment

from utils.finance import money, refresh_status, log_audit

NUM_INVOICES = 10
METHODS = ["cash", "mpesa", "bank", "card"]
CUSTOMERS = [
    {"customer_name": "Acme Traders", "contact": "0700000001"},
    {"customer_name": "Baraka Supplies", "contact": "0700000002"},
    {"customer_name": "Cheza Hardware", "contact": "0700000003"},
]


PRODUCTS = [
    {"product_name": "Cement 50kg", "category": "Building Materials", "quantity": 500, "threshold": 50, "price": 850.00},
    {"product_name": "Roofing Sheet", "category": "Roofing", "quantity": 300, "threshold": 30, "price": 1200.00},
    {"product_name": "Steel Rod 12mm", "category": "Steel", "quantity": 200, "threshold": 20, "price": 950.00},
]


def seed_customers():
    if Customer.query.count() >= 3:
        return
    for data in CUSTOMERS:
        db.session.add(Customer(**data))
    db.session.flush()


def seed_products():
    if Inventory.query.count() >= 3:
        return
    for data in PRODUCTS:
        db.session.add(Inventory(**data))
    db.session.flush()


def build_payment_plans(count):
    """Roughly 3 unpaid, 4 partly paid, 3 fully paid, in random order."""
    plans = ["none"] * 3 + ["partial"] * 4 + ["full"] * 3
    plans = (plans * (count // len(plans) + 1))[:count]
    random.shuffle(plans)
    return plans


def seed_invoices():
    seed_customers()
    seed_products()


    customers = Customer.query.all()
    products = Inventory.query.all()

    if not customers or not products:
        print("Seed at least one customer and one product first, then run this again.")
        return

    random.seed(42)  # same data every run; remove for fully random values

    created = []

    for plan in build_payment_plans(NUM_INVOICES):
        customer = random.choice(customers)
        product = random.choice(products)
        quantity = random.randint(1, 20)

        # Prices between 50.00 and 5000.00 in steps of 5.00
        unit_price = money(f"{Decimal(random.randrange(5000, 500001, 500)) / 100:.2f}")
        total = unit_price * quantity

        # The invoice must match an existing sale (same customer, product,
        # and not more than the sale's quantity and total), so create one.
        # Add status=... and date_of_sale=... here if your model requires them.
        sale = CustomerHistory(
            customer_id=customer.id,
            product_id=product.id,
            quantity=quantity,
            total_price=total,
        )
        db.session.add(sale)
        db.session.flush()

        invoice = Invoice(
            unit_price=unit_price,
            quantity=quantity,
            total=total,
            customer_id=customer.id,
            product_id=product.id,
            sale_id=sale.id,
        )
        db.session.add(invoice)
        db.session.flush()
        log_audit("invoice", invoice.id, "create", None, {"total": str(total), "sale_id": sale.id})

        if plan != "none":
            amount = total if plan == "full" else money(f"{total * Decimal('0.4'):.2f}")
            old = {"amount_paid": str(invoice.amount_paid), "status": invoice.status}

            payment = Payment(
                invoice_id=invoice.id,
                amount=amount,
                method=random.choice(METHODS),
                reference=f"SEED-{invoice.id}-1",
            )
            db.session.add(payment)
            invoice.amount_paid += amount
            refresh_status(invoice)
            db.session.flush()

            log_audit(
                "invoice",
                invoice.id,
                "payment",
                old,
                {
                    "amount_paid": str(invoice.amount_paid),
                    "status": invoice.status,
                    "payment_id": payment.id,
                    "payment_amount": str(amount),
                },
            )

        created.append(invoice)

    db.session.commit()

    print(f"Seeded {len(created)} invoices:")
    for inv in created:
        print(f"  #{inv.id}  total={inv.total}  paid={inv.amount_paid}  status={inv.status}")


if __name__ == "__main__":
    with app.app_context():
        try:
            seed_invoices()
        except Exception:
            db.session.rollback()
            raise