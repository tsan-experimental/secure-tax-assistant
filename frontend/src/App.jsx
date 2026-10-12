import { useEffect, useState } from 'react'
import './App.css'

function App() {
  const [backendData, setBackendData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch('http://127.0.0.1:8000/')
      .then((res) => res.json())
      .then((data) => {
        setBackendData(data)
        setLoading(false)
      })
      .catch((err) => {
        console.error('Connection error:', err)
        setLoading(false)
      })
  }, [])

  return (
    <div style={{ padding: '2rem', fontFamily: 'Arial, sans-serif' }}>
      <h1>Secure Tax Assistant</h1>
      <h2>Frontend-Backend Connection Test</h2>
      {loading ? (
        <p>Connecting to backend...</p>
      ) : backendData ? (
        <div style={{ background: '#e2f0d9', padding: '1rem', borderRadius: '8px', border: '1px solid #c8e6c9' }}>
          <p><strong>Status:</strong> {backendData.status}</p>
          <p><strong>Message:</strong> {backendData.message}</p>
        </div>
      ) : (
        <p style={{ color: 'red' }}>Could not connect to FastAPI backend.</p>
      )}
    </div>
  )
}

export default App