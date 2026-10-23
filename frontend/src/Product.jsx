import { useState } from "react";
import {
  Package,
  Plus,
  Search,
  Edit,
  Trash2,
  ArrowLeft,
} from "lucide-react";

function Product({ onBack }) {

  const [products, setProducts] = useState([]);

  const [form, setForm] = useState({
    name: "",
    code: "",
    category: "",
    supplier: "",
    purchasePrice: "",
    sellingPrice: "",
    stock: "",
    reorderLevel: "",
  });

  const [search, setSearch] = useState("");
  const [editIndex, setEditIndex] = useState(null);

  const handleChange = (e) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    if (!form.name || !form.code || !form.sellingPrice) {
      alert("Please fill Product Name, Product Code and Selling Price.");
      return;
    }

    if (editIndex !== null) {
      const updated = [...products];
      updated[editIndex] = form;
      setProducts(updated);
      setEditIndex(null);
    } else {
      setProducts([...products, form]);
    }

    setForm({
      name: "",
      code: "",
      category: "",
      supplier: "",
      purchasePrice: "",
      sellingPrice: "",
      stock: "",
      reorderLevel: "",
    });
  };

  const editProduct = (index) => {
    setForm(products[index]);
    setEditIndex(index);
  };

  const deleteProduct = (index) => {
    if (window.confirm("Delete this product?")) {
      setProducts(
        products.filter((_, i) => i !== index)
      );
    }
  };

  const filteredProducts = products.filter((product) =>
    product.name
      .toLowerCase()
      .includes(search.toLowerCase())
  );

  return (
    <div className="product-page">

      {/* HEADER */}

      <div className="product-header">

        <div className="product-title">

          <div className="product-icon">
            <Package size={28} />
          </div>

          <div>
            <h1>Product Management</h1>
            <p>
              Manage your products, prices and inventory.
            </p>
          </div>

        </div>

        <button
          className="back-button"
          onClick={onBack}
        >
          <ArrowLeft size={18} />
          Back to Dashboard
        </button>

      </div>

      {/* PRODUCT FORM */}

      <div className="product-card">

        <h2>
          {editIndex !== null
            ? "Update Product"
            : "Add New Product"}
        </h2>

        <form
          className="product-form"
          onSubmit={handleSubmit}
        >

          <div className="product-field">
            <label>Product Name</label>

            <input
              name="name"
              value={form.name}
              onChange={handleChange}
              placeholder="Enter product name"
            />
          </div>

          <div className="product-field">
            <label>Product Code / SKU</label>

            <input
              name="code"
              value={form.code}
              onChange={handleChange}
              placeholder="Enter product code"
            />
          </div>

          <div className="product-field">
            <label>Category</label>

            <input
              name="category"
              value={form.category}
              onChange={handleChange}
              placeholder="Enter category"
            />
          </div>

          <div className="product-field">
            <label>Supplier</label>

            <input
              name="supplier"
              value={form.supplier}
              onChange={handleChange}
              placeholder="Enter supplier"
            />
          </div>

          <div className="product-field">
            <label>Purchase Price</label>

            <input
              type="number"
              name="purchasePrice"
              value={form.purchasePrice}
              onChange={handleChange}
              placeholder="₹ 0.00"
            />
          </div>

          <div className="product-field">
            <label>Selling Price</label>

            <input
              type="number"
              name="sellingPrice"
              value={form.sellingPrice}
              onChange={handleChange}
              placeholder="₹ 0.00"
            />
          </div>

          <div className="product-field">
            <label>Stock Quantity</label>

            <input
              type="number"
              name="stock"
              value={form.stock}
              onChange={handleChange}
              placeholder="0"
            />
          </div>

          <div className="product-field">
            <label>Reorder Level</label>

            <input
              type="number"
              name="reorderLevel"
              value={form.reorderLevel}
              onChange={handleChange}
              placeholder="0"
            />
          </div>

          <div className="product-actions">

            <button
              type="submit"
              className="add-product-button"
            >
              {editIndex !== null ? (
                <>
                  <Edit size={18} />
                  Update Product
                </>
              ) : (
                <>
                  <Plus size={18} />
                  Add Product
                </>
              )}
            </button>

          </div>

        </form>

      </div>

      {/* PRODUCT LIST */}

      <div className="product-card">

        <div className="product-list-header">

          <div>
            <h2>Product List</h2>

            <p>
              {products.length} product(s)
            </p>
          </div>

          <div className="product-search">

            <Search size={18} />

            <input
              placeholder="Search products..."
              value={search}
              onChange={(e) =>
                setSearch(e.target.value)
              }
            />

          </div>

        </div>

        <div className="table-container">

          <table>

            <thead>
              <tr>
                <th>Product</th>
                <th>Code</th>
                <th>Category</th>
                <th>Supplier</th>
                <th>Purchase</th>
                <th>Selling</th>
                <th>Stock</th>
                <th>Actions</th>
              </tr>
            </thead>

            <tbody>

              {filteredProducts.length === 0 ? (

                <tr>
                  <td
                    colSpan="8"
                    className="empty-products"
                  >
                    No products found.
                  </td>
                </tr>

              ) : (

                filteredProducts.map((product, index) => (

                  <tr key={index}>

                    <td>
                      <strong>
                        {product.name}
                      </strong>
                    </td>

                    <td>{product.code}</td>

                    <td>{product.category}</td>

                    <td>{product.supplier}</td>

                    <td>
                      ₹{product.purchasePrice || 0}
                    </td>

                    <td>
                      ₹{product.sellingPrice || 0}
                    </td>

                    <td>
                      {product.stock || 0}
                    </td>

                    <td>

                      <button
                        className="edit-button"
                        onClick={() =>
                          editProduct(index)
                        }
                      >
                        <Edit size={16} />
                      </button>

                      <button
                        className="delete-button"
                        onClick={() =>
                          deleteProduct(index)
                        }
                      >
                        <Trash2 size={16} />
                      </button>

                    </td>

                  </tr>

                ))

              )}

            </tbody>

          </table>

        </div>

      </div>

    </div>
  );
}

export default Product;