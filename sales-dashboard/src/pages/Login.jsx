import React, { useState } from "react";
import { login, register } from "../api";

export default function Login({ setRole }) {

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showSignup, setShowSignup] = useState(false);
  const [signup, setSignup] = useState({
    company_name: "",
    email: "",
    password: "",
  });

  const loginManager = async () => {

    try {

      const res = await login(email, password);

      if (res.detail) {

        alert(res.detail);

        return;

      }

      localStorage.setItem(
        "company_id",
        res.company_id
      );

      localStorage.setItem(
        "company_name",
        res.company_name
      );

      localStorage.setItem(
        "role",
        res.role
      );

      setRole(res.role);

   } catch (err) {

     alert("Unable to connect to server.");

     console.error(err);

   }

 };

  const loginWorker = () => {

    localStorage.setItem("role", "worker");

    setRole("worker");
  };

  const createCompany = async () => {

    try {

      const res = await register(signup);

      if (res.detail) {
        alert(res.detail);
        return;
      }

      alert("Company created successfully!");

      setShowSignup(false);

      setEmail(signup.email);
      setPassword(signup.password);

    } catch (err) {

      alert("Registration failed.");

      console.error(err);

    }

  };

    

  if (showSignup) {
    return (
     <div
       style={{
         display: "flex",
         justifyContent: "center",
         alignItems: "center",
         height: "100vh",
         background: "#f4f4f4",
       }}
     >
       <div
         style={{
           width: 420,
           background: "#fff",
           padding: 40,
           borderRadius: 15,
           boxShadow: "0 10px 30px rgba(0,0,0,0.15)",
         }}
       >
         <h2>Create Company Account</h2>

         <input
           placeholder="Company Name"
           value={signup.company_name}
           onChange={(e) =>
             setSignup({
               ...signup,
               company_name: e.target.value,
             })
           }
           style={{
             width: "100%",
             padding: 12,
             marginBottom: 12,
           }}
         />

         <input
           placeholder="Owner Name"
           style={{ width: "100%", padding: 12, marginBottom: 12 }}
         />

         <input
           placeholder="Email"
           value={signup.email}
           onChange={(e) =>
             setSignup({
               ...signup,
               email: e.target.value,
             })
          }
          style={{
            width: "100%",
            padding: 12,
            marginBottom: 12,
          }}
        />

        <input
           type="password"
           placeholder="Password"
           value={signup.password}
           onChange={(e) =>
             setSignup({
               ...signup,
               password: e.target.value,
             })
        }
        style={{
          width: "100%",
          padding: 12,
          marginBottom: 20,
        }}
      /> 

         <button
           style={{
             width: "100%",
             padding: 12,
             background: "#2563eb",
             color: "#fff",
             border: "none",
             borderRadius: 8,
           }}
           onClick={ createCompany}
        >
          Create Workspace
        </button>

        <button
          onClick={() => setShowSignup(false)}
          style={{
            width: "100%",
            marginTop: 10,
            padding: 12,
          }}
        >
          Back to Login
        </button>
      </div>
    </div>
  );
}  
  return (

    <div
      style={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        height: "100vh",
        background: "#f4f4f4",
      }}
    >

      <div
         style={{
           width: 420,
           background: "#fff",
           padding: 40,
           borderRadius: 15,
           boxShadow: "0 10px 30px rgba(0,0,0,0.15)",
         }}
      >

        <div style={{ textAlign: "center", marginBottom: 30 }}>

          <h1
            style={{
              marginBottom: 5,
              color: "#2563eb",
            }}
          >
            Xcellytics
          </h1>

          <p style={{ color: "#666" }}>
            Business Intelligence Platform
          </p>

        </div>

        <input
          type="email"
          placeholder="Email Address"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          style={{
            width: "100%",
            padding: 12,
            marginBottom: 15,
            borderRadius: 8,
            border: "1px solid #ddd",
          }}
        />

        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          style={{
            width: "100%",
            padding: 12,
            marginBottom: 20,
            borderRadius: 8,
            border: "1px solid #ddd",
          }}
        />

        <button
          onClick={loginManager}
          style={{
            width: "100%",
            padding: 12,
            background: "#2563eb",
            color: "#fff",
            border: "none",
            borderRadius: 8,
            fontWeight: "bold",
            cursor: "pointer",
            marginBottom: 12,
          }}
        >
          Login
        </button>

        <button
          onClick={loginWorker}
          style={{
            width: "100%",
            padding: 12,
            background: "#f3f4f6",
            border: "1px solid #ddd",
            borderRadius: 8,
            cursor: "pointer",
          }}
        >
          Demo Worker Login
        </button>

        <hr style={{ margin: "25px 0" }} />

        <div
          style={{
            textAlign: "center",
            color: "#666",
            fontSize: 14,
          }}
        >
          New Company?
        </div>

        <button
          onClick={() => setShowSignup(true)}  
          style={{
            width: "100%",
            padding: 12,
            marginTop: 12,
            background: "#10b981",
            color: "#fff",
            border: "none",
            borderRadius: 8,
            cursor: "pointer",
            fontWeight: "bold",
          }}
        >
          Start Free Trial
        </button>

       </div>
    </div>  
  );
}