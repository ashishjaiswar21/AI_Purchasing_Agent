import { useState } from 'react';

function App() {
  const [sku, setSku] = useState('SKU-101');
  const [qty, setQty] = useState(100);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  async function submit(e) {
    e.preventDefault();
    setLoading(true); setResult(null); setError(null);
    try {
      const res = await fetch('http://localhost:8000/evaluate-purchase', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sku, quantity: Number(qty), supplier_id: 'SUP-A' }),
      });
      if (!res.ok) throw new Error(await res.text());
      setResult(await res.json());
    } catch (e) { setError(e.message); }
    setLoading(false);
  }

  return (
    <div style={{ maxWidth: 800, margin: '2rem auto', fontFamily: 'system-ui, sans-serif', padding: '0 1rem' }}>
      <h1>AI Purchasing Agent — Scenario 1</h1>
      <form onSubmit={submit} style={{ display: 'flex', gap: 10, alignItems: 'end', marginBottom: '1.5rem' }}>
        <div>
          <label>SKU</label><br />
          <input value={sku} onChange={e => setSku(e.target.value)} style={{ padding: 6, width: 120 }} />
        </div>
        <div>
          <label>Quantity</label><br />
          <input type="number" value={qty} onChange={e => setQty(e.target.value)} style={{ padding: 6, width: 100 }} />
        </div>
        <button type="submit" disabled={loading} style={{ padding: '6px 16px', cursor: 'pointer' }}>
          {loading ? 'Evaluating...' : 'Submit'}
        </button>
      </form>

      {error && <pre style={{ color: 'crimson', background: '#fee', padding: 12 }}>{error}</pre>}

      {result && (
        <div style={{ background: '#f5f5f5', padding: '1rem', borderRadius: 8, border: '1px solid #ddd' }}>
          <h2>Results</h2>
          <section style={{ marginBottom: 12 }}>
            <strong>Final Decision:</strong> <span style={{ fontWeight: 700, color: result.final_decision === 'ACCEPT' ? 'green' : result.final_decision === 'REJECT' ? 'red' : 'orange' }}>{result.final_decision}</span>
          </section>
          <section style={{ marginBottom: 12 }}>
            <strong>Reasoning Trace:</strong>
            <pre style={{ background: '#fff', padding: 10, overflow: 'auto', maxHeight: 220, border: '1px solid #ccc', fontSize: 13 }}>{JSON.stringify(result.reasoning_trace || [], null, 2)}</pre>
          </section>
          <section style={{ marginBottom: 12 }}>
            <strong>Action Taken:</strong> <pre style={{ background: '#fff', padding: 8, fontSize: 13 }}>{JSON.stringify(result.action_taken || [], null, 2)}</pre>
          </section>
          <section>
            <strong>Validation Result:</strong> <pre style={{ background: '#fff', padding: 8, fontSize: 13 }}>{JSON.stringify(result.validation_result || {}, null, 2)}</pre>
          </section>
        </div>
      )}
    </div>
  );
}

export default App;
