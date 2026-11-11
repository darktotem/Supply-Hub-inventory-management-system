
import { useEffect, useMemo, useState } from "react";

const API_URL = "https://dummyjson.com/products?limit=100";
const LOW_STOCK_LIMIT = 10;

/**
 * @typedef {Object} Product
 * @property {number|string} id
 * @property {string} title
 * @property {string} category
 * @property {string} [brand]
 * @property {number} price
 * @property {number} stock
 * @property {string} [sku]
 * @property {string} [thumbnail]
 * @property {number} [rating]
 */

/**
 * @typedef {Object} ProductForm
 * @property {string} title
 * @property {string} category
 * @property {string} brand
 * @property {string} price
 * @property {string} stock
 * @property {string} sku
 */

const initialForm = {
  title: "",
  category: "",
  brand: "",
  price: "",
  stock: "",
  sku: "",
};

/**
 * @param {number|string} price
 */
function formatPrice(price) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  }).format(Number(price || 0));
}

function Inventory() {
  /** @type {Product[]} */
  const initialProducts = [];

  const [products, setProducts] = useState(initialProducts);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("all");
  const [stockFilter, setStockFilter] = useState("all");

  const [showModal, setShowModal] = useState(false);

const [editingProduct, setEditingProduct] = useState(
  /** @type {Product|null} */ (null)
);

  /** @type {[ProductForm, (value: ProductForm|((previous: ProductForm) => ProductForm)) => void]} */
  const [form, setForm] = useState(initialForm);

  // Fetch products from DummyJSON
  const fetchProducts = async () => {
    try {
      setLoading(true);
      setError("");

      const response = await fetch(API_URL);

      if (!response.ok) {
        throw new Error("Unable to fetch inventory products.");
      }

      const data = await response.json();
      setProducts(data.products || []);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Something went wrong."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProducts();
  }, []);

  // Get unique product categories
  const categories = useMemo(() => {
    return [...new Set(products.map((product) => product.category))]
      .filter(Boolean)
      .sort();
  }, [products]);

  // Search and filter products
  const filteredProducts = useMemo(() => {
    return products.filter((product) => {
      const matchesSearch =
        product.title.toLowerCase().includes(search.toLowerCase()) ||
        (product.brand || "").toLowerCase().includes(search.toLowerCase()) ||
        (product.sku || "").toLowerCase().includes(search.toLowerCase());

      const matchesCategory =
        category === "all" || product.category === category;

      const matchesStock =
        stockFilter === "all" ||
        (stockFilter === "low" && product.stock <= LOW_STOCK_LIMIT) ||
        (stockFilter === "available" && product.stock > LOW_STOCK_LIMIT) ||
        (stockFilter === "out" && product.stock === 0);

      return matchesSearch && matchesCategory && matchesStock;
    });
  }, [products, search, category, stockFilter]);

  // Inventory statistics
  const totalProducts = products.length;

  const totalStock = products.reduce(
    (total, product) => total + Number(product.stock || 0),
    0
  );

  const lowStockProducts = products.filter(
    (product) =>
      product.stock > 0 && product.stock <= LOW_STOCK_LIMIT
  ).length;

  const outOfStockProducts = products.filter(
    (product) => product.stock === 0
  ).length;

  const inventoryValue = products.reduce(
    (total, product) =>
      total + Number(product.price || 0) * Number(product.stock || 0),
    0
  );

  // Open add product modal
  const openAddModal = () => {
    setEditingProduct(null);
    setForm(initialForm);
    setShowModal(true);
  };

  // Open edit product modal
  /**
   * @param {Product} product
   */
  const openEditModal = (product) => {
    setEditingProduct(product);

    setForm({
      title: product.title || "",
      category: product.category || "",
      brand: product.brand || "",
      price: String(product.price ?? ""),
      stock: String(product.stock ?? ""),
      sku: product.sku || "",
    });

    setShowModal(true);
  };

  // Handle form input
  /**
   * @param {{ target: { name: string, value: string } }} event
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
   * @param {{ preventDefault: () => void }} event
   */
  const handleSubmit = (event) => {
    event.preventDefault();

    const productData = {
      ...form,
      price: Number(form.price),
      stock: Number(form.stock),
      thumbnail:
        editingProduct?.thumbnail ||
        "https://placehold.co/100x100?text=Product",
    };

    if (
      !productData.title.trim() ||
      !productData.category.trim() ||
      !productData.sku.trim() ||
      Number.isNaN(productData.price) ||
      productData.price < 0 ||
      !Number.isInteger(productData.stock) ||
      productData.stock < 0
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
        ...productData,
        id: `local-${Date.now()}`,
        rating: 0,
      };

      setProducts((previous) => [newProduct, ...previous]);
    }

    setShowModal(false);
    setEditingProduct(null);
    setForm(initialForm);
  };

  // Delete product
  /**
   * @param {number|string} id
   * @param {string} title
   */
  const handleDelete = (id, title) => {
    const confirmed = window.confirm(
      `Are you sure you want to delete "${title}"?`
    );

    if (!confirmed) return;

    setProducts((previous) =>
      previous.filter((product) => product.id !== id)
    );
  };

  // Stock status
  /**
   * @param {number} stock
   */
  const getStockStatus = (stock) => {
    if (stock === 0) {
      return { label: "Out of stock", className: "out" };
    }

    if (stock <= LOW_STOCK_LIMIT) {
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
        .sf-inventory .modal-form input:focus,
        .sf-inventory .modal-form select:focus {
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
          gap: 11px;
          min-width: 210px;
        }

        .sf-inventory .product-info img {
          width: 42px;
          height: 42px;
          object-fit: contain;
          border: 1px solid #edf0f4;
          border-radius: 7px;
          background: white;
        }

        .sf-inventory .product-info strong {
          display: block;
          color: #263247;
          font-size: 12px;
          max-width: 180px;
          overflow: hidden;
          text-overflow: ellipsis;
        }

        .sf-inventory .product-info small {
          color: #98a2b3;
          display: block;
          margin-top: 4px;
          font-size: 10px;
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

        .sf-inventory .loading-state,
        .sf-inventory .empty-state {
          text-align: center;
          padding: 55px 20px;
          color: #718096;
          font-size: 13px;
        }

        .sf-inventory .error-state {
          background: #fff1f2;
          border: 1px solid #fecdd3;
          color: #be123c;
          border-radius: 9px;
          padding: 17px;
          margin-bottom: 18px;
          font-size: 13px;
        }

        .sf-inventory .retry-btn {
          margin-left: 12px;
          border: none;
          color: #be123c;
          font-weight: 700;
          background: transparent;
          cursor: pointer;
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

        .sf-inventory .modal-form input,
        .sf-inventory .modal-form select {
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
          <small>Products with 1–10 units</small>
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

      {/* ERROR MESSAGE */}
      {error && (
        <div className="error-state">
          {error}
          <button className="retry-btn" onClick={fetchProducts}>
            Try again
          </button>
        </div>
      )}

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
              placeholder="Search by product, brand or SKU..."
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

        {loading ? (
          <div className="loading-state">
            Loading inventory products...
          </div>
        ) : filteredProducts.length === 0 ? (
          <div className="empty-state">
            <h3>No products found</h3>
            <p>Try changing your search or filters.</p>
          </div>
        ) : (
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>PRODUCT</th>
                  <th>SKU</th>
                  <th>CATEGORY</th>
                  <th>PRICE</th>
                  <th>STOCK</th>
                  <th>STATUS</th>
                  <th>ACTIONS</th>
                </tr>
              </thead>

              <tbody>
                {filteredProducts.map((product) => {
                  const status = getStockStatus(product.stock);

                  return (
                    <tr key={product.id}>
                      <td>
                        <div className="product-info">
                          <img
                            src={product.thumbnail}
                            alt={product.title}
                            onError={(event) => {
                              event.currentTarget.src =
                                "https://placehold.co/100x100?text=Product";
                            }}
                          />
                          <div>
                            <strong title={product.title}>
                              {product.title}
                            </strong>
                            <small>{product.brand || "No brand"}</small>
                          </div>
                        </div>
                      </td>

                      <td>{product.sku || "—"}</td>

                      <td>{product.category}</td>

                      <td>{formatPrice(product.price)}</td>

                      <td>
                        <span className="stock-number">
                          {product.stock}
                        </span>
                      </td>

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
                              handleDelete(product.id, product.title)
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
                  name="title"
                  value={form.title}
                  onChange={handleChange}
                  placeholder="Enter product name"
                  required
                />
              </div>

              <div className="form-field">
                <label>Category *</label>
                <input
                  name="category"
                  value={form.category}
                  onChange={handleChange}
                  placeholder="e.g. Electronics"
                  required
                />
              </div>

              <div className="form-field">
                <label>Brand</label>
                <input
                  name="brand"
                  value={form.brand}
                  onChange={handleChange}
                  placeholder="Enter brand"
                />
              </div>

              <div className="form-field">
                <label>Price (USD) *</label>
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
                  name="stock"
                  value={form.stock}
                  onChange={handleChange}
                  min="0"
                  step="1"
                  required
                />
              </div>

              <div className="form-field full">
                <label>SKU *</label>
                <input
                  name="sku"
                  value={form.sku}
                  onChange={handleChange}
                  placeholder="e.g. SF-PROD-001"
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
