import React, { useEffect, useState } from "react";

import {
  Routes,
  Route,
  Link,
  Navigate,
} from "react-router-dom";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  Legend,
} from "recharts";

import {
  getProducts,
  createProduct,
  updateProduct,
  deleteProduct,

  getSales,
  createSale,
  updateSale,
  deleteSale,

  getExpenses,
  createExpense,
  deleteExpense,

  getAnalytics

} from "../api";

import BulkUpload from "./BulkUpload";
import Login from "./Login";


// ================= COLORS =================

const COLORS = [
  "#3b82f6",
  "#10b981",
  "#f59e0b",
  "#ef4444",
  "#8b5cf6",
  "#06b6d4",
];


// ================= CARD =================

const Card = ({ title, value, color }) => (

  <div
    style={{
      background: "#fff",
      borderLeft: `8px solid ${color}`,
      padding: 25,
      borderRadius: 15,
      boxShadow: "0 2px 10px rgba(0,0,0,0.1)",
      minWidth: 220,
      flex: 1,
    }}
  >

    <h3>{title}</h3>

    <h1>{value}</h1>

  </div>
);


// ================= LAYOUT =================

const Layout = ({ children, role, logout }) => (

  <div style={{ display: "flex", minHeight: "100vh" }}>

    <div
      style={{
        width: 220,
        background: "#111",
        color: "#fff",
        padding: 20,
      }}
    >

      <h2>Xcellytics</h2>

      <p>
        Logged in as:
        <b> {role} </b>
      </p>

      <div style={{ marginTop: 20 }}>

        {role === "manager" && (
          <>
            <Link to="/home">Dashboard</Link>
            <br /><br />
          </>
        )}

        {role === "manager" && (
          <>
            <Link to="/products">Products</Link>
            <br /><br />
          </>
        )}

        <Link to="/sales">Sales</Link>

        <br /><br />

        <Link to="/expenses">Expenses</Link>

        <br /><br />

        {role === "manager" && (
          <>
            <Link to="/upload">Bulk Upload</Link>
            <br /><br />
          </>
        )}

        <button onClick={logout}>
          Logout
        </button>

      </div>

    </div>

    <div
      style={{
        flex: 1,
        padding: 25,
        background: "#f5f5f5",
      }}
    >
      {children}
    </div>

  </div>
);


// ================= DASHBOARD =================

const Dashboard = () => {

  const [data, setData] = useState(null);

  const [fullscreenChart, setFullscreenChart] =
  useState(null);  

  const load = async () => {

    const res = await getAnalytics();

    if (res) {
      setData(res);
    }
  };

  useEffect(() => {
    load();
  }, []);

  if (!data) {
    return <h2>Loading Dashboard...</h2>;
  }

  return (

  <div>

    {fullscreenChart && (

      <div
        onClick={() =>
          setFullscreenChart(null)
        }
        style={{
          position: "fixed",
          top: 0,
          left: 0,
          width: "100%",
          height: "100%",
          background: "rgba(0,0,0,0.85)",
          zIndex: 9999,
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          padding: 30,
        }}
      >

        <div
          onClick={(e) =>
            e.stopPropagation()
          }
          style={{
            width: "95%",
            height: "90%",
            background: "#fff",
            borderRadius: 15,
            padding: 25,
          }}
        >

          <button
            onClick={() =>
              setFullscreenChart(null)
            }
            style={{
              float: "right",
              marginBottom: 10,
            }}
          >
            Close
          </button>

          {fullscreenChart}

        </div>

      </div>

    )}

      <div
        style={{
          background: "#ffffff",
          padding: 20,
          borderRadius: 15,
          marginBottom: 25,
          boxShadow: "0 2px 10px rgba(0,0,0,0.08)",
        }}
      >
        <h1
          style={{
            margin: 0,
            color: "#2563eb",
          }}
        >
          Xcellytics Executive Dashboard
        </h1>

        <p
          style={{
            marginTop: 8,
            color: "#666",
          }}
        >
          Manual Sales Analytics & Business Performance
        </p>
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns:
             "repeat(auto-fit, minmax(200px, 1fr))",
          gap: 20,
          marginBottom: 30,
        }}
      >

        <Card
          title="Revenue"
          value={`$${data.totals.revenue}`}
          color="#10b981"
        />

        <Card
          title="Expenses"
          value={`$${data.totals.expenses}`}
          color="#ef4444"
        />

        <Card
          title="Profit"
          value={`$${data.totals.profit}`}
          color="#3b82f6"
        />

        <Card
          title="Sales"
          value={data.sales_count}
          color="#f59e0b"
        />

        <Card
          title="Products"
          value={data.product_count}
          color="#8b5cf6"
        />

        <Card
          title="Expenses Logged"
          value={data.expense_count}
          color="#14b8a6"
        />  

      </div>

      <div
        style={{
          background: "#fff",
          padding: 20,
          borderRadius: 15,
          marginBottom: 30,
          boxShadow: "0 2px 10px rgba(0,0,0,0.08)",
        }}
      >

        <h2>Business Summary</h2>

        <p>
          Revenue:
           <b> ${data.totals.revenue}</b>
        </p>

        <p>
          Expenses:
           <b> ${data.totals.expenses}</b>
        </p>

        <p>
          Profit:
           <b> ${data.totals.profit}</b>
        </p>

        <p>
          Profit Margin:
        <b>
          {" "}
          {data.totals.revenue > 0
            ? (
                (data.totals.profit /
                  data.totals.revenue) *
                100
              ).toFixed(1)
            : 0}
           %
         </b>
       </p>

     </div>

      {/* MANUAL SALES ONLY */}

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: 20,
          marginBottom: 30,
        }}
      >  
      <div
        style={{
          background: "#fff",
          padding: 25,
          borderRadius: 15,
          marginBottom: 30,
        }}
      >

        <h2>Manual Sales Trends</h2>

        <button
          onClick={() =>
            setFullscreenChart(

              <ResponsiveContainer
                width="100%"
                height="100%"
              >

                <BarChart data={data.graph || []}>

                  <CartesianGrid strokeDasharray="3 3" />

                  <XAxis dataKey="date" />

                  <YAxis />

                  <Tooltip />

                  <Legend />

                  <Bar
                    dataKey="sales"
                    fill="#3b82f6"
                  />

                </BarChart>

              </ResponsiveContainer>

            )
          }
          style={{
            marginBottom: 15,
            padding: "8px 14px",
            border: "none",
            borderRadius: 8,
            background: "#2563eb",
            color: "#fff",
            cursor: "pointer",
          }}
        >
          Fullscreen
        </button>  

        <div style={{ width: "100%", height: 400 }}>

          <ResponsiveContainer width="100%" height="100%">

            <BarChart data={data.graph || []}>

              <CartesianGrid strokeDasharray="3 3" />

              <XAxis dataKey="date" />

              <YAxis />

              <Tooltip />

              <Legend />

              <Bar
                dataKey="sales"
                fill="#3b82f6"
              />

            </BarChart>

          </ResponsiveContainer>

        </div>

      </div>

      <div
        style={{
          background: "#fff",
          padding: 25,
          borderRadius: 15,
          marginBottom: 30,
        }}
      >

        <h2>Sales Growth</h2>

        <button
          onClick={() =>
            setFullscreenChart(

              <ResponsiveContainer
                width="100%"
                height="100%"
              >

                <LineChart data={data.graph || []}>

                <CartesianGrid strokeDasharray="3 3" />

                <XAxis dataKey="date" />

                <YAxis />

                <Tooltip />

                <Legend />

                <Line
                  type="monotone"
                  dataKey="sales"
                  stroke="#10b981"
                  strokeWidth={3}
                />

               </LineChart>

              </ResponsiveContainer>

            )
          }
          style={{
            marginBottom: 15,
            padding: "8px 14px",
            border: "none",
            borderRadius: 8,
            background: "#2563eb",
            color: "#fff",
            cursor: "pointer",
          }}
        >
          Fullscreen
        </button>

        <div style={{ width: "100%", height: 350 }}>

          <ResponsiveContainer width="100%" height="100%">

            <LineChart data={data.graph || []}>

              <CartesianGrid strokeDasharray="3 3" />

              <XAxis dataKey="date" />

              <YAxis />

              <Tooltip />

              <Legend />

              <Line
                type="monotone"
                dataKey="sales"
                stroke="#10b981"
                strokeWidth={3}
              />

            </LineChart>

          </ResponsiveContainer>

        </div>

      </div>

      <div
        style={{
          background: "#fff",
          padding: 25,
          borderRadius: 15,
          marginBottom: 30,
        }}
      >

        <h2>Product Performance Distribution</h2>

        <button
          onClick={() =>
            setFullscreenChart(

              <ResponsiveContainer
                width="100%"
                height="100%"
              >

                <PieChart>

                  <Pie
                    data={data.performance || []}
                    dataKey="actual"
                    nameKey="name"
                    outerRadius={250}
                    label
                  >

                    {(data.performance || []).map(
                      (entry, index) => (

                        <Cell
                          key={index}
                          fill={
                            COLORS[
                              index % COLORS.length
                            ]
                           }
                         />

                       )
                     )}

                   </Pie>

                   <Tooltip />

                   </PieChart>

                   </ResponsiveContainer>

                )
              }
              style={{
                marginBottom: 15,
                padding: "8px 14px",
                border: "none",
                borderRadius: 8,
                background: "#2563eb",
                color: "#fff",
                cursor: "pointer",
              }}
             >
              Fullscreen
             </button>

        <div style={{ width: "100%", height: 400 }}>

          <ResponsiveContainer width="100%" height="100%">

            <PieChart>

              <Pie
                data={data.performance || []}
                dataKey="actual"
                nameKey="name"
                outerRadius={140}
                label
              >

                {(data.performance || []).map(
                  (entry, index) => (

                    <Cell
                      key={index}
                      fill={
                        COLORS[
                          index % COLORS.length
                        ]
                      }
                    />

                  )
                )}

              </Pie>

              <Tooltip />

            </PieChart>

          </ResponsiveContainer>

        </div>

      </div>

      <div
        style={{
          background: "#fff",
          padding: 25,
          borderRadius: 15,
        }}
      >

        <h2>Performance Analytics</h2>

        <table
          border="1"
          cellPadding="10"
          width="100%"
        >

          <thead>

            <tr>
              <th>Product</th>
              <th>Actual</th>
              <th>Target</th>
              <th>Percent</th>
              <th>Status</th>
            </tr>

          </thead>

          <tbody>

            {(data.performance || []).map(
              (p, i) => (

                <tr key={i}>

                  <td>{p.name}</td>

                  <td>${p.actual}</td>

                  <td>${p.target}</td>

                  <td>{p.percent}%</td>

                  <td>{p.status}</td>

                </tr>

              )
            )}

          </tbody>

        </table>

      </div>

    </div>
   </div>     
  );
};


// ================= PRODUCTS =================

const Products = () => {

  const [list, setList] = useState([]);

  const [editing, setEditing] = useState(null);

  const [form, setForm] = useState({
    name: "",
    price: "",
    target: "",
    password: "",
  });

  const load = async () => {

    const res = await getProducts();

    // REMOVE BULK PRODUCTS
    const filtered = (res || []).filter(
      (p) => !p.name?.startsWith("BULK_")
    );

    setList(filtered);
  };

  useEffect(() => {
    load();
  }, []);

  const submit = async (e) => {

    e.preventDefault();

    if (editing) {

      await updateProduct(editing, form);

      setEditing(null);

    } else {

      await createProduct(form);
    }

    setForm({
      name: "",
      price: "",
      target: "",
      password: "",
    });

    load();
  };

  const edit = (p) => {

    setEditing(p.id);

    setForm({
      name: p.name,
      price: p.price,
      target: p.target,
      password: "",
    });
  };

  const remove = async (id) => {

    const password = prompt(
      "Manager Password"
    );

    await deleteProduct(id, password);

    load();
  };

  return (

    <div>

      <h2>Products</h2>

      <form onSubmit={submit}>

        <input
          placeholder="Name"
          value={form.name}
          onChange={(e) =>
            setForm({
              ...form,
              name: e.target.value,
            })
          }
        />

        <input
          placeholder="Price"
          value={form.price}
          onChange={(e) =>
            setForm({
              ...form,
              price: e.target.value,
            })
          }
        />

        <input
          placeholder="Target"
          value={form.target}
          onChange={(e) =>
            setForm({
              ...form,
              target: e.target.value,
            })
          }
        />

        <input
          type="password"
          placeholder="Manager Password"
          value={form.password}
          onChange={(e) =>
            setForm({
              ...form,
              password: e.target.value,
            })
          }
        />

        <button>
          {editing
            ? "Update Product"
            : "Add Product"}
        </button>

      </form>

      <br />

      <table border="1" cellPadding="10">

        <thead>

          <tr>
            <th>Name</th>
            <th>Price</th>
            <th>Target</th>
            <th>Actions</th>
          </tr>

        </thead>

        <tbody>

          {list.map((p) => (

            <tr key={p.id}>

              <td>{p.name}</td>

              <td>${p.price}</td>

              <td>${p.target}</td>

              <td>

                <button
                  onClick={() => edit(p)}
                >
                  Edit
                </button>

                <button
                  onClick={() => remove(p.id)}
                >
                  Delete
                </button>

              </td>

            </tr>

          ))}

        </tbody>

      </table>

    </div>
  );
};


// ================= SALES =================

const Sales = () => {

  const [products, setProducts] = useState([]);

  const [sales, setSales] = useState([]);

  const [editing, setEditing] = useState(null);

  const [form, setForm] = useState({
    product_id: "",
    quantity: "",
    purchase_date: "",
  });

  const load = async () => {

    const p = await getProducts();

    const s = await getSales();

    const filteredProducts = (p || []).filter(
      (x) => !x.name?.startsWith("BULK_")
    );

    const filteredSales = (s || []).filter(
      (sale) => {

        const product = (p || []).find(
          (x) => x.id === sale.product_id
        );

        return !product?.name?.startsWith(
          "BULK_"
        );
      }
    );

    setProducts(filteredProducts);

    setSales(filteredSales);
  };

  useEffect(() => {
    load();
  }, []);

  const submit = async (e) => {

    e.preventDefault();

    if (editing) {

      await updateSale(editing, form);

      setEditing(null);

    } else {

      await createSale(form);
    }

    setForm({
      product_id: "",
      quantity: "",
      purchase_date: "",
    });

    load();
  };

  const editSale = (s) => {

    setEditing(s.id);

    setForm({
      product_id: s.product_id,
      quantity: s.quantity,
      purchase_date: s.purchase_date
        ? s.purchase_date.slice(0, 10)
        : "",
    });
  };

  const remove = async (id) => {

    await deleteSale(id);

    load();
  };

  const getName = (id) =>
    products.find(
      (p) => p.id === id
    )?.name || "Unknown";

  return (

    <div>

      <h2>Sales</h2>

      <form onSubmit={submit}>

        <select
          value={form.product_id}
          onChange={(e) =>
            setForm({
              ...form,
              product_id: e.target.value,
            })
          }
        >

          <option value="">
            Select Product
          </option>

          {products.map((p) => (

            <option
              key={p.id}
              value={p.id}
            >
              {p.name}
            </option>

          ))}

        </select>

        <input
          placeholder="Quantity"
          value={form.quantity}
          onChange={(e) =>
            setForm({
              ...form,
              quantity: e.target.value,
            })
          }
        />
        <input
          type="date"
          value={form.purchase_date}
          onChange={(e) =>
            setForm({
              ...form,
              purchase_date: e.target.value,
             })
          }
        />

        <button>
          {editing
            ? "Update Sale"
            : "Add Sale"}
        </button>

      </form>

      <br />

      <table border="1" cellPadding="10">

        <thead>

          <tr>
            <th>Product</th>
            <th>Quantity</th>
            <th>Total</th>
            <th>Purchase Date</th>
            <th>Created Date</th>
            <th>Last Modified</th>
            <th>Actions</th>
          </tr>

        </thead>

        <tbody>

          {sales.map((s) => (

            <tr key={s.id}>

              <td>
                {getName(s.product_id)}
              </td>

              <td>{s.quantity}</td>

              <td>${s.total_price}</td>

              <td>
                {s.purchase_date
                  ? s.purchase_date.slice(0, 10)
                  : ""}
              </td>

              <td>
                {s.created_date
                  ? s.created_date.slice(0, 10)
                  : ""}
              </td>

              <td>
                {s.last_modified_date
                  ? s.last_modified_date.slice(0, 19)
                  : ""}
              </td>

              <td>

                <button
                  onClick={() =>
                    editSale(s)
                  }
                >
                  Edit
                </button>

                <button
                  onClick={() =>
                    remove(s.id)
                  }
                >
                  Delete
                </button>

              </td>

            </tr>

          ))}

        </tbody>

      </table>

    </div>
  );
};


// ================= EXPENSES =================

const Expenses = () => {

  const role = localStorage.getItem(
    "role"
  );

  const [list, setList] = useState([]);

  const [form, setForm] = useState({
    amount: "",
    description: "",
    type: "general",
    password: "",
  });

  const load = async () => {

    const res = await getExpenses();

    if (!res) {
      setList([]);
      return;
    }

    if (role === "worker") {

      const filtered = res.filter(
        (e) =>
          e.type === "general"
      );

      setList(filtered);

    } else {

      setList(res);
    }
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps  
  }, []);

  const submit = async (e) => {

    e.preventDefault();

    if (
      role === "worker" &&
      form.type === "confidential"
    ) {

      alert(
        "Workers cannot create confidential expenses"
      );

      return;
    }

    await createExpense(form);

    setForm({
      amount: "",
      description: "",
      type: "general",
      password: "",
    });

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

        <input
          placeholder="Amount"
          value={form.amount}
          onChange={(e) =>
            setForm({
              ...form,
              amount: e.target.value,
            })
          }
        />

        <input
          placeholder="Description"
          value={form.description}
          onChange={(e) =>
            setForm({
              ...form,
              description: e.target.value,
            })
          }
        />

        <select
          value={form.type}
          onChange={(e) =>
            setForm({
              ...form,
              type: e.target.value,
            })
          }
        >

          <option value="general">
            General
          </option>

          {role === "manager" && (
            <option value="confidential">
              Confidential
            </option>
          )}

        </select>

        {form.type ===
          "confidential" &&
          role === "manager" && (

          <input
            type="password"
            placeholder="Manager Password"
            value={form.password}
            onChange={(e) =>
              setForm({
                ...form,
                password: e.target.value,
              })
            }
          />

        )}

        <button>
          Add Expense
        </button>

      </form>

      <br />

      <table border="1" cellPadding="10">

        <thead>

          <tr>
            <th>Amount</th>
            <th>Description</th>
            <th>Type</th>
            <th>Date</th>
            <th>Action</th>
          </tr>

        </thead>

        <tbody>

          {list.map((e) => (

            <tr key={e.id}>

              <td>${e.amount}</td>

              <td>{e.description}</td>

              <td>{e.type}</td>

              <td>{e.date}</td>

              <td>

                <button
                  onClick={() =>
                    remove(e.id)
                  }
                >
                  Delete
                </button>

              </td>

            </tr>

          ))}

        </tbody>

      </table>

    </div>
  );
};


// ================= MAIN =================

export default function Pages() {

  const [role, setRole] = useState(
    localStorage.getItem("role")
  );

  const logout = () => {

    localStorage.removeItem("role");

    setRole(null);
  };

  if (!role) {

    return <Login setRole={setRole} />;
  }

  return (

    <Layout
      role={role}
      logout={logout}
    >

      <Routes>

        {role === "manager" ? (
          <Route
            path="/"
            element={<Dashboard />}
          />
        ) : (
          <Route
            path="/"
            element={
              <Navigate to="/sales" />
            }
          />
        )}

        {role === "manager" && (
          <Route
            path="/home"
            element={<Dashboard />}
          />
        )}

        {role === "manager" && (
          <Route
            path="/products"
            element={<Products />}
          />
        )}

        <Route
          path="/sales"
          element={<Sales />}
        />

        <Route
          path="/expenses"
          element={<Expenses />}
        />

        {role === "manager" && (
          <Route
            path="/upload"
            element={<BulkUpload />}
          />
        )}

      </Routes>

    </Layout>
  );
}