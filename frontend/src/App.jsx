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

  const decisionColor = result?.final_decision === 'ACCEPT' ? '#22c55e' : result?.final_decision === 'REJECT' ? '#ef4444' : result?.final_decision === 'MODIFY' ? '#f59e0b' : '#6366f1';

  return (
    <div style={{ minHeight: '100vh', background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 100%)', color: '#f8fafc', fontFamily: "'Inter', system-ui, sans-serif", padding: '2rem 1rem' }}>
      <div style={{ maxWidth: 860, margin: '0 auto' }}>
        <h1 style={{ fontSize: '2.5rem', fontWeight: 800, letterSpacing: '-0.03em', background: 'linear-gradient(90deg, #60a5fa, #c084fc)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', marginBottom: 8 }}>
          AI Purchasing Agent
        </h1>
        <p style={{ color: '#94a3b8', fontSize: '1.05rem', marginBottom: '2rem' }}>
          Scenario 1 • Purchase Recommendation Review • LangGraph • Groq
        </p>

        <form onSubmit={submit} style={{ display: 'flex', gap: 12, alignItems: 'end', background: 'rgba(255,255,255,0.05)', padding: '1.25rem', borderRadius: 16, border: '1px solid rgba(255,255,255,0.08)', marginBottom: '2rem', backdropFilter: 'blur(8px)' }}>
          <div>
            <label style={{ display: 'block', fontWeight: 600, fontSize: 13, color: '#cbd5e1', marginBottom: 6, textTransform: 'uppercase', letterSpacing: 0.5 }}>SKU</label>
            <input value={sku} onChange={e => setSku(e.target.value)} style={{ padding: '10px 14px', borderRadius: 10, border: '1px solid rgba(255,255,255,0.15)', background: '#0b1220', color: '#f8fafc', fontSize: 15, width: 130 }} />
          </div>
          <div>
            <label style={{ display: 'block', fontWeight: 600, fontSize: 13, color: '#cbd5e1', marginBottom: 6, textTransform: 'uppercase', letterSpacing: 0.5 }}>Quantity</label>
            <input type="number" value={qty} onChange={e => setQty(e.target.value)} style={{ padding: '10px 14px', borderRadius: 10, border: '1px solid rgba(255,255,255,0.15)', background: '#0b1220', color: '#f8fafc', fontSize: 15, width: 100 }} />
          </div>
          <button type="submit" disabled={loading} style={{ padding: '10px 22px', borderRadius: 10, border: 'none', background: 'linear-gradient(90deg, #6366f1, #a855f7)', color: '#fff', fontWeight: 700, fontSize: 15, cursor: 'pointer', boxShadow: '0 4px 20px rgba(168,85,247,0.35)' }}>
            {loading ? 'Evaluating…' : 'Evaluate Purchase'}
          </button>
        </form>

        {error && <div style={{ background: '#fee2e2', color: '#7f1d1d', padding: 14, borderRadius: 12, border: '1px solid #fecaca', marginBottom: 20, fontWeight: 500 }}>{error}</div>}

        {result && (
          <div style={{ background: 'rgba(255,255,255,0.03)', padding: '2rem', borderRadius: 20, border: '1px solid rgba(255,255,255,0.1)', boxShadow: '0 20px 40px rgba(0,0,0,0.3)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 20 }}>
              <span style={{ fontSize: '0.85rem', fontWeight: 700, color: '#f8fafc', background: decisionColor, padding: '6px 14px', borderRadius: 999, letterSpacing: 0.5, textTransform: 'uppercase' }}>{result.final_decision}</span>
              <h2 style={{ fontSize: '1.5rem', fontWeight: 700, margin: 0 }}>
                Final Decision
              </h2>
            </div>

            <section style={{ marginBottom: 24 }}>
              <h3 style={{ fontSize: '0.9rem', textTransform: 'uppercase', letterSpacing: 1, color: '#94a3b8', borderBottom: '1px solid rgba(255,255,255,0.1)', paddingBottom: 8, marginBottom: 12 }}>Reasoning Trace</h3>
              <pre style={{ background: '#0b1220', padding: 14, borderRadius: 12, overflow: 'auto', maxHeight: 260, fontSize: 13, lineHeight: 1.6, border: '1px solid rgba(255,255,255,0.06)' }}>
                {JSON.stringify(result.reasoning_trace || [], null, 2)}
              </pre>
            </section>

            <section style={{ marginBottom: 24 }}>
              <h3 style={{ fontSize: '0.9rem', textTransform: 'uppercase', letterSpacing: 1, color: '#94a3b8', borderBottom: '1px solid rgba(255,255,255,0.1)', paddingBottom: 8, marginBottom: 12 }}>Action Taken</h3>
              <pre style={{ background: '#0b1220', padding: 14, borderRadius: 12, fontSize: 13, border: '1px solid rgba(255,255,255,0.06)' }}>{JSON.stringify(result.action_taken || [], null, 2)}</pre>
            </section>

            <section>
              <h3 style={{ fontSize: '0.9rem', textTransform: 'uppercase', letterSpacing: 1, color: '#94a3b8', borderBottom: '1px solid rgba(255,255,255,0.1)', paddingBottom: 8, marginBottom: 12 }}>Validation Outcome</h3>
              <pre style={{ background: '#0b1220', padding: 14, borderRadius: 12, fontSize: 13, border: '1px solid rgba(255,255,255,0.06)' }}>{JSON.stringify(result.validation_result || {}, null, 2)}</pre>
            </section>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
