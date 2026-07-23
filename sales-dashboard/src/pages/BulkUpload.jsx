 import React, { useEffect, useState } from "react";

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

import { bulkUpload } from "../api";

const COLORS = [
  "#3b82f6",
  "#10b981",
  "#f59e0b",
  "#ef4444",
  "#8b5cf6",
  "#06b6d4",
  "#14b8a6",
  "#f97316",
];

export default function BulkUpload() {

  const [file, setFile] = useState(null);

  const [loading, setLoading] = useState(false);

  const [result, setResult] = useState(null);

  const [archives, setArchives] = useState([]);
  const [fullscreenChart, setFullscreenChart] =
  useState(null);  

  const [timeFilter, setTimeFilter] =
    useState("all");

  const [productFilter, setProductFilter] =
    useState("all");

  const company_id = localStorage.getItem("company_id");  
  // ================= LOAD SAVED RESULT =================

  useEffect(() => {

    const company_id = localStorage.getItem("company_id");

    const saved = localStorage.getItem(
        `bulk_upload_results_${company_id}`
      );  

    if (saved) {

      setResult(JSON.parse(saved));
    }

    const savedArchives = localStorage.getItem(
      `bulk_upload_archives_${company_id}`
    );

    if (savedArchives) {

      setArchives(JSON.parse(savedArchives));
    }

  }, []);

  // ================= UPLOAD =================

  const upload = async () => {

    if (!file) {

      alert("Please select a file");

      return;
    }

    setLoading(true);

    const res = await bulkUpload(file);

    setLoading(false);

    if (res) {

      setResult(res);

      // SAVE RESULTS

       
      localStorage.setItem(
        `bulk_upload_results_${company_id}`,
        JSON.stringify(res)
      );
    }
  };


  // ================= ARCHIVE =================

  const archiveCurrent = () => {

    if (!result) {
      alert("No analysis to archive");
      return;
    }

    const archiveName = prompt("Enter archive name");

    if (!archiveName) return;

    const updated = [
      {
        id: Date.now(),
        name: archiveName,
        archivedAt: new Date().toLocaleString(),
        data: result,
      },
      ...archives,
    ];

    setArchives(updated);

    
      
    localStorage.setItem(
      `bulk_upload_archives_${company_id}`,
      JSON.stringify(updated)
    );

    setResult(null);

     
    localStorage.removeItem(
      `bulk_upload_results_${company_id}`,
    );
  };

  const loadArchive = (archive) => {
    setResult(archive.data);
    
    localStorage.setItem(
      `bulk_upload_results_${company_id}`,
      JSON.stringify(archive.data)
    );
  };

  const deleteArchive = (id) => {
    const updated = archives.filter(
      (a) => a.id !== id
    );

    setArchives(updated);
    
    localStorage.setItem(
      `bulk_upload_archives_${company_id}`,
      JSON.stringify(updated)
    );
  };

  // ================= CHART DATA =================

  // ================= FILTER SALES =================

  const filteredSales = result?.sales
    ? result.sales.filter((sale) => {

        // Product Filter
        if (
          productFilter !== "all" &&
          sale.product !== productFilter
        ) {
          return false;
        }

       // Time Filter
       if (timeFilter === "all") {
         return true;
       }

       const saleDate = new Date(sale.date);
       const today = new Date();

       const diffDays = Math.floor(
         (today - saleDate) /
         (1000 * 60 * 60 * 24)
       );

       switch (timeFilter) {

         case "day":
           return diffDays === 0;

         case "week":
           return diffDays <= 7;

         case "month":
           return (
             saleDate.getMonth() === today.getMonth() &&
             saleDate.getFullYear() === today.getFullYear()
           );

         case "year":
           return (
             saleDate.getFullYear() === today.getFullYear()
           );

         default:
           return true;
       }

      })
    : [];


  // ================= REBUILD REVENUE =================

  const revenueData = Object.values(

    filteredSales.reduce((acc, sale) => {

      if (!acc[sale.product]) {

        acc[sale.product] = {
          name: sale.product,
          revenue: 0,
        };

      }

      acc[sale.product].revenue += sale.revenue;

      return acc;

   }, {})

 ).map(item => ({

   ...item,

   revenue: Number(item.revenue.toFixed(2))

 }));


 // ================= SORT =================

 const sortedRevenueData =
   [...revenueData].sort(
     (a, b) => b.revenue - a.revenue
   );


 // ================= SUMMARY =================

 const totalRevenue =
   revenueData.reduce(
     (sum, item) => sum + item.revenue,
     0
   );

 const topProduct =
   sortedRevenueData[0];

 const lowProduct =
   sortedRevenueData[
     sortedRevenueData.length - 1
   ];


 // ================= DAILY REVENUE =================

 const dailyRevenueData = Object.values(

  filteredSales.reduce((acc, sale) => {

    if (!acc[sale.date]) {

      acc[sale.date] = {
        date: sale.date,
        revenue: 0,
      };

    }

    acc[sale.date].revenue += sale.revenue;

    return acc;

  }, {})

)
.sort(
  (a, b) => new Date(a.date) - new Date(b.date)
)
.map(item => ({
  ...item,
  revenue: Number(item.revenue.toFixed(2))
}));


 // ================= PIE DATA =================

 const pieData = (() => {

   const top10 =
     sortedRevenueData.slice(0, 10);

   const remaining =
     sortedRevenueData.slice(10);

   const otherRevenue =
     remaining.reduce(
       (sum, item) => sum + item.revenue,
       0
     );

   if (otherRevenue > 0) {

     return [
       ...top10,
       {
         name: "Other",
         revenue: otherRevenue,
       },
     ];

   }

   return top10;

 })();


 // ================= FILTERED TABLE =================

 const filteredRevenueData =
   sortedRevenueData.filter((item) => {

     if (
       productFilter !== "all" &&
       item.name !== productFilter
     ) {
       return false;
     }

     return true;

    });
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
            background:
              "rgba(0,0,0,0.85)",
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
             height: "85%",
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
        marginBottom: 20,
        boxShadow: "0 2px 10px rgba(0,0,0,0.08)",
      }}
    >

     <h1
       style={{
         margin: 0,
         color: "#2563eb",
       }}
     >
       Xcellytics Analytics Dashboard
     </h1>

     <p
       style={{
         marginTop: 8,
         color: "#666",
       }}
     >
       POS Data Import, Revenue Analysis & Business Intelligence
     </p>

    </div>
        

      

      {/* ================= INFO BOX ================= */}
       <div
         style={{
           background: "#ffffff",
           padding: 15,
           borderRadius: 15,
           marginBottom: 15,
           boxShadow: "0 2px 10px rgba(0,0,0,0.08)",
         }}
       >

         <h3 style={{ marginTop: 0 }}>
           Import Requirements
         </h3>

         <table
           width="100%"
           style={{
             borderCollapse: "collapse",
             marginBottom: 10,
           }}
         >

           <thead>

             <tr>
               <th align="left">Product</th>
               <th align="left">Quantity</th>
               <th align="left">Price</th>
               <th align="left">Date</th>
             </tr>

          </thead>

          <tbody>

            <tr>
              <td>Coke</td>
              <td>5</td>
              <td>18.99</td>
              <td>2026-05-27</td>
            </tr>

            <tr>
              <td>Bread</td>
              <td>3</td>
              <td>12.50</td>
              <td>2026-05-27</td>
            </tr>

           </tbody>

         </table>

         <p style={{ margin: 0 }}>
            <b>Supported:</b> CSV, XLSX |
            <b> Required:</b> Product, Quantity |
            <b> Optional:</b> Price, Date
         </p>

       </div>
      

      {/* ================= UPLOAD AREA ================= */}

      <div
        style={{
          background: "#ffffff",
          padding: 15,
          borderRadius: 15,
          marginBottom: 20,
          boxShadow: "0 2px 10px rgba(0,0,0,0.08)",
          display: "flex",
          gap: 15,
          alignItems: "center", 
          flexWrap: "wrap",  
        }}
      >

        <input
          type="file"
          accept=".csv,.xlsx"
          onChange={(e) =>
            setFile(e.target.files[0])
          }
        />

        

        <button
          onClick={upload}
          style={{
            padding: "10px 18px",
            border: "none",
            borderRadius: 10,
            background: "#2563eb",
            color: "#fff",
            cursor: "pointer",
            fontWeight: "bold",
            height: "42px",  
          }}
        >

          {loading
            ? "Importing..."
            : "Upload POS Data"}

        </button>

      </div>

      {/* ================= ERROR ================= */}

      {result?.error && (

        <div
          style={{
            background: "#ffe5e5",
            padding: 20,
            borderRadius: 15,
            marginBottom: 25,
          }}
        >

          <h3 style={{ color: "red" }}>
            Error
          </h3>

          <p>{result.error}</p>

        </div>
      )}

      {/* ================= SUCCESS ================= */}

      {result && !result.error && (

        <>

          {/* ================= SUMMARY CARDS ================= */}

          <div
            style={{
              display: "grid",
              gridTemplateColumns:
                  "repeat(auto-fit, minmax(180px, 1fr))",
              gap: 15,
              marginBottom: 25,
            }}
          >

            <div
              style={{
                flex: 1,
                minWidth: 220,
                background: "#ffffff",
                padding: 15,
                borderRadius: 12,
                borderLeft: "8px solid #10b981",
                boxShadow: "0 2px 10px rgba(0,0,0,0.08)",
              }}
            >

              <h4 style={{ margin: 0 }}>Sales Created</h4>

              <h2 style={{ marginTop: 10 }}>{result.sales_created}</h2>

            </div>

            <div
              style={{
                flex: 1,
                minWidth: 220,
                background: "#ffffff",
                padding: 15,
                borderRadius: 12,
                borderLeft: "8px solid #3b82f6",
                boxShadow: "0 2px 10px rgba(0,0,0,0.08)",
              }}
            >

              <h4 style={{ margin: 0 }}>Products Auto Created</h4>

              <h2 style={{ marginTop: 10 }}>{result.products_auto_created}</h2>

            </div>

            <div
              style={{
                flex: 1,
                minWidth: 220,
                background: "#ffffff",
                padding: 15,
                borderRadius: 12,
                borderLeft: "8px solid #ef4444",
                boxShadow: "0 2px 10px rgba(0,0,0,0.08)",
              }}
            >

              <h4 style={{ margin: 0 }}>Skipped Rows</h4>

              <h2 style={{ marginTop: 10 }}>{result.skipped_rows}</h2>

            </div>
            <div
              style={{
                flex: 1,
                minWidth: 220,
                background: "#ffffff",
                padding: 15,
                borderRadius: 12,
                borderLeft: "8px solid #14b8a6",
                boxShadow: "0 2px 10px rgba(0,0,0,0.08)",
              }}
            >

              <h4 style={{ margin: 0 }}>Total Revenue</h4>

              <h2 style={{ marginTop: 10 }}>
                $
                {totalRevenue.toLocaleString(
                  "en-US",
                  {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2,
                  }
                )}
              </h2>

            </div>

            <div
              style={{
                flex: 1,
                minWidth: 220,
                background: "#ffffff",
                padding: 15,
                borderRadius: 12,
                borderLeft: "8px solid #10b981",
                boxShadow: "0 2px 10px rgba(0,0,0,0.08)",
              }}
            >

              <h4 style={{ margin: 0 }}>Top Product</h4>

              <h2 style={{ marginTop: 10 }}>
                {topProduct?.name || "-"}
              </h2>

            </div>

            <div
              style={{
                flex: 1,
                minWidth: 220,
                background: "#ffffff",
                padding: 15,
                borderRadius: 12,
                borderLeft: "8px solid #ef4444",
                boxShadow: "0 2px 10px rgba(0,0,0,0.08)",
              }}
            >

              <h4 style={{ margin: 0 }}>Lowest Product</h4>

              <h2 style={{ marginTop: 10 }}>
                {lowProduct?.name || "-"}
              </h2>

            </div>  

          </div>

          {/* ================= IMPORT DETAILS ================= */}

          <div
            style={{
              background: "#ffffff",
              padding: 25,
              borderRadius: 15,
              marginBottom: 30,
              boxShadow: "0 2px 10px rgba(0,0,0,0.08)",
            }}
          >

            <h2>Import Successful</h2>

            <p>
                <b>File:</b> {result.filename}
            </p>

            <br />

            <button
               onClick={archiveCurrent}
               style={{
                   padding: "12px 20px",
                   border: "none",
                   borderRadius: 10,
                   background: "#f59e0b",
                   color: "#fff",
                   cursor: "pointer",
                   fontWeight: "bold",
                }}
            >
               Archive Data
            </button>

          

          </div>

          <div
            style={{
              background: "#ffffff",
              padding: 20,
              borderRadius: 15,
              marginBottom: 30,
              boxShadow: "0 2px 10px rgba(0,0,0,0.08)",
              display: "flex",
              gap: 20,
              flexWrap: "wrap",
              alignItems: "center",
            }}
          >

            <h3 style={{ marginRight: 20 }}>
              Dashboard Filters
            </h3>

            <div>

              <label>Product</label>

              <br />

              <select
                value={productFilter}
                onChange={(e) =>
                  setProductFilter(e.target.value)
                }
              >

                <option value="all">
                  All Products
                </option>

                {sortedRevenueData.map((item) => (

                  <option
                    key={item.name}
                    value={item.name}
                  >
                    {item.name}
                  </option>

                ))}

              </select>

            </div>

            <div>

              <label>Time</label>

              <br />

              <select
                value={timeFilter}
                onChange={(e) =>
                  setTimeFilter(e.target.value)
                }
              >

                <option value="all">All</option>

                <option value="day">Day</option>

                <option value="week">Week</option>

                <option value="month">Month</option>

                <option value="year">Year</option>

             </select>

            </div>

          </div>  

          <div
            style={{
             display: "grid",
             gridTemplateColumns: "1fr 1fr",
             gap: 20,
             marginBottom: 30,
            }}
         >

         {/* ================= BAR CHART ================= */}

          <div
            style={{
              background: "#ffffff",
              padding: 25,
              borderRadius: 15,
              marginBottom: 30,
              boxShadow: "0 2px 10px rgba(0,0,0,0.08)",
            }}
          >

            <h2>
              Revenue by Product
            </h2>

            <button
              onClick={() =>
                setFullscreenChart(

                  <ResponsiveContainer
                    width="100%"
                    height="100%"
                  >

                    <BarChart
                      data={sortedRevenueData}
                    >

                      <CartesianGrid
                        strokeDasharray="3 3"
                      />

                      <XAxis dataKey="name" />

                      <YAxis />

                      <Tooltip />

                      <Legend />

                      <Bar
                        dataKey="revenue"
                        fill="#3b82f6"
                      />

                    </BarChart>

                  </ResponsiveContainer>

                )
              }
            >

              Fullscreen

            </button>
            

            <div style={{ width: "100%", height: 280 }}>

              <ResponsiveContainer width="100%" height="100%">

                <BarChart data={sortedRevenueData}>

                  <CartesianGrid strokeDasharray="3 3" />

                  <XAxis dataKey="name" />

                  <YAxis />

                  <Tooltip />

                  <Legend />

                  <Bar
                    dataKey="revenue"
                    fill="#3b82f6"
                  />

                </BarChart>

              </ResponsiveContainer>

            </div>

          </div>

          {/* ================= LINE CHART ================= */}

          <div
            style={{
              background: "#ffffff",
              padding: 25,
              borderRadius: 15,
              marginBottom: 30,
              boxShadow: "0 2px 10px rgba(0,0,0,0.08)",
            }}
          >

            <h2>
              Revenue Trend
            </h2>

            <button
              onClick={() =>
                setFullscreenChart(

                  <ResponsiveContainer
                    width="100%"
                    height="100%"
                  >

                    <LineChart
                      data={dailyRevenueData}
                    >

                      <CartesianGrid
                        strokeDasharray="3 3"
                      />

                      <XAxis dataKey="date" />

                      <YAxis />

                      <Tooltip />

                      <Legend />

                      <Line
                        type="monotone"
                        dataKey="revenue"
                        stroke="#10b981"
                        strokeWidth={3}
                      />

                    </LineChart>

                  </ResponsiveContainer>

                )
              }
            >

              Fullscreen

            </button>

            <div style={{ width: "100%", height: 280 }}>

              <ResponsiveContainer width="100%" height="100%">

                <LineChart data={dailyRevenueData}>

                  <CartesianGrid strokeDasharray="3 3" />

                  <XAxis dataKey="date" />

                  <YAxis />

                  <Tooltip />

                  <Legend />

                  <Line
                    type="monotone"
                    dataKey="revenue"
                    stroke="#10b981"
                    strokeWidth={3}
                  />

                </LineChart>

              </ResponsiveContainer>

            </div>

          </div>

          {/* ================= PIE CHART ================= */}

          <div
            style={{
              background: "#ffffff",
              padding: 25,
              borderRadius: 15,
              marginBottom: 30,
              boxShadow: "0 2px 10px rgba(0,0,0,0.08)",
            }}
          >

            <h2>
              Revenue Distribution
            </h2>

            <button
              onClick={() =>
                setFullscreenChart(

                  <ResponsiveContainer
                    width="100%"
                    height="100%"
                  >

                    <PieChart>

                      <Pie
                        data={pieData}
                        dataKey="revenue"
                        nameKey="name"
                        outerRadius={250}
                        label
                      >

                        {pieData.map(
                          (
                            entry,
                            index
                          ) => (

                            <Cell
                              key={index}
                              fill={
                                COLORS[
                                  index %
                                  COLORS.length
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
         >

           Fullscreen

         </button>

            <div style={{ width: "100%", height: 320 }}>

              <ResponsiveContainer width="100%" height="100%">

                <PieChart>

                  <Pie
                    data={pieData}
                    dataKey="revenue"
                    nameKey="name"
                    outerRadius={150}
                    label
                  >

                    {pieData.map((entry, index) => (

                      <Cell
                        key={index}
                        fill={
                          COLORS[
                            index % COLORS.length
                          ]
                        }
                      />

                    ))}

                  </Pie>

                  <Tooltip />

                </PieChart>

              </ResponsiveContainer>

            </div>

          </div>

              
              

          {/* ================= REVENUE SUMMARY ================= */}

          <div
            style={{
              background: "#ffffff",
              padding: 25,
              borderRadius: 15,
              marginBottom: 30,
              boxShadow: "0 2px 10px rgba(0,0,0,0.08)",
            }}
          >

            <h2>Revenue Summary</h2>

            <table
              border="1"
              cellPadding="10"
              width="100%"
            >

              <thead>

                <tr>
                  <th>Product</th>
                  <th>Revenue</th>
                </tr>

              </thead>

              <tbody>

                {filteredRevenueData.map((item) => (
                  
                

                  <tr key={item.name}>

                    <td>{item.name}</td>

                    <td>
                      $
                      {item.revenue.toLocaleString(
                        "en-US",
                        {
                          minimumFractionDigits: 2,
                          maximumFractionDigits: 2,
                        }
                      )}
                    </td>

                  </tr>

                ))}

              </tbody>

            </table>

          </div>
           <div
             style={{
                background: "#ffffff",
                padding: 25,
                borderRadius: 15,
                marginBottom: 30,
                boxShadow: "0 2px 10px rgba(0,0,0,0.08)",
            }}
          >

            <h2>Top Performers</h2>

            <table
              border="1"
              cellPadding="10"
              width="100%"
            >

             <thead>

               <tr>
                <th>Rank</th>
                <th>Product</th>
                <th>Revenue</th>
               </tr>

            </thead>

            <tbody>

              {filteredRevenueData
                .slice(0, 5)
                .map((item, index) => (

                  <tr key={item.name}>

                    <td>
                      #{index + 1}
                    </td>

                    <td>
                      {item.name}
                    </td>

                    <td>
                      $
                      {item.revenue.toLocaleString(
                        "en-US",
                      {
                        minimumFractionDigits: 2,
                        maximumFractionDigits: 2,
                      }
                    )}
                    </td>

                  </tr>

               ))}

            </tbody>

          </table>

         </div>
          <div
            style={{
              background: "#ffffff",
              padding: 25,
              borderRadius: 15,
              marginBottom: 30,
              boxShadow: "0 2px 10px rgba(0,0,0,0.08)",
            }}
          >

            <h2>Low Performers</h2>

            <table
              border="1"
              cellPadding="10"
              width="100%"
            >

              <thead>

                <tr>
                  <th>Rank</th>
                  <th>Product</th>
                  <th>Revenue</th>
                </tr>

              </thead>

              <tbody>

                {[...filteredRevenueData]
                  .reverse()
                  .slice(0, 5)
                  .map((item, index) => (

                    <tr key={item.name}>

                      <td>
                        #{index + 1}
                      </td>

                      <td>
                        {item.name}
                      </td>

                      <td>
                        $
                        {item.revenue.toLocaleString(
                          "en-US",
                        {
                            minimumFractionDigits: 2,
                            maximumFractionDigits: 2,
                        }
                      )}
                      </td>

                    </tr>

                 ))}

               </tbody>

             </table>

           </div>    
          </div>    
       </>
    )}
{/* ================= ARCHIVES ================= */}

{archives.length > 0 && (

  <div
    style={{
      background: "#ffffff",
      padding: 25,
      borderRadius: 15,
      marginBottom: 30,
      boxShadow: "0 2px 10px rgba(0,0,0,0.08)",
    }}
  >

    <h2>Archived Analyses</h2>

    <table
      border="1"
      cellPadding="10"
      width="100%"
    >

      <thead>

        <tr>
          <th>Name</th>
          <th>Archived</th>
          <th>Actions</th>
        </tr>

      </thead>

      <tbody>

        {archives.map((archive) => (

          <tr key={archive.id}>

            <td>{archive.name}</td>

            <td>{archive.archivedAt}</td>

            <td>

              <button
                onClick={() =>
                  loadArchive(archive)
                }
              >
                Open
              </button>

              {" "}

              <button
                onClick={() =>
                  deleteArchive(archive.id)
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

)}
       

    </div>
  );
}