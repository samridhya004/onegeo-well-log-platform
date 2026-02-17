import { useEffect, useState } from "react";
import axios from "axios";
import Plot from "react-plotly.js";
import "./index.css";

const API_BASE = "http://127.0.0.1:8000";

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState(null);
  const [uploadType, setUploadType] = useState(null); // success | error | warning
  const [wells, setWells] = useState([]);
  const [selectedWell, setSelectedWell] = useState("");
  const [curves, setCurves] = useState([]);
  const [selectedCurve, setSelectedCurve] = useState("");
  const [curveStats, setCurveStats] = useState(null);
  const [minDepth, setMinDepth] = useState("");
  const [maxDepth, setMaxDepth] = useState("");
  const [plotData, setPlotData] = useState(null);
  const [interpretation, setInterpretation] = useState(null);
  
  const handleUpload = async () => {
    if (!selectedFile) return;
  
    const formData = new FormData();
    formData.append("file", selectedFile);
  
    try {
      setUploading(true);
  
      const response = await axios.post(
        `${API_BASE}/api/wells/upload`,
        formData,
        { headers: { "Content-Type": "multipart/form-data" } }
      );
  
      if (response.data.duplicate) {
        setUploadMessage("File already uploaded. Existing well loaded.");
        setUploadType("warning");
  
        setSelectedWell(response.data.well_id);
  
        // refresh wells
        const wellsRes = await axios.get(`${API_BASE}/api/wells`);
        setWells(wellsRes.data);
  
        return;
      }
  
      setUploadMessage("Upload successful!");
      setUploadType("success");
  
      const wellsRes = await axios.get(`${API_BASE}/api/wells`);
      setWells(wellsRes.data);
  
    } catch (error) {
      const message =
        error.response?.data?.detail ||
        "Upload failed due to server error.";
  
      setUploadMessage(message);
      setUploadType("error");        
    } finally {
      setUploading(false);
    }
  };
  
  useEffect(() => {
    axios.get(`${API_BASE}/api/wells`)
      .then(res => setWells(res.data))
      .catch(err => console.error(err));
  }, []);

  useEffect(() => {
    if (!selectedWell) return;

    axios.get(`${API_BASE}/api/wells/${selectedWell}/curves`)
      .then(res => setCurves(res.data))
      .catch(err => console.error(err));
  }, [selectedWell]);

  const fetchInterpretation = async () => {
    if (!selectedCurve || !minDepth || !maxDepth) return;
  
    try {
      const res = await axios.post(
        `${API_BASE}/api/interpret`,
        null,
        {
          params: {
            curve_id: selectedCurve,
            min_depth: minDepth,
            max_depth: maxDepth
          }
        }
      );
  
      setInterpretation(res.data);
  
    } catch (error) {
      console.error(error);
      setInterpretation(null);
    }
  };  

  const fetchCurveData = async () => {
    if (!selectedCurve || !minDepth || !maxDepth) return;

    try {
      const res = await axios.get(
        `${API_BASE}/api/curves/${selectedCurve}/data`,
        {
          params: {
            min_depth: minDepth,
            max_depth: maxDepth
          }
        }
      );

      const depths = res.data.map(d => d.depth);
      const values = res.data.map(d => d.value);

      setPlotData({ x: values, y: depths });
      
      const stats = {
        min: Math.min(...values),
        max: Math.max(...values),
        avg: values.reduce((a, b) => a + b, 0) / values.length,
        count: values.length
      };
      
      setCurveStats(stats);
      fetchInterpretation();
      
    } catch (error) {
      console.error(error);
      alert("Error fetching curve data.");
    }
  };


  return (
    <div className="app-container">
      <div className="header">
        <h1>OneGeo Well Log Platform</h1>
        <p>Subsurface well-log visualization and AI-assisted interpretation</p>
      </div>

      <div className="content">
        <div className="left-panel">
        <label>Upload LAS File</label>
        <input
          type="file"
          accept=".las"
          onChange={(e) => setSelectedFile(e.target.files[0])}
        />
        <button
          onClick={handleUpload}
          disabled={uploading}
        >
          {uploading ? "Uploading..." : "Upload File"}
        </button>
        
        {uploadMessage && (
          <div className={`upload-message ${uploadType}`}>
            {uploadMessage}
          </div>
        )}

          <label>Select Well</label>
          <select value={selectedWell} onChange={e => {
            setSelectedWell(e.target.value);
            setSelectedCurve("");
            setPlotData(null);
          }}>
            <option value="">Choose well</option>
            {wells.map(w => (
              <option key={w.id} value={w.id}>{w.name}</option>
            ))}
          </select>

          <label>Select Curve</label>
          <select value={selectedCurve} onChange={e => setSelectedCurve(e.target.value)}>
            <option value="">Choose curve</option>
            {curves.map(c => (
              <option key={c.id} value={c.id}>{c.mnemonic}</option>
            ))}
          </select>

          <label>Min Depth</label>
          <input
            type="number"
            value={minDepth}
            onChange={e => setMinDepth(e.target.value)}
          />

          <label>Max Depth</label>
          <input
            type="number"
            value={maxDepth}
            onChange={e => setMaxDepth(e.target.value)}
          />

          <button onClick={fetchCurveData}>Plot Curve</button>
        </div>

        <div className="right-panel">
          {plotData ? (
            <>
              <div className="plot-container">
                <div className="plot-header">
                  <strong>Curve:</strong> {curves.find(c => c.id == selectedCurve)?.mnemonic}
                  &nbsp; | &nbsp;
                  <strong>Depth Range:</strong> {minDepth} – {maxDepth}
                </div>
                <Plot
                  data={[
                    {
                      x: plotData.x,
                      y: plotData.y,
                      type: "scatter",
                      mode: "lines",
                      line: { color: "#2f80ed" }
                    }
                  ]}
                  layout={{
                    title: "Curve vs Depth",
                    yaxis: { autorange: "reversed", title: "Depth" },
                    xaxis: { title: "Value" },
                    autosize: true,
                    margin: { t: 40, l: 60, r: 20, b: 50 }
                  }}
                  style={{ width: "100%", height: "100%" }}
                  config={{ responsive: true }}
                  useResizeHandler={true}
                />
              </div>

              <div className="stats-panel">
                <h4>Curve Summary</h4>

                <div className="stats-grid">
                  <div className="stat-card">
                    <span>Points</span>
                    <strong>{curveStats?.count}</strong>
                  </div>

                  <div className="stat-card">
                    <span>Min</span>
                    <strong>{curveStats?.min?.toFixed(2)}</strong>
                  </div>

                  <div className="stat-card">
                    <span>Max</span>
                    <strong>{curveStats?.max?.toFixed(2)}</strong>
                  </div>

                  <div className="stat-card">
                    <span>Average</span>
                    <strong>{curveStats?.avg?.toFixed(2)}</strong>
                  </div>
                </div>
              </div>

              {interpretation && (
                <div className="ai-panel">
                  <h4>AI Interpretation (Rule-Based Engine)</h4>
                  <ul>
                    {interpretation.interpretation.map((item, index) => (
                      <li key={index}>{item}</li>
                    ))}
                  </ul>
                </div>
              )}
            </>
          ) : (
            <div className="empty-state">
              Select well, curve and depth range to visualize data.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
