import { useState } from 'react';
import ReactMarkdown from 'react-markdown';

function App() {
  const [clientId, setClientId] = useState('1');
  const [organizer, setOrganizer] = useState('');
  const [loading, setLoading] = useState(false);

  const fetchOrganizer = async () => {
    setLoading(true);
    try {
      const res = await fetch(`http://127.0.0.1:8000/organizer/${clientId}`);
      const data = await res.json();
      setOrganizer(data.organizer);
    } catch (err) {
      console.error("Error fetching organizer:", err);
      setOrganizer("Failed to load organizer.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '2rem', fontFamily: 'system-ui, -apple-system, sans-serif', maxWidth: '800px', margin: '0 auto', textAlign: 'left' }}>
      <h1 style={{ borderBottom: '2px solid #333', paddingBottom: '0.5rem', marginBottom: '1.5rem' }}>Secure Tax Assistant</h1>
      
      <div style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <label style={{ fontWeight: 'bold' }}>Client ID:</label>
        <input 
          type="number" 
          value={clientId} 
          onChange={(e) => setClientId(e.target.value)} 
          style={{ padding: '0.4rem 0.8rem', fontSize: '1rem', borderRadius: '4px', border: '1px solid #ccc' }}
        />
        <button 
          onClick={fetchOrganizer} 
          disabled={loading}
          style={{ padding: '0.4rem 1rem', fontSize: '1rem', cursor: 'pointer', borderRadius: '4px', backgroundColor: '#0066cc', color: '#fff', border: 'none' }}
        >
          {loading ? 'Generating Report...' : 'Fetch Organizer'}
        </button>
      </div>

      {organizer && (
        <div style={{
          border: '1px solid #e0e0e0',
          padding: '2rem',
          borderRadius: '8px',
          background: '#ffffff',
          boxShadow: '0 2px 8px rgba(0,0,0,0.05)',
          color: '#222',
          lineHeight: '1.6',
          textAlign: 'left'
        }}>
          <ReactMarkdown
            components={{
              ul: ({ node, ...props }) => <ul style={{ paddingLeft: '1.2rem', margin: '0.5rem 0' }} {...props} />,
              li: ({ node, ...props }) => <li style={{ marginBottom: '0.3rem' }} {...props} />,
              h1: ({ node, ...props }) => <h1 style={{ fontSize: '1.5rem', margin: '1rem 0 0.5rem 0' }} {...props} />,
              h2: ({ node, ...props }) => <h2 style={{ fontSize: '1.2rem', margin: '1rem 0 0.5rem 0', color: '#0066cc' }} {...props} />,
            }}
          >
            {organizer}
          </ReactMarkdown>
        </div>
      )}
    </div>
  );
}

export default App;