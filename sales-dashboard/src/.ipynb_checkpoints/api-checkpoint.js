const API = "http://127.0.0.1:8000";

const safe = async (url, opt) => {
  try {
    const r = await fetch(url, opt);
    return await r.json();
  } catch {
    return null;
  }
};

// PRODUCTS
export const getProducts = () => safe(`${API}/products/`);
export const createProduct = (d) =>
  safe(`${API}/products/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(d),
  });

export const deleteProduct = (id) =>
  safe(`${API}/products/${id}`, { method: "DELETE" });

// SALES
export const getSales = () => safe(`${API}/sales/`);
export const createSale = (d) =>
  safe(`${API}/sales/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(d),
  });

export const deleteSale = (id) =>
  safe(`${API}/sales/${id}`, { method: "DELETE" });

// EXPENSES
export const getExpenses = () => safe(`${API}/expenses/`);
export const createExpense = (d) =>
  safe(`${API}/expenses/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(d),
  });

export const deleteExpense = (id) =>
  safe(`${API}/expenses/${id}`, { method: "DELETE" });

// ANALYTICS
export const getAnalytics = () => safe(`${API}/analytics/`);