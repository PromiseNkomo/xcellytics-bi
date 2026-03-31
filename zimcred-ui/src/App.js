import { BrowserRouter as Router, Routes, Route, Link, Navigate } from "react-router-dom";
import React, { useEffect, useState, useRef } from "react";

// ✅ AUTH PAGES
import Login from "./Login";
import Register from "./Register";

// ================= STYLES =================

const container = { maxWidth: "1100px", margin: "auto" };

const card = {
  background: "#fff",
  padding: "25px",
  borderRadius: "10px",
  marginBottom: "25px",
  boxShadow: "0 3px 12px rgba(0,0,0,0.08)"
};

const input = {
  width: "100%",
  padding: "12px",
  marginBottom: "10px",
  borderRadius: "6px",
  border: "1px solid #ccc"
};

const button = {
  padding: "12px",
  width: "100%",
  background: "#0d6efd",
  color: "white",
  border: "none",
  borderRadius: "6px",
  fontWeight: "bold",
  cursor: "pointer"
};

// ================= 🔐 PRIVATE ROUTE =================

function PrivateRoute({ children }) {
  const token = localStorage.getItem("token");
  return token ? children : <Navigate to="/login" />;
}

// ================= HOME =================

function Home() {
  return (
    <div style={container}>
      <h2>ZimCred AI — Credit Decision Intelligence</h2>
      <p style={{ fontSize: "18px", lineHeight: "1.7" }}>
        ZimCred AI is a professional credit risk decision platform built for 
        microfinance institutions and lenders operating in emerging markets.
        It delivers fast, consistent, and explainable loan decisions powered by AI.
      </p>
      <hr />
      <h3>Key Capabilities</h3>
      <ul>
        <li>✔ Probability of Default (PD) modeling</li>
        <li>✔ Automated credit scoring (300–850 scale)</li>
        <li>✔ Risk classification (Low → Very High)</li>
        <li>✔ Policy-based loan approval system</li>
        <li>✔ Explainable AI for audit & compliance</li>
      </ul>
      <hr />
      <h3>Operational Value</h3>
      <p>
        ZimCred AI reduces default rates, improves lending consistency, 
        and enables institutions to scale decision-making without increasing risk exposure.
      </p>
    </div>
  );
}

// ================= ABOUT =================

function About() {
  return (
    <div style={container}>
      <h2>About ZimCred AI</h2>
      <p>
        ZimCred AI is a fintech decision intelligence system designed to modernize 
        credit risk assessment for financial institutions.
      </p>
      <hr />
      <h3>Platform Architecture</h3>
      <ul>
        <li>FastAPI backend (secure & scalable)</li>
        <li>Machine learning credit scoring engine</li>
        <li>AI-powered decision explanation layer</li>
        <li>React-based user interface</li>
      </ul>
      <hr />
      <h3>Vision</h3>
      <p>
        To become a leading AI infrastructure provider for credit risk decisioning 
        across Africa and other emerging markets.
      </p>
    </div>
  );
}

// ================= DISCLAIMER =================

function Disclaimer() {
  return (
    <div style={container}>
      <h2>Legal & Risk Disclaimer</h2>
      <p>
        ZimCred AI is a decision-support system intended to assist financial 
        institutions in evaluating credit applications.
      </p>
      <hr />
      <p>
        The system provides predictive insights based on data inputs and machine 
        learning models. Final lending decisions remain the responsibility of the institution.
      </p>
      <hr />
      <p>
        ZimCred AI does not assume liability for financial losses resulting from 
        decisions made using this platform.
      </p>
    </div>
  );
}

// ================= DASHBOARD =================

function Dashboard() {

  const [income, setIncome] = useState("");
  const [loan, setLoan] = useState("");
  const [expenses, setExpenses] = useState("");
  const [dependents, setDependents] = useState("");

  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  const [message, setMessage] = useState("");
  const [chat, setChat] = useState([]);

  // 🔥 BULK STATES
  const [file, setFile] = useState(null);
  const [bulkResult, setBulkResult] = useState(null);

  const chatEndRef = useRef(null);

  useEffect(() => {
    const saved = localStorage.getItem("zimcred_result");
    if (saved) setResult(JSON.parse(saved));

    const savedChat = localStorage.getItem("zimcred_chat");
    if (savedChat) setChat(JSON.parse(savedChat));
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chat]);

  const handleEvaluate = async () => {
    setError("");

    try {
      const res = await fetch("http://127.0.0.1:8001/assist", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-API-Key": "zimcapital-secret-key"
        },
        body: JSON.stringify({
          question: "Evaluate",
          mfi_name: "ZimCapital Microfinance",
          applicant_data: {
            monthly_income: Number(income),
            requested_loan_amount: Number(loan),
            monthly_expenses: Number(expenses),
            dependents: Number(dependents)
          }
        })
      });

      const data = await res.json();
      setResult(data);
      localStorage.setItem("zimcred_result", JSON.stringify(data));

    } catch {
      setError("Failed to connect to backend");
    }
  };

  // 🔥 BULK UPLOAD FUNCTION
  const handleBulkUpload = async () => {
    if (!file) return alert("Please upload a CSV file");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch("http://127.0.0.1:8000/bulk-score", {
        method: "POST",
        body: formData
      });

      const data = await res.json();
      setBulkResult(data);

    } catch {
      alert("Bulk upload failed");
    }
  };

  const sendMessage = async () => {
    if (!message) return;

    const userMsg = { sender: "user", text: message };
    setChat(prev => [...prev, userMsg]);

    try {
      const res = await fetch("http://127.0.0.1:8001/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-API-Key": "zimcapital-secret-key"
        },
        body: JSON.stringify({
          message,
          mfi_name: "ZimCapital Microfinance"
        })
      });

      const data = await res.json();

      const botMsg = {
        sender: "bot",
        text: data.agent_reply || "No response"
      };

      const updated = [...chat, userMsg, botMsg];
      setChat(updated);
      localStorage.setItem("zimcred_chat", JSON.stringify(updated));

    } catch {
      alert("Chat failed");
    }

    setMessage("");
  };

  return (
    <div style={container}>
      <h2>Credit Decision Dashboard</h2>

      {/* SINGLE */}
      <div style={card}>
        <h3>Loan Evaluation</h3>

        <input style={input} placeholder="Monthly Income" onChange={e => setIncome(e.target.value)} />
        <input style={input} placeholder="Requested Loan" onChange={e => setLoan(e.target.value)} />
        <input style={input} placeholder="Monthly Expenses" onChange={e => setExpenses(e.target.value)} />
        <input style={input} placeholder="Dependents" onChange={e => setDependents(e.target.value)} />

        <button style={button} onClick={handleEvaluate}>
          Evaluate Loan
        </button>

        {error && <p style={{ color: "red" }}>{error}</p>}
      </div>

      {/* 🔥 BULK UPLOAD */}
      <div style={card}>
        <h3>Bulk Loan Evaluation (CSV Upload)</h3>

        <input type="file" accept=".csv" onChange={(e) => setFile(e.target.files[0])} />

        <button style={button} onClick={handleBulkUpload}>
          Upload & Process
        </button>

        {bulkResult && (
          <pre style={{ marginTop: "15px", overflowX: "auto" }}>
            {JSON.stringify(bulkResult, null, 2)}
          </pre>
        )}
      </div>

      {/* EXISTING RESULT + CHAT REMAINS UNTOUCHED */}
      {result && result.decision_panel && (
        <div style={card}>
          <h3>Decision Panel</h3>
          <p><b>Score:</b> {result.decision_panel.Credit_Score}</p>
          <p><b>Risk:</b> {result.decision_panel.Risk_Band}</p>
          <p><b>Status:</b> {result.decision_panel.Policy_Status}</p>
          <hr />
          <h3>AI Explanation</h3>
          <p>{result.assistant.summary}</p>
        </div>
      )}

      <div style={card}>
        <h3>AI Assistant</h3>
        <div style={{ height: "250px", overflowY: "auto", background: "#f1f1f1", padding: "15px", borderRadius: "8px" }}>
          {chat.map((c, i) => (
            <div key={i} style={{
              display: "flex",
              justifyContent: c.sender === "user" ? "flex-end" : "flex-start",
              marginBottom: "10px"
            }}>
              <div style={{
                maxWidth: "70%",
                padding: "10px",
                borderRadius: "10px",
                background: c.sender === "user" ? "#0d6efd" : "#e0e0e0",
                color: c.sender === "user" ? "white" : "black"
              }}>
                {c.text}
              </div>
            </div>
          ))}
          <div ref={chatEndRef} />
        </div>

        <input style={input} value={message} onChange={(e) => setMessage(e.target.value)} />
        <button style={button} onClick={sendMessage}>Send</button>
      </div>
    </div>
  );
}

// ================= APP =================

function App() {
  return (
    <Router>
      <div style={{ padding: "20px", background: "#f5f7fa", minHeight: "100vh" }}>
        <h1>ZimCred AI</h1>

        <nav>
          <Link to="/login">Login</Link> |{" "}
          <Link to="/register">Register</Link> |{" "}
          <Link to="/">Home</Link> |{" "}
          <Link to="/dashboard">Dashboard</Link> |{" "}
          <Link to="/about">About</Link> |{" "}
          <Link to="/disclaimer">Disclaimer</Link>
        </nav>

        <hr />

        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/" element={<Home />} />
          <Route path="/about" element={<About />} />
          <Route path="/disclaimer" element={<Disclaimer />} />

          <Route path="/dashboard" element={
            <PrivateRoute>
              <Dashboard />
            </PrivateRoute>
          } />
        </Routes>
      </div>
    </Router>
  );
}

export default App;