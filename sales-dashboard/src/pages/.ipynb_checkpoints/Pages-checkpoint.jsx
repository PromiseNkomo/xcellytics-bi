import React, { useEffect, useState } from "react";
import { Routes, Route, Link } from "react-router-dom";
import {
  getProducts, createProduct, deleteProduct,
  getSales, createSale, deleteSale,
  getExpenses, createExpense, deleteExpense,
  getAnalytics
} from "../api";

// LAYOUT
const Layout = ({ children }) => (
  <div style={{ display: "flex", height: "100vh" }}>
    <div style={{ width: 220, background: "#111", color: "#fff", padding: 15 }}>
      <h2>Xcellytics</h2>
      <Link to="/home">Dashboard</Link><br />
      <Link to="/products">Products</Link><br />
      <Link to="/sales">Sales</Link><br />
      <Link to="/expenses">Expenses</Link>
    </div>
    <div style={{ flex: 1, padding: 20 }}>{children}</div>
  </div>
);

// DASHBOARD
const Dashboard = () => {
  const [data, setData] = useState(null);

  useEffect(() => {
    getAnalytics().then(setData);
  }, []);

  if (!data) return <h3>Loading...</h3>;

  return (
    <div>
      <h2>Dashboard</h2>
      <h3>Revenue: ${data.totals.revenue}</h3>
      <h3>Expenses: ${data.totals.expenses}</h3>
      <h3>Profit: ${data.totals.profit}</h3>
    </div>
  );
};

// PRODUCTS
const Products = () => {
  const [list, setList] = useState([]);
  const [form, setForm] = useState({ name: "", price: "", target: "" });

  const load = () => getProducts().then(r => setList(r || []));

  useEffect(load, []);

  const add = async (e) => {
    e.preventDefault();
    await createProduct(form);
    setForm({ name: "", price: "", target: "" });
    load();
  };

  const remove = async (id) => {
    await deleteProduct(id);
    load();
  };

  return (
    <div>
      <h2>Products</h2>

      <form onSubmit={add}>
        <input placeholder="Name" value={form.name}
          onChange={e => setForm({ ...form, name: e.target.value })} />

        <input placeholder="Price" value={form.price}
          onChange={e => setForm({ ...form, price: e.target.value })} />

        <input placeholder="Target" value={form.target}
          onChange={e => setForm({ ...form, target: e.target.value })} />

        <button>Add</button>
      </form>

      <table border="1" cellPadding="8">
        <thead>
          <tr>
            <th>Name</th>
            <th>Price</th>
            <th>Target</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          {list.map(p => (
            <tr key={p.id}>
              <td>{p.name}</td>
              <td>{p.price}</td>
              <td>{p.target}</td>
              <td>
                <button onClick={() => remove(p.id)}>Delete</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

// SALES (REAL TABLE)
const Sales = () => {
  const [products, setProducts] = useState([]);
  const [sales, setSales] = useState([]);
  const [form, setForm] = useState({ product_id: "", quantity: "" });

  const load = () => {
    getProducts().then(setProducts);
    getSales().then(setSales);
  };

  useEffect(load, []);

  const submit = async (e) => {
    e.preventDefault();
    await createSale(form);
    setForm({ product_id: "", quantity: "" });
    load();
  };

  const remove = async (id) => {
    await deleteSale(id);
    load();
  };

  const getName = (id) =>
    products.find(p => p.id === id)?.name || "Unknown";

  return (
    <div>
      <h2>Sales</h2>

      <form onSubmit={submit}>
        <select value={form.product_id}
          onChange={e => setForm({ ...form, product_id: e.target.value })}>
          <option>Select Product</option>
          {products.map(p => (
            <option key={p.id} value={p.id}>{p.name}</option>
          ))}
        </select>

        <input placeholder="Quantity"
          value={form.quantity}
          onChange={e => setForm({ ...form, quantity: e.target.value })} />

        <button>Add</button>
      </form>

      <table border="1" cellPadding="8">
        <thead>
          <tr>
            <th>Product</th>
            <th>Qty</th>
            <th>Total</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          {sales.map(s => (
            <tr key={s.id}>
              <td>{getName(s.product_id)}</td>
              <td>{s.quantity}</td>
              <td>{s.total_price}</td>
              <td>
                <button onClick={() => remove(s.id)}>Delete</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

// EXPENSES
const Expenses = () => {
  const [list, setList] = useState([]);
  const [form, setForm] = useState({ amount: "", description: "", type: "general" });

  const load = () => getExpenses().then(setList);

  useEffect(load, []);

  const submit = async (e) => {
    e.preventDefault();
    await createExpense(form);
    setForm({ amount: "", description: "", type: "general" });
    load();
  };

  const remove = async (id) => {
    await deleteExpense(id);
    load();
  };

  return (
    <div>
      <h2>Expenses</h2>

      <form onSubmit={submit}>
        <input placeholder="Amount"
          value={form.amount}
          onChange={e => setForm({ ...form, amount: e.target.value })} />

        <input placeholder="Description"
          value={form.description}
          onChange={e => setForm({ ...form, description: e.target.value })} />

        <select value={form.type}
          onChange={e => setForm({ ...form, type: e.target.value })}>
          <option value="general">General</option>
          <option value="confidential">Confidential</option>
        </select>

        <button>Add</button>
      </form>

      <table border="1" cellPadding="8">
        <thead>
          <tr>
            <th>Amount</th>
            <th>Description</th>
            <th>Type</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          {list.map(e => (
            <tr key={e.id}>
              <td>{e.amount}</td>
              <td>{e.description}</td>
              <td>{e.type}</td>
              <td>
                <button onClick={() => remove(e.id)}>Delete</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

// ROUTES
export default function Pages() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/home" element={<Dashboard />} />
        <Route path="/products" element={<Products />} />
        <Route path="/sales" element={<Sales />} />
        <Route path="/expenses" element={<Expenses />} />
      </Routes>
    </Layout>
  );
}