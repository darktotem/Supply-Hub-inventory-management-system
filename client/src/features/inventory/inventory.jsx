
import { useMemo, useState } from "react";

const initialForm = {
  product_name: "",
  category: "",
  quantity: "",
  threshold: "10",
  price: "",
};

/**
 * @typedef {Object} Product
 * @property {number} id
 * @property {string} product_name
 * @property {string} category
 * @property {number} quantity
 * @property {number} threshold
 * @property {number} price
 */

/**
 * @typedef {Object} ProductForm
 * @property {string} product_name
 * @property {string} category
 * @property {string} quantity
 * @property {string} threshold
 * @property {string} price
 */

/**
 * @param {number|string} price
 */
function formatPrice(price) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "KSH",
  }).format(Number(price || 0));
}

function Inventory() {
  const [products, setProducts] = useState(
    /** @type {Product[]} */ ([])
  );

  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("all");
  const [stockFilter, setStockFilter] = useState("all");

  const [showModal, setShowModal] = useState(false);

  const [editingProduct, setEditingProduct] = useState(
    /** @type {Product | null} */ (null)
  );

  const [form, setForm] = useState(
    /** @type {ProductForm} */ (initialForm)
  );

  // Get unique product categories
  const categories = useMemo(() => {
    return [...new Set(products.map((product) => product.category))]
      .filter(Boolean)
      .sort();
  }, [products]);

  // Search and filter products
  const filteredProducts = useMemo(() => {
    return products.filter((product) => {
      const matchesSearch = product.product_name
        .toLowerCase()
        .includes(search.toLowerCase());

      const matchesCategory =
        category === "all" || product.category === category;

      const matchesStock =
        stockFilter === "all" ||
        (stockFilter === "available" && product.quantity > product.threshold) ||
        (stockFilter === "low" && product.quantity <= product.threshold) ||
        (stockFilter === "out" && product.quantity === 0);

      return matchesSearch && matchesCategory && matchesStock;
    });
  }, [products, search, category, stockFilter]);

  // Inventory statistics
  const totalProducts = products.length;

  const totalStock = products.reduce(
    (total, product) => total + product.quantity,
    0
  );

  const lowStockProducts = products.filter(
    (product) => product.quantity <= product.threshold
  ).length;

  const outOfStockProducts = products.filter(
    (product) => product.quantity === 0
  ).length;

  const inventoryValue = products.reduce(
    (total, product) => total + product.price * product.quantity,
    0
  );

  // Open add product modal
  const openAddModal = () => {
    setEditingProduct(null);
    setForm({ ...initialForm });
    setShowModal(true);
  };

  // Open edit product modal
  /**
   * @param {Product} product
   */
  const openEditModal = (product) => {
    setEditingProduct(product);

    setForm({
      product_name: product.product_name,
      category: product.category,
      quantity: String(product.quantity),
      threshold: String(product.threshold),
      price: String(product.price),
    });

    setShowModal(true);
  };

  // Handle form input
  /**
   * @param {React.ChangeEvent<HTMLInputElement>} event
   */
  const handleChange = (event) => {
    const { name, value } = event.target;

    setForm((previous) => ({
      ...previous,
      [name]: value,
    }));
  };

  // Add or update product
  /**
   * @param {React.FormEvent<HTMLFormElement>} event
   */
  const handleSubmit = (event) => {
    event.preventDefault();

    const productData = {
      product_name: form.product_name.trim(),
      category: form.category.trim(),
      quantity: Number(form.quantity),
      threshold: Number(form.threshold),
      price: Number(form.price),
    };

    if (
      !productData.product_name ||
      !productData.category ||
      form.quantity === "" ||
      form.threshold === "" ||
      form.price === "" ||
      !Number.isInteger(productData.quantity) ||
      productData.quantity < 0 ||
      !Number.isInteger(productData.threshold) ||
      productData.threshold < 0 ||
      !Number.isFinite(productData.price) ||
      productData.price < 0
    ) {
      alert("Please enter valid product details.");
      return;
    }

    if (editingProduct) {
      setProducts((previous) =>
        previous.map((product) =>
          product.id === editingProduct.id
            ? { ...product, ...productData }
            : product
        )
      );
    } else {
      const newProduct = {
        id: Date.now(),
        ...productData,
      };

      setProducts((previous) => [newProduct, ...previous]);
    }

    setShowModal(false);
    setEditingProduct(null);
    setForm({ ...initialForm });
  };

  // Delete product
  /**
   * @param {number} id
   * @param {string} productName
   */
  const handleDelete = (id, productName) => {
    const confirmed = window.confirm(
      `Are you sure you want to delete "${productName}"?`
    );

    if (!confirmed) return;

    setProducts((previous) =>
      previous.filter((product) => product.id !== id)
    );
  };

  // Stock status
  /**
   * @param {number} quantity
   * @param {number} threshold
   */
  const getStockStatus = (quantity, threshold) => {
    if (quantity === 0) {
      return { label: "Out of stock", className: "out" };
    }

    if (quantity <= threshold) {
      return { label: "Low stock", className: "low" };
    }

    return { label: "In stock", className: "available" };
  };

  return (
    <div className="sf-inventory">
      <style>{`
        .sf-inventory {
          color: #172033;
          width: 100%;
          font-family: Inter, Arial, sans-serif;
        }

        .sf-inventory * {
          box-sizing: border-box;
        }

        .sf-inventory button,
        .sf-inventory input,
        .sf-inventory select {
          font: inherit;
        }

        .sf-inventory .inv-heading {
          display: flex;
          justify-content: space-between;
          align-items: center;
          gap: 16px;
          margin-bottom: 25px;
        }

        .sf-inventory .inv-heading h1 {
          font-size: 25px;
          margin: 0 0 7px;
          font-weight: 750;
        }

        .sf-inventory .inv-heading p {
          color: #718096;
          margin: 0;
          font-size: 13px;
        }

        .sf-inventory .primary-btn {
          border: none;
          border-radius: 8px;
          padding: 11px 17px;
          background: #15803d;
          color: white;
          font-weight: 600;
          cursor: pointer;
          display: inline-flex;
          align-items: center;
          justify-content: center;
          gap: 8px;
        }

        .sf-inventory .primary-btn:hover {
          background: #166534;
        }

        .sf-inventory .stats-grid {
          display: grid;
          grid-template-columns: repeat(4, minmax(0, 1fr));
          gap: 16px;
          margin-bottom: 24px;
        }

        .sf-inventory .stat-card {
          background: white;
          border: 1px solid #e8edf2;
          border-radius: 11px;
          padding: 19px;
          min-width: 0;
        }

        .sf-inventory .stat-top {
          display: flex;
          justify-content: space-between;
          align-items: center;
          gap: 10px;
          color: #718096;
          font-size: 12px;
        }

        .sf-inventory .stat-icon {
          width: 36px;
          height: 36px;
          display: grid;
          place-items: center;
          border-radius: 9px;
          font-size: 17px;
          background: #eff6ff;
        }

        .sf-inventory .stat-card h2 {
          font-size: 24px;
          margin: 13px 0 5px;
          color: #172033;
        }

        .sf-inventory .stat-card small {
          color: #8491a3;
          font-size: 11px;
        }

        .sf-inventory .inventory-panel {
          background: white;
          border: 1px solid #e8edf2;
          border-radius: 11px;
          overflow: hidden;
        }

        .sf-inventory .panel-heading {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 20px;
          gap: 12px;
        }

        .sf-inventory .panel-heading h2 {
          font-size: 16px;
          margin: 0 0 5px;
        }

        .sf-inventory .panel-heading p {
          color: #8491a3;
          margin: 0;
          font-size: 12px;
        }

        .sf-inventory .filters {
          padding: 0 20px 18px;
          display: flex;
          gap: 12px;
          flex-wrap: wrap;
        }

        .sf-inventory .search-box {
          flex: 1;
          min-width: 190px;
          position: relative;
        }

        .sf-inventory .search-box input {
          width: 100%;
          padding: 10px 13px 10px 36px;
          border: 1px solid #dce3eb;
          border-radius: 8px;
          outline: none;
          font-size: 13px;
        }

        .sf-inventory .search-box input:focus,
        .sf-inventory .filters select:focus,
        .sf-inventory .modal-form input:focus {
          border-color: #16a34a;
          box-shadow: 0 0 0 3px #16a34a18;
        }

        .sf-inventory .search-symbol {
          position: absolute;
          left: 12px;
          top: 9px;
          color: #8491a3;
        }

        .sf-inventory .filters select {
          min-width: 145px;
          padding: 10px;
          border: 1px solid #dce3eb;
          border-radius: 8px;
          background: white;
          outline: none;
          color: #465267;
          font-size: 12px;
        }

        .sf-inventory .table-wrapper {
          width: 100%;
          overflow-x: auto;
        }

        .sf-inventory table {
          width: 100%;
          border-collapse: collapse;
          text-align: left;
          white-space: nowrap;
        }

        .sf-inventory thead {
          background: #f8fafc;
        }

        .sf-inventory th {
          padding: 13px 17px;
          font-size: 11px;
          color: #718096;
          font-weight: 650;
          border-top: 1px solid #edf0f4;
          border-bottom: 1px solid #edf0f4;
        }

        .sf-inventory td {
          padding: 13px 17px;
          border-bottom: 1px solid #edf0f4;
          font-size: 12px;
          color: #465267;
        }

        .sf-inventory tbody tr:hover {
          background: #fafcfb;
        }

        .sf-inventory .product-info {
          display: flex;
          align-items: center;
          min-width: 180px;
        }

        .sf-inventory .product-info strong {
          display: block;
          color: #263247;
          font-size: 12px;
          max-width: 220px;
          overflow: hidden;
          text-overflow: ellipsis;
        }

        .sf-inventory .stock-number {
          font-weight: 700;
          color: #263247;
        }

        .sf-inventory .status {
          display: inline-block;
          padding: 5px 9px;
          border-radius: 20px;
          font-size: 10px;
          font-weight: 650;
        }

        .sf-inventory .status.available {
          background: #dcfce7;
          color: #166534;
        }

        .sf-inventory .status.low {
          background: #fef3c7;
          color: #92400e;
        }

        .sf-inventory .status.out {
          background: #fee2e2;
          color: #b91c1c;
        }

        .sf-inventory .actions {
          display: flex;
          gap: 7px;
        }

        .sf-inventory .action-btn {
          border: 1px solid #e1e7ee;
          background: white;
          border-radius: 6px;
          padding: 6px 9px;
          cursor: pointer;
          font-size: 11px;
          color: #475569;
        }

        .sf-inventory .action-btn:hover {
          background: #f1f5f9;
        }

        .sf-inventory .action-btn.delete {
          color: #dc2626;
        }

        .sf-inventory .table-footer {
          padding: 14px 20px;
          color: #8491a3;
          font-size: 11px;
        }

        .sf-inventory .empty-state {
          text-align: center;
          padding: 55px 20px;
          color: #718096;
          font-size: 13px;
        }

        .sf-inventory .empty-state h3 {
          color: #263247;
        }

        .sf-inventory .modal-backdrop {
          position: fixed;
          inset: 0;
          z-index: 1000;
          background: rgba(15, 23, 42, .55);
          display: grid;
          place-items: center;
          padding: 16px;
        }

        .sf-inventory .modal {
          width: 100%;
          max-width: 490px;
          background: white;
          border-radius: 13px;
          padding: 24px;
          max-height: 90vh;
          overflow-y: auto;
          box-shadow: 0 20px 60px #0002;
        }

        .sf-inventory .modal-heading {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 20px;
        }

        .sf-inventory .modal-heading h2 {
          font-size: 19px;
          margin: 0;
        }

        .sf-inventory .close-btn {
          border: none;
          background: #f1f5f9;
          border-radius: 7px;
          width: 30px;
          height: 30px;
          cursor: pointer;
          font-size: 17px;
        }

        .sf-inventory .modal-form {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 14px;
        }

        .sf-inventory .form-field {
          display: flex;
          flex-direction: column;
          gap: 7px;
        }

        .sf-inventory .form-field.full {
          grid-column: 1 / -1;
        }

        .sf-inventory .form-field label {
          color: #475569;
          font-size: 11px;
          font-weight: 650;
        }

        .sf-inventory .modal-form input {
          width: 100%;
          border: 1px solid #dce3eb;
          border-radius: 7px;
          padding: 10px;
          outline: none;
          font-size: 12px;
          background: white;
        }

        .sf-inventory .modal-actions {
          display: flex;
          justify-content: flex-end;
          gap: 10px;
          grid-column: 1 / -1;
          margin-top: 10px;
        }

        .sf-inventory .cancel-btn {
          border: 1px solid #dce3eb;
          background: white;
          color: #475569;
          border-radius: 8px;
          padding: 10px 15px;
          cursor: pointer;
        }

        @media (max-width: 950px) {
          .sf-inventory .stats-grid {
            grid-template-columns: repeat(2, 1fr);
          }
        }

        @media (max-width: 600px) {
          .sf-inventory .inv-heading {
            align-items: flex-start;
            flex-direction: column;
          }

          .sf-inventory .stats-grid {
            gap: 9px;
          }

          .sf-inventory .stat-card {
            padding: 13px;
          }

          .sf-inventory .stat-card h2 {
            font-size: 19px;
          }

          .sf-inventory .filters {
            flex-direction: column;
          }

          .sf-inventory .filters select {
            width: 100%;
          }

          .sf-inventory .modal-form {
            grid-template-columns: 1fr;
          }

          .sf-inventory .form-field.full {
            grid-column: auto;
          }

          .sf-inventory .modal-actions {
            grid-column: auto;
          }
        }
      `}</style>

      {/* PAGE HEADER */}
      <div className="inv-heading">
        <div>
          <h1>Inventory Management</h1>
          <p>Manage products, monitor stock and track inventory levels.</p>
        </div>

        <button className="primary-btn" onClick={openAddModal}>
          <span>＋</span> Add Product
        </button>
      </div>

      {/* SUMMARY CARDS */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-top">
            Total Products
            <span className="stat-icon">📦</span>
          </div>
          <h2>{totalProducts}</h2>
          <small>Products in inventory</small>
        </div>

        <div className="stat-card">
          <div className="stat-top">
            Total Stock Units
            <span className="stat-icon">🏬</span>
          </div>
          <h2>{totalStock.toLocaleString()}</h2>
          <small>Units currently available</small>
        </div>

        <div className="stat-card">
          <div className="stat-top">
            Low Stock Items
            <span className="stat-icon">⚠️</span>
          </div>
          <h2>{lowStockProducts}</h2>
          <small>Products at or below their threshold</small>
        </div>

        <div className="stat-card">
          <div className="stat-top">
            Inventory Value
            <span className="stat-icon">💰</span>
          </div>
          <h2>{formatPrice(inventoryValue)}</h2>
          <small>Estimated value at listed prices</small>
        </div>
      </div>

      {/* INVENTORY TABLE */}
      <div className="inventory-panel">
        <div className="panel-heading">
          <div>
            <h2>All Products</h2>
            <p>View and manage your inventory products.</p>
          </div>
        </div>

        {/* SEARCH AND FILTERS */}
        <div className="filters">
          <div className="search-box">
            <span className="search-symbol">⌕</span>
            <input
              type="text"
              placeholder="Search by product name..."
              value={search}
              onChange={(event) => setSearch(event.target.value)}
            />
          </div>

          <select
            value={category}
            onChange={(event) => setCategory(event.target.value)}
          >
            <option value="all">All Categories</option>
            {categories.map((item) => (
              <option value={item} key={item}>
                {item}
              </option>
            ))}
          </select>

          <select
            value={stockFilter}
            onChange={(event) => setStockFilter(event.target.value)}
          >
            <option value="all">All Stock Levels</option>
            <option value="available">In Stock</option>
            <option value="low">Low Stock</option>
            <option value="out">Out of Stock</option>
          </select>
        </div>

        {filteredProducts.length === 0 ? (
          <div className="empty-state">
            <h3>
              {products.length === 0 ? "No products yet" : "No products found"}
            </h3>
            <p>
              {products.length === 0
                ? "Add your first product to get started."
                : "Try changing your search or filters."}
            </p>
          </div>
        ) : (
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>PRODUCT</th>
                  <th>CATEGORY</th>
                  <th>PRICE</th>
                  <th>QUANTITY</th>
                  <th>THRESHOLD</th>
                  <th>STATUS</th>
                  <th>ACTIONS</th>
                </tr>
              </thead>

              <tbody>
                {filteredProducts.map((product) => {
                  const status = getStockStatus(
                    product.quantity,
                    product.threshold
                  );

                  return (
                    <tr key={product.id}>
                      <td>
                        <div className="product-info">
                          <strong title={product.product_name}>
                            {product.product_name}
                          </strong>
                        </div>
                      </td>

                      <td>{product.category}</td>
                      <td>{formatPrice(product.price)}</td>

                      <td>
                        <span className="stock-number">
                          {product.quantity}
                        </span>
                      </td>

                      <td>{product.threshold}</td>

                      <td>
                        <span className={`status ${status.className}`}>
                          {status.label}
                        </span>
                      </td>

                      <td>
                        <div className="actions">
                          <button
                            className="action-btn"
                            onClick={() => openEditModal(product)}
                          >
                            Edit
                          </button>

                          <button
                            className="action-btn delete"
                            onClick={() =>
                              handleDelete(product.id, product.product_name)
                            }
                          >
                            Delete
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}

        <div className="table-footer">
          Showing {filteredProducts.length} of {totalProducts} products
          {" · "}
          {outOfStockProducts} out of stock
        </div>
      </div>

      {/* ADD / EDIT PRODUCT MODAL */}
      {showModal && (
        <div
          className="modal-backdrop"
          onMouseDown={(event) => {
            if (event.target === event.currentTarget) {
              setShowModal(false);
            }
          }}
        >
          <div className="modal">
            <div className="modal-heading">
              <h2>
                {editingProduct ? "Edit Product" : "Add New Product"}
              </h2>

              <button
                className="close-btn"
                onClick={() => setShowModal(false)}
                aria-label="Close modal"
              >
                ×
              </button>
            </div>

            <form className="modal-form" onSubmit={handleSubmit}>
              <div className="form-field full">
                <label>Product Name *</label>
                <input
                  name="product_name"
                  value={form.product_name}
                  onChange={handleChange}
                  placeholder="Enter product name"
                  maxLength={150}
                  required
                />
              </div>

              <div className="form-field full">
                <label>Category *</label>
                <input
                  name="category"
                  value={form.category}
                  onChange={handleChange}
                  placeholder="e.g. Electronics"
                  maxLength={100}
                  required
                />
              </div>

              <div className="form-field">
                <label>Price (KSH) *</label>
                <input
                  type="number"
                  name="price"
                  value={form.price}
                  onChange={handleChange}
                  min="0"
                  step="0.01"
                  required
                />
              </div>

              <div className="form-field">
                <label>Stock Quantity *</label>
                <input
                  type="number"
                  name="quantity"
                  value={form.quantity}
                  onChange={handleChange}
                  min="0"
                  step="1"
                  required
                />
              </div>

              <div className="form-field full">
                <label>Low Stock Threshold *</label>
                <input
                  type="number"
                  name="threshold"
                  value={form.threshold}
                  onChange={handleChange}
                  min="0"
                  step="1"
                  required
                />
              </div>

              <div className="modal-actions">
                <button
                  type="button"
                  className="cancel-btn"
                  onClick={() => setShowModal(false)}
                >
                  Cancel
                </button>

                <button type="submit" className="primary-btn">
                  {editingProduct ? "Save Changes" : "Add Product"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default Inventory;
