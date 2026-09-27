import { useState } from 'react';

export default function App() {
  const [sku, setSku] = useState('SKU-101');
  const [qty, setQty] = useState(100);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  async function submit(e) {
    e.preventDefault();
    setLoading(true); setResult(null); setError(null);
    try {
      const r = await fetch('http://localhost:8000/evaluate-purchase', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sku, quantity: Number(qty), supplier_id: 'SUP-A' }),
      });
      if (!r.ok) throw new Error(await r.text());
      setResult(await r.json());
    } catch (e) { setError(String(e)); }
    setLoading(false);
  }

  const decisionColor = result?.final_decision === 'ACCEPT' ? '#10b981' : result?.final_decision === 'REJECT' ? '#ef4444' : result?.final_decision === 'MODIFY' ? '#f59e0b' : '#8b5cf6';

  return (
    <div style={{ minHeight: '100vh', background: '#0b0f19', color: '#e2e8f0', fontFamily: "'Inter', ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif", padding: '3rem 1.5rem', lineHeight: 1.6 }}>
      <div style={{ maxWidth: 960, margin: '0 auto' }}>
        {/* Header */}
        <header style={{ marginBottom: 48 }}>
          <div style={{ display: 'inline-flex', alignItems: 'center', gap: 10, background: 'rgba(255,255,255,0.05)', padding: '6px 14px', borderRadius: 999, border: '1px solid rgba(255,255,255,0.08)', fontSize: 12, fontWeight: 600, color: '#94a3b8', letterSpacing: 0.5, marginBottom: 12 }}>
            <span style={{ width: 8, height: 8, borderRadius: '50%', background: '#22d3ee', boxShadow: '0 0 8px #22d3ee' }} />
            LIVE AGENT • LANGGRAPH • GROQ
          </div>
          <h1 style={{ fontSize: '3rem', fontWeight: 800, letterSpacing: '-0.035em', lineHeight: 1.1, background: 'linear-gradient(135deg, #f8fafc 0%, #a78bfa 60%, #38bdf8 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', margin: 0, paddingBottom: 4, textShadow: 'none' }}>
            Purchase Evaluation
          </h1>
          <p style={{ color: '#94a3b8', fontSize: '1.15rem', marginTop: 12, maxWidth: 600, fontWeight: 400 }}>
            Scenario 1 • Real-time recommendation review with inventory, demand, supplier constraints and validation loop.
          </p>
        </header>

        {/* Form */}
        <section style={{ background: 'rgba(255,255,255,0.035)', border: '1px solid rgba(255,255,255,0.07)', borderRadius: 20, padding: '2rem', backdropFilter: 'blur(12px)', marginBottom: 32, boxShadow: '0 1px 3px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.05)' }}>
          <form onSubmit={submit} style={{ display: 'flex', gap: 16, alignItems: 'end', flexWrap: 'wrap' }}>
            <div style={{ flex: 1, minWidth: 160 }}>
              <label htmlFor="sku" style={{ display: 'block', fontSize: 11, fontWeight: 700, color: '#94a3b8', textTransform: 'uppercase', letterSpacing: 1, marginBottom: 6 }}>SKU</label>
              <input id="sku" value={sku} onChange={e => setSku(e.target.value)} style={{ width: '100%', padding: '12px 14px', borderRadius: 10, border: '1px solid rgba(255,255,255,0.12)', background: '#0f1222', color: '#f8fafc', fontSize: 15, outline: 'none', transition: 'border-color .15s, box-shadow .15s' }} onFocus={e => e.target.style.borderColor = '#a78bfa'} onBlur={e => e.target.style.borderColor = 'rgba(255,255,255,0.12)'} />
            </div>
            <div style={{ flex: 1, minWidth: 160 }}>
              <label htmlFor="qty" style={{ display: 'block', fontSize: 11, fontWeight: 700, color: '#94a3b8', textTransform: 'uppercase', letterSpacing: 1, marginBottom: 6 }}>Quantity</label>
              <input id="qty" type="number" value={qty} onChange={e => setQty(e.target.value)} style={{ width: '100%', padding: '12px 14px', borderRadius: 10, border: '1px solid rgba(255,255,255,0.12)', background: '#0f1222', color: '#f8fafc', fontSize: 15, outline: 'none', transition: 'border-color .15s, box-shadow .15s' }} onFocus={e => e.target.style.borderColor = '#a78bfa'} onBlur={e => e.target.style.borderColor = 'rgba(255,255,255,0.12)'} />
            </div>
            <button type="submit" disabled={loading} style={{ padding: '12px 28px', borderRadius: 12, border: 'none', background: 'linear-gradient(135deg, #7c3aed, #a855f7)', color: '#fff', fontWeight: 700, fontSize: 15, cursor: loading ? 'wait' : 'pointer', boxShadow: '0 10px 30px rgba(124,58,237,0.35)', transition: 'transform .08s, box-shadow .15s', letterSpacing: 0.2 }} onMouseDown={e => { e.currentTarget.style.transform = 'translateY(2px)'; e.currentTarget.style.boxShadow = '0 4px 15px rgba(124,58,237,0.3)'; }} onMouseUp={e => { e.currentTarget.style.transform = 'translateY(0)'; e.currentTarget.style.boxShadow = '0 10px 30px rgba(124,58,237,0.35)'; }}>
              {loading ? 'Evaluating…' : 'Evaluate'}
            </button>
          </form>
        </section>

        {error && (
          <div style={{ background: '#450a0a', color: '#fecaca', padding: 14, borderRadius: 12, border: '1px solid #7f1d1d', marginBottom: 28, fontWeight: 500, fontSize: 14 }}>
            {error}
          </div>
        )}

        {result && (
          <section style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 24, padding: '2.5rem', boxShadow: '0 25px 60px rgba(0,0,0,0.35)', backdropFilter: 'blur(14px)' }}>
            {/* Header row */}
            <div style={{ display: 'flex', alignItems: 'center', gap: 14, marginBottom: 28, flexWrap: 'wrap' }}>
              <span style={{ display: 'inline-flex', alignItems: 'center', gap: 8, background: decisionColor + '18', color: decisionColor, padding: '8px 16px', borderRadius: 999, fontWeight: 800, fontSize: 15, letterSpacing: 0.5, border: '1px solid ' + decisionColor + '40' }}>
                <span style={{ width: 8, height: 8, borderRadius: '50%', background: decisionColor, boxShadow: '0 0 6px ' + decisionColor }} />
                {result.final_decision}
              </span>
              <h2 style={{ fontSize: '1.6rem', fontWeight: 800, margin: 0, letterSpacing: '-0.02em', color: '#f1f5f9' }}>Agent Decision</h2>
            </div>

            {/* Reasoning */}
            <div style={{ marginBottom: 28 }}>
              <h3 style={{ fontSize: 11, textTransform: 'uppercase', letterSpacing: 1.2, color: '#94a3b8', fontWeight: 700, marginBottom: 14, borderBottom: '1px solid rgba(255,255,255,0.08)', paddingBottom: 10 }}>Reasoning Trace</h3>
              <div style={{ background: '#0b1222', padding: 16, borderRadius: 14, overflow: 'auto', maxHeight: 320, fontSize: 13, lineHeight: 1.65, border: '1px solid rgba(255,255,255,0.06)', whiteSpace: 'pre-wrap', color: '#cbd5e1', fontFamily: "'Fira Code', ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace" }}>
                {JSON.stringify(result.reasoning_trace || [], null, 2)}
              </div>
            </div>

            {/* Action */}
            <div style={{ marginBottom: 28 }}>
              <h3 style={{ fontSize: 11, textTransform: 'uppercase', letterSpacing: 1.2, color: '#94a3b8', fontWeight: 700, marginBottom: 14, borderBottom: '1px solid rgba(255,255,255,0.08)', paddingBottom: 10 }}>Action Taken</h3>
              <div style={{ background: '#0b1222', padding: 14, borderRadius: 14, border: '1px solid rgba(255,255,255,0.06)', fontSize: 13, color: '#cbd5e1', fontFamily: "'Fira Code', ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace" }}>
                {JSON.stringify(result.action_taken || [], null, 2)}
              </div>
            </div>

            {/* Validation */}
            <div>
              <h3 style={{ fontSize: 11, textTransform: 'uppercase', letterSpacing: 1.2, color: '#94a3b8', fontWeight: 700, marginBottom: 14, borderBottom: '1px solid rgba(255,255,255,0.08)', paddingBottom: 10 }}>Validation Outcome</h3>
              <div style={{ background: '#0b1222', padding: 14, borderRadius: 14, border: '1px solid rgba(255,255,255,0.06)', fontSize: 13, color: '#cbd5e1', fontFamily: "'Fira Code', ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace" }}>
                {JSON.stringify(result.validation_result || {}, null, 2)}
              </div>
            </div>
          </section>
        )}
      </div>
    </div>
  );
}
