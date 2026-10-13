import { useState, useEffect, useCallback } from 'react';
import ReactMarkdown from 'react-markdown';

const API_BASE = 'http://127.0.0.1:8000';

// ─── Tab Definitions ────────────────────────────────────────────────────────────

const TABS = [
  { id: 'organizer', label: '📄 Organizer' },
  { id: 'trigger',   label: '📞 Trigger' },
  { id: 'upload',    label: '📎 Upload' },
  { id: 'progress',  label: '📊 Progress' },
];

// ─── Main App ───────────────────────────────────────────────────────────────────

function App() {
  const [clientId, setClientId] = useState('1');
  const [activeTab, setActiveTab] = useState('organizer');

  return (
    <div style={{ padding: '2rem', fontFamily: 'system-ui, -apple-system, sans-serif', maxWidth: '900px', margin: '0 auto', textAlign: 'left' }}>
      <h1 style={{ borderBottom: '2px solid #333', paddingBottom: '0.5rem', marginBottom: '1.5rem' }}>
        🔒 Secure Tax Assistant
      </h1>

      {/* Client ID Selector */}
      <div style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <label style={{ fontWeight: 'bold' }}>Client ID:</label>
        <input
          type="number"
          min="1"
          max="4"
          value={clientId}
          onChange={(e) => setClientId(e.target.value)}
          style={{ padding: '0.4rem 0.8rem', fontSize: '1rem', borderRadius: '4px', border: '1px solid #ccc', width: '60px' }}
        />
        <span style={{ fontSize: '0.85rem', color: '#666' }}>
          (1: Alice Smith, 2: Bob Jones, 3: Charlie Davis, 4: David Miller)
        </span>
      </div>

      {/* Tab Navigation */}
      <div style={{ display: 'flex', gap: '0', marginBottom: '0', borderBottom: '2px solid #e0e0e0' }}>
        {TABS.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            style={{
              padding: '0.6rem 1.2rem',
              fontSize: '0.95rem',
              cursor: 'pointer',
              border: 'none',
              borderBottom: activeTab === tab.id ? '2px solid #0066cc' : '2px solid transparent',
              backgroundColor: activeTab === tab.id ? '#f0f7ff' : 'transparent',
              fontWeight: activeTab === tab.id ? '600' : '400',
              color: activeTab === tab.id ? '#0066cc' : '#555',
              marginBottom: '-2px',
            }}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div style={{ paddingTop: '1.5rem' }}>
        {activeTab === 'organizer' && <OrganizerTab clientId={clientId} />}
        {activeTab === 'trigger'   && <TriggerTab clientId={clientId} />}
        {activeTab === 'upload'    && <UploadTab clientId={clientId} />}
        {activeTab === 'progress'  && <ProgressTab clientId={clientId} />}
      </div>
    </div>
  );
}

// ─── Tab 1: Organizer ───────────────────────────────────────────────────────────

function OrganizerTab({ clientId }) {
  const [organizer, setOrganizer] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const fetchOrganizer = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await fetch(`${API_BASE}/organizer/${clientId}`);
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || `HTTP ${res.status}`);
      }
      const data = await res.json();
      setOrganizer(data.organizer);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div style={{ marginBottom: '1rem' }}>
        <button onClick={fetchOrganizer} disabled={loading} style={buttonStyle}>
          {loading ? 'Generating Report…' : 'Fetch Organizer'}
        </button>
      </div>
      {error && <div style={errorStyle}>{error}</div>}
      {organizer && (
        <div style={cardStyle}>
          <ReactMarkdown
            components={{
              h1: ({ node, ...props }) => <h1 style={{ fontSize: '1.4rem', margin: '1rem 0 0.5rem 0' }} {...props} />,
              h2: ({ node, ...props }) => <h2 style={{ fontSize: '1.15rem', margin: '1rem 0 0.5rem 0', color: '#0066cc' }} {...props} />,
              ul: ({ node, ...props }) => <ul style={{ paddingLeft: '1.2rem', margin: '0.5rem 0' }} {...props} />,
              li: ({ node, ...props }) => <li style={{ marginBottom: '0.3rem' }} {...props} />,
              p:  ({ node, ...props }) => <p style={{ margin: '0.5rem 0', lineHeight: '1.6' }} {...props} />,
            }}
          >
            {organizer}
          </ReactMarkdown>
        </div>
      )}
    </div>
  );
}

// ─── Tab 2: Trigger Lookup ──────────────────────────────────────────────────────

function TriggerTab({ clientId }) {
  const [phrase, setPhrase] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const submitTrigger = async () => {
    if (!phrase.trim()) return;
    setLoading(true);
    setError('');
    try {
      const res = await fetch(`${API_BASE}/trigger-lookup/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ client_id: parseInt(clientId), phrase }),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || `HTTP ${res.status}`);
      }
      setResult(await res.json());
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const suggestions = ['audit notice', 'missing W-2', 'missing 1099'];

  return (
    <div>
      <p style={{ color: '#555', marginBottom: '0.75rem' }}>
        Type a trigger phrase to get recommended next steps. Try:
      </p>
      <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem', flexWrap: 'wrap' }}>
        {suggestions.map((s) => (
          <button key={s} onClick={() => setPhrase(s)} style={chipStyle}>
            {s}
          </button>
        ))}
      </div>

      <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem' }}>
        <input
          type="text"
          value={phrase}
          onChange={(e) => setPhrase(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && submitTrigger()}
          placeholder="e.g., audit notice"
          style={{ ...inputStyle, flex: 1 }}
        />
        <button onClick={submitTrigger} disabled={loading} style={buttonStyle}>
          {loading ? '…' : 'Analyze'}
        </button>
      </div>

      {error && <div style={errorStyle}>{error}</div>}

      {result && (
        <div style={cardStyle}>
          <h3 style={{ margin: '0 0 0.5rem 0', color: '#0066cc' }}>Recommended Actions</h3>
          <ul style={{ paddingLeft: '1.2rem', margin: '0 0 1rem 0' }}>
            {result.recommendations.map((r, i) => (
              <li key={i} style={{ marginBottom: '0.3rem' }}>{r}</li>
            ))}
          </ul>
          {result.missing_documents.length > 0 && (
            <>
              <h4 style={{ margin: '0.5rem 0 0.3rem 0' }}>Currently Missing</h4>
              <ul style={{ paddingLeft: '1.2rem', color: '#c0392b' }}>
                {result.missing_documents.map((d, i) => (
                  <li key={i}>{d}</li>
                ))}
              </ul>
            </>
          )}
        </div>
      )}
    </div>
  );
}

// ─── Tab 3: Document Upload Simulation ─────────────────────────────────────────

function UploadTab({ clientId }) {
  const [taxYear, setTaxYear] = useState('2025');
  const [docName, setDocName] = useState('');
  const [simText, setSimText] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const submitUpload = async () => {
    if (!docName.trim()) return;
    setLoading(true);
    setError('');
    try {
      const res = await fetch(`${API_BASE}/upload-document/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          client_id: parseInt(clientId),
          tax_year: parseInt(taxYear),
          document_name: docName,
          simulated_text: simText || 'Simulated document content for testing.',
        }),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || `HTTP ${res.status}`);
      }
      setResult(await res.json());
      setDocName('');
      setSimText('');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <p style={{ color: '#555', marginBottom: '0.75rem' }}>
        Simulate uploading a document. This updates the client's checklist from "Missing" → "Received".
      </p>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', marginBottom: '1rem' }}>
        <div>
          <label style={labelStyle}>Tax Year</label>
          <select value={taxYear} onChange={(e) => setTaxYear(e.target.value)} style={inputStyle}>
            <option value="2023">2023</option>
            <option value="2024">2024</option>
            <option value="2025">2025</option>
          </select>
        </div>
        <div>
          <label style={labelStyle}>Document Name</label>
          <input
            type="text"
            value={docName}
            onChange={(e) => setDocName(e.target.value)}
            placeholder="e.g., Form W-2"
            style={inputStyle}
          />
        </div>
      </div>

      <div style={{ marginBottom: '1rem' }}>
        <label style={labelStyle}>Simulated Document Text (optional — for PII redaction demo)</label>
        <textarea
          value={simText}
          onChange={(e) => setSimText(e.target.value)}
          placeholder="Paste mock document text containing PII to see redaction in action…"
          style={{ ...inputStyle, height: '80px', resize: 'vertical' }}
        />
      </div>

      <button onClick={submitUpload} disabled={loading || !docName.trim()} style={buttonStyle}>
        {loading ? 'Uploading…' : 'Simulate Upload'}
      </button>

      {error && <div style={{ ...errorStyle, marginTop: '1rem' }}>{error}</div>}

      {result && (
        <div style={{ ...cardStyle, marginTop: '1rem', borderLeft: '4px solid #27ae60' }}>
          <p style={{ margin: 0, color: '#27ae60', fontWeight: '600' }}>{result.message}</p>
          <p style={{ margin: '0.5rem 0 0 0', fontSize: '0.9rem', color: '#666' }}>
            Received at: {result.received_at}
          </p>
          {result.extracted_preview && (
            <p style={{ margin: '0.5rem 0 0 0', fontSize: '0.85rem', color: '#555', fontFamily: 'monospace' }}>
              Preview: {result.extracted_preview}
            </p>
          )}
        </div>
      )}
    </div>
  );
}

// ─── Tab 4: Progress / Checklist ────────────────────────────────────────────────

function ProgressTab({ clientId }) {
  const [data, setData] = useState(null);
  const [error, setError] = useState('');

  const fetchStatus = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/client/${clientId}/status`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      setData(await res.json());
    } catch (err) {
      setError(err.message);
    }
  }, [clientId]);

  useEffect(() => { fetchStatus(); }, [fetchStatus]);

  if (error) return <div style={errorStyle}>{error}</div>;
  if (!data) return <p>Loading…</p>;

  return (
    <div>
      {/* Progress Bar */}
      <div style={{ marginBottom: '1.5rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.3rem' }}>
          <span style={{ fontWeight: '600' }}>Documentation Progress</span>
          <span style={{ color: '#555' }}>{data.progress} docs received</span>
        </div>
        <div style={{ width: '100%', height: '12px', backgroundColor: '#e0e0e0', borderRadius: '6px', overflow: 'hidden' }}>
          <div
            style={{
              width: `${data.percent}%`,
              height: '100%',
              backgroundColor: data.percent === 100 ? '#27ae60' : '#0066cc',
              borderRadius: '6px',
              transition: 'width 0.4s ease',
            }}
          />
        </div>
        <span style={{ fontSize: '0.85rem', color: '#555' }}>{data.percent}% complete</span>
      </div>

      {/* Checklist Table */}
      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.9rem' }}>
        <thead>
          <tr style={{ borderBottom: '2px solid #e0e0e0', textAlign: 'left' }}>
            <th style={thStyle}>Tax Year</th>
            <th style={thStyle}>Document</th>
            <th style={thStyle}>Status</th>
            <th style={thStyle}>Received At</th>
          </tr>
        </thead>
        <tbody>
          {data.checklist.map((item, i) => (
            <tr key={i} style={{ borderBottom: '1px solid #f0f0f0' }}>
              <td style={tdStyle}>{item.year}</td>
              <td style={tdStyle}>{item.doc}</td>
              <td style={tdStyle}>
                <span
                  style={{
                    padding: '0.15rem 0.5rem',
                    borderRadius: '4px',
                    fontSize: '0.8rem',
                    fontWeight: '600',
                    backgroundColor: item.status === 'Received' ? '#d4edda' : '#f8d7da',
                    color: item.status === 'Received' ? '#155724' : '#721c24',
                  }}
                >
                  {item.status}
                </span>
              </td>
              <td style={{ ...tdStyle, fontSize: '0.8rem', color: '#888' }}>
                {item.received_at || '—'}
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <button onClick={fetchStatus} style={{ ...buttonStyle, marginTop: '1rem', backgroundColor: '#555' }}>
        ↻ Refresh
      </button>
    </div>
  );
}

// ─── Shared Styles ──────────────────────────────────────────────────────────────

const buttonStyle = {
  padding: '0.4rem 1rem',
  fontSize: '0.95rem',
  cursor: 'pointer',
  borderRadius: '4px',
  backgroundColor: '#0066cc',
  color: '#fff',
  border: 'none',
};

const chipStyle = {
  padding: '0.25rem 0.6rem',
  fontSize: '0.85rem',
  cursor: 'pointer',
  borderRadius: '12px',
  backgroundColor: '#f0f7ff',
  border: '1px solid #cce5ff',
  color: '#0066cc',
};

const inputStyle = {
  padding: '0.4rem 0.8rem',
  fontSize: '0.95rem',
  borderRadius: '4px',
  border: '1px solid #ccc',
  width: '100%',
  boxSizing: 'border-box',
};

const labelStyle = {
  display: 'block',
  fontWeight: '600',
  fontSize: '0.85rem',
  marginBottom: '0.25rem',
  color: '#333',
};

const cardStyle = {
  border: '1px solid #e0e0e0',
  padding: '1.5rem',
  borderRadius: '8px',
  background: '#ffffff',
  boxShadow: '0 2px 8px rgba(0,0,0,0.05)',
  color: '#222',
  lineHeight: '1.6',
};

const errorStyle = {
  padding: '0.75rem 1rem',
  backgroundColor: '#f8d7da',
  color: '#721c24',
  borderRadius: '4px',
  marginBottom: '1rem',
  fontSize: '0.9rem',
};

const thStyle = { padding: '0.5rem 0.75rem', fontWeight: '600' };
const tdStyle = { padding: '0.5rem 0.75rem' };

export default App;   