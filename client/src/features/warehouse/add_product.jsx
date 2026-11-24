import { useEffect, useMemo, useState } from "react";
import {
  createWarehouseProduct,
  getWarehouseProducts,
} from "../../api/warehouse";
import "./warehouse.css";

const emptyForm = {
  product_name: "",
  category: "",
  quantity: "",
  threshold: "10",
  price: "",
};

function formatCurrency(value) {
  return new Intl.NumberFormat("en-KE", {
    style: "currency",
    currency: "KES",
    maximumFractionDigits: 2,
  }).format(Number(value) || 0);
}

function AddProduct() {
  const [products, setProducts] = useState([]);
  const [form, setForm] = useState({ ...emptyForm });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [search, setSearch] = useState("");

  useEffect(() => {
    let cancelled = false;

    async function loadProducts() {
      try {
        const data = await getWarehouseProducts();
        if (!cancelled) {
          setProducts(Array.isArray(data) ? data : []);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Could not load products.");
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    loadProducts();
    return () => {
      cancelled = true;
    };
  }, []);

  const visibleProducts = useMemo(() => {
    const query = search.trim().toLowerCase();
    return products.filter((product) =>
      `${product.product_name} ${product.category}`.toLowerCase().includes(query)
    );
  }, [products, search]);

  const lowStockCount = products.filter(
    (product) => Number(product.quantity) <= Number(product.threshold)
  ).length;

  function handleChange(event) {
    const { name, value } = event.target;
    setForm((previous) => ({ ...previous, [name]: value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setSuccess("");

    const product = {
      product_name: form.product_name.trim(),
      category: form.category.trim(),
      quantity: Number(form.quantity),
      threshold: Number(form.threshold),
      price: Number(form.price),
    };

    if (
      !product.product_name ||
      !product.category ||
      form.quantity === "" ||
      form.threshold === "" ||
      form.price === "" ||
      !Number.isInteger(product.quantity) ||
      product.quantity < 0 ||
      !Number.isInteger(product.threshold) ||
      product.threshold < 0 ||
      !Number.isFinite(product.price) ||
      product.price < 0
    ) {
      setError("Enter a name, category, valid stock levels, and a non-negative price.");
      return;
    }

    setSaving(true);
    try {
      const created = await createWarehouseProduct(product);
      setProducts((previous) =>
        [...previous, created].sort((a, b) =>
          a.product_name.localeCompare(b.product_name)
        )
      );
      setForm({ ...emptyForm });
      setSuccess(`${created.product_name} was added to the warehouse.`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not add the product.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <section className="warehouse-page" aria-labelledby="warehouse-products-title">
      <header className="warehouse-heading">
        <div>
          <p className="warehouse-eyebrow">Warehouse / Inventory</p>
          <h1 id="warehouse-products-title">Products</h1>
          <p>Register new products and keep an eye on available stock.</p>
        </div>
      </header>

      <div className="warehouse-stats">
        <article className="warehouse-stat">
          <span>Products in catalog</span>
          <strong>{products.length}</strong>
          <small>Products currently tracked</small>
        </article>
        <article className="warehouse-stat">
          <span>Units in stock</span>
          <strong>
            {products.reduce((total, item) => total + Number(item.quantity || 0), 0)}
          </strong>
          <small>Total quantity across products</small>
        </article>
        <article className="warehouse-stat warehouse-stat-warning">
          <span>Low stock items</span>
          <strong>{lowStockCount}</strong>
          <small>At or below their reorder threshold</small>
        </article>
      </div>

      <div className="warehouse-content-grid">
        <section className="warehouse-panel warehouse-product-form-panel">
          <div className="warehouse-panel-heading">
            <div>
              <h2>Add a product</h2>
              <p>Enter the product details to add it to inventory.</p>
            </div>
            <span className="warehouse-heading-icon" aria-hidden="true">+</span>
          </div>

          {error && <div className="warehouse-alert warehouse-alert-error" role="alert">{error}</div>}
          {success && <div className="warehouse-alert warehouse-alert-success" role="status">{success}</div>}

          <form className="warehouse-form" onSubmit={handleSubmit}>
            <label className="warehouse-field warehouse-field-wide">
              <span>Product name</span>
              <input
                name="product_name"
                value={form.product_name}
                onChange={handleChange}
                maxLength={150}
                placeholder="e.g. Packing tape"
                required
              />
            </label>
            <label className="warehouse-field warehouse-field-wide">
              <span>Category</span>
              <input
                name="category"
                value={form.category}
                onChange={handleChange}
                maxLength={100}
                placeholder="e.g. Packaging"
                required
              />
            </label>
            <label className="warehouse-field">
              <span>Opening quantity</span>
              <input
                name="quantity"
                type="number"
                min="0"
                step="1"
                value={form.quantity}
                onChange={handleChange}
                placeholder="0"
                required
              />
            </label>
            <label className="warehouse-field">
              <span>Low stock threshold</span>
              <input
                name="threshold"
                type="number"
                min="0"
                step="1"
                value={form.threshold}
                onChange={handleChange}
                required
              />
            </label>
            <label className="warehouse-field warehouse-field-wide">
              <span>Unit price (KES)</span>
              <input
                name="price"
                type="number"
                min="0"
                step="0.01"
                value={form.price}
                onChange={handleChange}
                placeholder="0.00"
                required
              />
            </label>
            <button className="warehouse-primary-button warehouse-field-wide" type="submit" disabled={saving}>
              {saving ? "Adding product…" : "Add product"}
            </button>
          </form>
        </section>

        <section className="warehouse-panel warehouse-products-panel">
          <div className="warehouse-panel-heading">
            <div>
              <h2>Product catalog</h2>
              <p>Current warehouse inventory</p>
            </div>
            <label className="warehouse-search">
              <span className="warehouse-visually-hidden">Search products</span>
              <input
                type="search"
                value={search}
                onChange={(event) => setSearch(event.target.value)}
                placeholder="Search products"
              />
            </label>
          </div>

          {loading ? (
            <p className="warehouse-empty-state">Loading products…</p>
          ) : visibleProducts.length === 0 ? (
            <p className="warehouse-empty-state">
              {products.length ? "No products match your search." : "No products have been added yet."}
            </p>
          ) : (
            <div className="warehouse-table-scroll">
              <table className="warehouse-table">
                <thead>
                  <tr>
                    <th>Product</th>
                    <th>Category</th>
                    <th>In stock</th>
                    <th>Unit price</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {visibleProducts.map((product) => {
                    const quantity = Number(product.quantity);
                    const low = quantity <= Number(product.threshold);
                    return (
                      <tr key={product.id}>
                        <td><strong>{product.product_name}</strong></td>
                        <td>{product.category}</td>
                        <td>{quantity}</td>
                        <td>{formatCurrency(product.price)}</td>
                        <td>
                          <span className={`warehouse-badge ${low ? "warehouse-badge-warning" : "warehouse-badge-success"}`}>
                            {low ? "Low stock" : "In stock"}
                          </span>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </section>
      </div>
    </section>
  );
}

export default AddProduct;