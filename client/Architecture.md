```bash
ROUTES

>> AUTHENTICATION (login/registering)
        /auth
           login.jsx


>> OPERATIONS DIRECTOR (admin)
    1. view inventory
    2. view supply history
    3. view sales history
    4. approve/cancel supply orders from procurement officer
    5. set stock thresholds

>> AN IT 
    manage employees (register, delete, patch records)


>> PROCUREMENT OFFICER (suppliers)
    1. view inventory
    2. view supply history/orders
    4. manage suppliers (create, delete)
    3. manage supply orders (create, cancel)   --> supply history

>> STORE WORKER
    1. view inventory
    2. view supply orders/history
    3. manage deliveries(mark orders as delivered, adding new product)(create new, patch existing)
    4. give reports about inventory

>> SALES OFFICER (customers)
    1. view inventory
    2. manage customers (create, delete)
    3. manage customer orders (create, cancel) --moves to sales history

>> FINANCE OFFICER (payments)
    1. view sales history
    2. view supply history
    3. manage invoices
    4. manage payments (mark it as paid)
  

COMPONENTS


components
    navbar.jsx

features
    auth/
      login.jsx

    admin/
      employees.jsx
    
    inventory/
      inventory.jsx

    supply/
      history.jsx
      supply_orders.jsx
      reg_suppliers.jsx

    warehouse/
      deliveries.jsx
      add_product.jsx
      reports.jsx

    sales/
      customers.jsx
      customer_orders.jsx

    finance/
      invoices.jsx
      payments.jsx

    auditor/
      audit_dashboard.jsx
      
routes

api
hooks
app.jsx
main.css

'''
components
    navbar.jsx

features
    auth/
      login.jsx

    admin/
      employees.jsx
    
    inventory/
      inventory.jsx

    supply/
      history.jsx
      supply_orders.jsx
      reg_suppliers.jsx

    warehouse/
      deliveries.jsx
      add_product.jsx
      reports.jsx

    sales/
      customers.jsx
      customer_orders.jsx

    finance/
      invoices.jsx
      payments.jsx

    auditor/
      audit_dashboard.jsx

BACK-END
models
1. inventory (product details)
2. employees (users)
3. suppliers
4. supply_history
5. customers (sales)
6. customer_orders
7. payment_invoices & history
8. 

(routes fetch are)
```

