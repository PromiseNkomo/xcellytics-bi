import React from "react";
import { Link } from "react-router-dom";

const Sidebar = () => {
  return (
    <div className="w-64 bg-gray-800 text-white flex flex-col p-4">
      <h1 className="text-2xl font-bold mb-6">Sales System</h1>
      <Link to="/dashboard" className="mb-2 hover:bg-gray-700 p-2 rounded">Dashboard</Link>
      <Link to="/products" className="mb-2 hover:bg-gray-700 p-2 rounded">Products</Link>
      <Link to="/sales" className="mb-2 hover:bg-gray-700 p-2 rounded">Sales</Link>
      <Link to="/expenses" className="mb-2 hover:bg-gray-700 p-2 rounded">Expenses</Link>
      <Link to="/" className="mt-auto hover:bg-gray-700 p-2 rounded">Logout</Link>
    </div>
  );
};

export default Sidebar;