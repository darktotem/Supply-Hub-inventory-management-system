```
server/
├── app.py                  ← entry point (creates app, imports routes last)
├── config.py
├── extensions.py           ← db, migrate, bcrypt
├── schemas.py              ← marshmallow schemas
├── seed.py                 ← dev data (uses Faker)
├── Pipfile
├── Pipfile.lock
├── migrations/             ← created by flask db init
├── instance/
│   └── inventory.db        ← SQLite file, created by flask db upgrade
├── tests/
│
├── models/
│   ├── __init__.py         ← imports every model
│   ├── user.py             ← User, Role, ALL_ROLES
│   ├── product.py
│   ├── supplier.py         ← Supplier, SupplierProduct
│   ├── supply_history.py   ← SupplyOrder, SupplyItem
│   ├── customer.py
│   ├── customer_history.py ← CustomerOrder, CustomerOrderItem
│   ├── invoice.py
│   ├── report.py
│   └── audit_log.py
│
├── controllers/
│   ├── __init__.py         ← empty
│   ├── auth.py             ← login, change_password, change_username, recover_password
│   ├── employees.py        ← employees, register_employee, change_details,
│   │                         reset_password, recovery_code, deny_access,
│   │                         restore_access, delete_employee
│   ├── inventory.py        ← inventory (+ ?search=)
│   ├── supply.py           ← cancel_supply_order (more to come)
│   ├── warehouse.py        ← stub
│   ├── sales.py            ← stub
│   └── finance.py          ← stub
│
└── utils/
    ├── __init__.py         ← empty
    ├── constants.py        ← SupplyStatus, CustomerOrderStatus, PaymentStatus
    ├── decorators.py       ← login_required, roles_required, current_user
    ├── tokens.py           ← create_token, decode_token (PyJWT)
    ├── validators.py       ← load_json (marshmallow wrapper)
    ├── audit.py            ← log_action
    ├── stock.py            ← increase_stock, decrease_stock
    └── errors.py           ← JSON 404/405/500 handlers
```