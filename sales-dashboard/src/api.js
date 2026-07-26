const API = "https://xcellytics-bi.onrender.com";

const safe = async (url, opt = {}) => {

  const company_id = localStorage.getItem("company_id");

  opt.headers = {
    ...(opt.headers || {}),
    company_id,
  };

  try {

    const r = await fetch(url, opt);

    return await r.json();

  } catch (err) {

    console.log(err);

    return null;
  }

};


// ================= PRODUCTS =================

export const getProducts = () =>
  safe(`${API}/products/`);


export const createProduct = (d) =>
  safe(`${API}/products/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(d),
  });


export const updateProduct = (id, d) =>
  safe(`${API}/products/${id}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(d),
  });


export const deleteProduct = (id, password) =>
  safe(`${API}/products/${id}?password=${password}`, {
    method: "DELETE",
  });


// ================= SALES =================

export const getSales = () =>
  safe(`${API}/sales/`);


export const createSale = (d) =>
  safe(`${API}/sales/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(d),
  });


export const updateSale = (id, d) =>
  safe(`${API}/sales/${id}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(d),
  });


export const deleteSale = (id) =>
  safe(`${API}/sales/${id}`, {
    method: "DELETE",
  });


// ================= EXPENSES =================

export const getExpenses = () =>
  safe(`${API}/expenses/`);


export const createExpense = (d) =>
  safe(`${API}/expenses/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(d),
  });


export const deleteExpense = (id) =>
  safe(`${API}/expenses/${id}`, {
    method: "DELETE",
  });


// ================= ANALYTICS =================

// ================= ANALYTICS =================

export const getAnalytics = () => {

    const company_id = localStorage.getItem("company_id");

    return safe(
        `${API}/analytics/?company_id=${company_id}`
    );
};

export const login = async (email, password) => {

  const response = await fetch(`${API}/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      email,
      password,
    }),
  });

  const data = await response.json();

  if (response.ok) {

    localStorage.setItem(
      "company_id",
      data.company_id
    );

    localStorage.setItem(
      "company_name",
      data.company_name
    );

    localStorage.setItem(
      "role",
      data.role
    );
  }

  return data;
};

export const register = async (company) => {

  try {

    const response = await fetch(`${API}/register`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(company),
    });

    return await response.json();

  } catch (err) {

    console.log(err);

    return null;

  }

};
// ================= BULK UPLOAD =================

export const bulkUpload = async (file) => {

  const company_id = localStorage.getItem("company_id");

  const formData = new FormData();

  formData.append("file", file);

  try {

    const r = await fetch(
      `${API}/bulk-upload/?company_id=${company_id}`,
      {
        method: "POST",
        body: formData,
      }
    );

    return await r.json();

  } catch (err) {

    console.log(err);

    return null;
  }
};