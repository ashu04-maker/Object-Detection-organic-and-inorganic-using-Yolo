import React, { useState, useEffect } from "react";
import { useDropzone } from "react-dropzone";
import "./App.css";

function App() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState([]);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const response = await fetch("http://localhost:8000/history");
        const data = await response.json();
        setHistory(data.reverse());
      } catch (error) {
        console.error("Error fetching history:", error);
      }
    };

    fetchHistory();
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: "image/*",
    maxFiles: 1,
    onDrop: async (acceptedFiles) => {
      setLoading(true);
      const formData = new FormData();
      formData.append("file", acceptedFiles[0]);

      try {
        const response = await fetch("http://localhost:8000/upload", {
          method: "POST",
          body: formData,
        });
        const data = await response.json();
        setResult(data);
        setHistory((prev) => [data, ...prev]);
      } catch (error) {
        console.error("Upload error:", error);
      }
      setLoading(false);
    },
  });

  // Function to parse the detection string into an array of objects
  const parseDetections = (detectionString) => {
    if (!detectionString) return [];

    // Example string: "1 person, 3 bottles, 1 cup, 2 apples, 1 mouse"
    const parts = detectionString.split(", ");
    return parts.map((part) => {
      const [count, ...objectParts] = part.split(" ");
      const objectName = objectParts.join(" ");
      return {
        count: parseInt(count),
        name: objectName,
      };
    });
  };

  const deleteHistoryItem = async (imageName) => {
    try {
      const response = await fetch(
        `http://localhost:8000/history/${imageName}`,
        {
          method: "DELETE",
        }
      );

      if (!response.ok) {
        throw new Error("Failed to delete item");
      }

      // Refresh the history after deletion
      const historyResponse = await fetch("http://localhost:8000/history");
      const updatedHistory = await historyResponse.json();
      setHistory(updatedHistory.reverse());
    } catch (error) {
      console.error("Error deleting history item:", error);
      setError("Failed to delete item. Please try again.");
    }
  };

  return (
    <div className="app-container">
      <div className="main-container">
        <h1 className="app-header">Image Classifier</h1>

        <div
          {...getRootProps()}
          className={`dropzone ${isDragActive ? "active" : ""}`}
        >
          <input {...getInputProps()} />
          <div className="dropzone-content">
            {isDragActive ? (
              <p className="drop-text">Drop the image here...</p>
            ) : (
              <>
                <svg className="upload-icon" viewBox="0 0 24 24">
                  <path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z" />
                </svg>
                <p className="drop-text">Click to upload or drag & drop</p>
                <p className="format-text">Supported formats: JPEG, PNG</p>
              </>
            )}
          </div>
        </div>

        {loading && (
          <div className="loading-container">
            <div className="spinner"></div>
            <p className="loading-text">Analyzing waste composition...</p>
          </div>
        )}

        {result ? (
          <div className="result-container">
            <h2 className="result-header">Analysis Results</h2>
            <div className="result-grid">
              <div className="result-card organic">
                <h3>Organic</h3>
                <p className="result-value">{result.organic}</p>
                <p className="result-percentage">
                  {result.organic_percentage}%
                </p>
              </div>
              <div className="result-card inorganic">
                <h3>Inorganic</h3>
                <p className="result-value">{result.inorganic}</p>
                <p className="result-percentage">
                  {result.inorganic_percentage}%
                </p>
              </div>
            </div>

            {/* Display detected objects */}
            {result.detections && (
              <div className="detected-objects-container">
                <h3 className="detected-objects-header">Detected Objects</h3>
                <div className="detected-objects-grid">
                  {parseDetections(result.detections).map((item, index) => (
                    <div key={index} className="detected-object-card">
                      <span className="object-count">{item.count}x</span>
                      <span className="object-name">{item.name}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {result.image && (
              <div className="image-preview">
                <img
                  src={`http://localhost:8000/processed_images/${result.image}`}
                  alt="Processed waste"
                  className="processed-image"
                  onError={(e) => {
                    e.target.onerror = null;
                    e.target.src = "placeholder.jpg";
                  }}
                />
              </div>
            )}
          </div>
        ) : (
          <div className="empty-state">
            <p className="empty-text">
              Upload an image to analyze waste composition
            </p>
            <p className="empty-subtext">
              Our AI will classify organic and inorganic materials
            </p>
          </div>
        )}

        <div className="history-section">
          <h2 className="history-header">Classification History</h2>
          {history.length > 0 ? (
            <div className="history-table-container">
              <table className="history-table">
                <thead>
                  <tr>
                    <th>Preview</th>
                    <th>Organic</th>
                    <th>Inorganic</th>
                    <th>Detected Objects</th>
                    <th>Date</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {history.map((item, index) => (
                    <tr key={index}>
                      <td>
                        <div className="thumbnail-container">
                          <img
                            src={`http://localhost:8000/processed_images/${item.image}`}
                            alt="Classification result"
                            className="history-thumbnail"
                          />
                        </div>
                      </td>
                      <td className="organic-data">
                        {item.organic} <span>({item.organic_percentage}%)</span>
                      </td>
                      <td className="inorganic-data">
                        {item.inorganic}{" "}
                        <span>({item.inorganic_percentage}%)</span>
                      </td>
                      <td className="detected-objects-data">
                        {item.detections ? (
                          <div className="history-detected-objects">
                            {parseDetections(item.detections).map((obj, i) => (
                              <span key={i} className="history-object-item">
                                {obj.count}x {obj.name}
                                {i < parseDetections(item.detections).length - 1
                                  ? ", "
                                  : ""}
                              </span>
                            ))}
                          </div>
                        ) : (
                          "N/A"
                        )}
                      </td>
                      <td className="date-data">
                        {item.date || "N/A"}
                        <br />
                        {item.time || "N/A"}
                      </td>
                      <td className="actions-data">
                        <button
                          onClick={() => deleteHistoryItem(item.image)}
                          className="delete-button"
                          title="Delete this entry"
                        >
                          <svg className="delete-icon" viewBox="0 0 24 24">
                            <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z" />
                          </svg>
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="empty-history">
              <p>No classification history yet</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
