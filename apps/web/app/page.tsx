"use client";

import { FormEvent, useState } from "react";

type Result = { repository: string; files: number; lines: number; health_score: number; risks: { severity: string; category: string; message: string }[] };

export default function Home() {
  const [path, setPath] = useState(".");
  const [result, setResult] = useState<Result | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function analyze(e: FormEvent) {
    e.preventDefault(); setLoading(true); setError("");
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"}/v1/analyze`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ path }) });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail ?? "Analysis failed");
      setResult(data);
    } catch (err) { setError(err instanceof Error ? err.message : "Analysis failed"); }
    finally { setLoading(false); }
  }

  return <main className="shell">
    <header className="top"><div className="brand">PET</div><div className="tag">PERSONAL ENGINEERING TOOLKIT · v0.1</div></header>
    <section className="hero"><div className="eyebrow">Evidence-first engineering intelligence</div><h1>Understand the system.<br/>Improve the system.</h1><p>PET turns repository signals into a concise engineering health view — with deterministic analysis first, evidence attached to findings, and AI kept behind replaceable interfaces.</p></section>
    <section className="panel">
      <form className="row" onSubmit={analyze}><input className="input" value={path} onChange={e => setPath(e.target.value)} aria-label="Repository path" placeholder="/path/to/repository"/><button className="button" disabled={loading}>{loading ? "Analyzing…" : "Analyze repository"}</button></form>
      {error && <p role="alert">{error}</p>}
      {result && <div className="result"><div className="stats"><div className="stat"><small>Health</small><strong>{result.health_score}/100</strong></div><div className="stat"><small>Files</small><strong>{result.files}</strong></div><div className="stat"><small>Lines</small><strong>{result.lines.toLocaleString()}</strong></div><div className="stat"><small>Risks</small><strong>{result.risks.length}</strong></div></div><h3>{result.repository}</h3>{result.risks.length === 0 ? <p>No deterministic risks detected.</p> : result.risks.map((risk, i) => <div className="risk" key={i}><b>{risk.severity} · {risk.category}</b><p>{risk.message}</p></div>)}</div>}
    </section>
    <div className="footer">Local-first · deterministic analysis · provider-neutral architecture</div>
  </main>;
}
