import React, { useState } from "react";
import { bulkUpload } from "../api";

export default function BulkUpload() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);

  const upload = async () => {
    if (!file) return;
    const res = await bulkUpload(file);
    setResult(res);
  };

  return (
    <div>
      <h2>Bulk Upload</h2>

      <input type="file" onChange={e => setFile(e.target.files[0])} />
      <button onClick={upload}>Upload</button>

      {result && (
        <div>
          <h3>Sales Created: {result.sales_created}</h3>

          <h4>Grouped Totals</h4>
          {Object.entries(result.grouped || {}).map(([k, v]) => (
            <div key={k}>{k}: ${v}</div>
          ))}
        </div>
      )}
    </div>
  );
}