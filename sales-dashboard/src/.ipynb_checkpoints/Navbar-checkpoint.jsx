import React from "react";
import { Link } from "react-router-dom";

const Navbar = () => {
  return (
    <nav className="bg-blue-600 text-white p-4 flex justify-between">
      <h1 className="font-bold text-lg">Sales System</h1>
      <div className="space-x-4">
        <Link to="/dashboard">Dashboard</Link>
        <Link to="/products">Products</Link>
        <Link to="/sales">Sales</Link>
        <Link to="/expenses">Expenses</Link>
      </div>
    </nav>
  );
};

export default Navbar;