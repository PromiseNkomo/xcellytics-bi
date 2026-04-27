import React, { useEffect, useState } from "react";
import { getMonthlyAnalytics } from "../api";
import Navbar from "../components/Navbar";
import { BarChart, Bar, XAxis, YAxis, Tooltip, Legend } from "recharts";

const Dashboard = () => {
  const [monthlyData, setMonthlyData] = useState([]);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const data = await getMonthlyAnalytics(2026, 4);
      setMonthlyData(Array.isArray(data) ? data : []);
    } catch (err) {
      console.log(err);
      setMonthlyData([]);
    }
  };

  return (
    <div>
      <Navbar />

      <div className="p-6 space-y-6">
        <h2 className="text-2xl font-bold">
          Monthly Revenue & Profit
        </h2>

        {/* Chart */}
        <div className="bg-white p-4 rounded shadow">
          <BarChart width={800} height={400} data={monthlyData}>
            <XAxis dataKey="product" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="revenue" />
            <Bar dataKey="profit" />
          </BarChart>
        </div>

        {/* Target Status */}
        <div>
          <h3 className="text-xl font-semibold mb-2">
            Target Status
          </h3>

          <div className="flex flex-wrap gap-3">
            {monthlyData.map((item, index) => (
              <div
                key={index}
                className={`px-4 py-2 rounded text-white ${
                  item.status === "green"
                    ? "bg-green-500"
                    : item.status === "yellow"
                    ? "bg-yellow-500"
                    : "bg-red-500"
                }`}
              >
                {item.product}: {item.status.toUpperCase()}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;