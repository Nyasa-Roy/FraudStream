"use client";

import { useEffect, useState } from "react";

type Event = { transaction_id?: string; id?: number; amount?: number; risk_level?: string; risk_score?: number; status?: string };
type Analytics = { transaction_count: number; alert_count: number; risk_distribution: Record<string, number> };

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

function RiskBadge({ level }: { level?: string }) {
  return <span className={`badge ${(level ?? "LOW").toLowerCase()}`}>{level ?? "LOW"}</span>;
}

export default function Dashboard() {
  const [analytics, setAnalytics] = useState<Analytics>({ transaction_count: 0, alert_count: 0, risk_distribution: {} });
  const [transactions, setTransactions] = useState<Event[]>([]);
  const [alerts, setAlerts] = useState<Event[]>([]);
  useEffect(() => {
    fetch(`${API}/fraud/analytics`).then((response) => response.json()).then(setAnalytics).catch(() => undefined);
    fetch(`${API}/transactions`).then((response) => response.json()).then(setTransactions).catch(() => undefined);
    fetch(`${API}/fraud/alerts`).then((response) => response.json()).then(setAlerts).catch(() => undefined);
    const connect = (path: string, handler: (event: Event) => void) => {
      const socket = new WebSocket(`${API.replace("http", "ws")}${path}`);
      socket.onmessage = (message) => handler(JSON.parse(message.data));
      return socket;
    };
    const transactionSocket = connect("/ws/transactions", (event) => setTransactions((current) => [event, ...current].slice(0, 50)));
    const alertSocket = connect("/ws/alerts", (event) => setAlerts((current) => [event, ...current].slice(0, 50)));
    return () => { transactionSocket.close(); alertSocket.close(); };
  }, []);
  return <main><header><div><p className="eyebrow">LIVE OPERATIONS</p><h1>FraudStream</h1></div><span className="status"><i /> Connected</span></header>
    <section className="kpis"><Kpi label="Transactions" value={analytics.transaction_count} /><Kpi label="Open alerts" value={analytics.alert_count} danger /><Kpi label="High risk" value={analytics.risk_distribution.HIGH ?? 0} danger /><Kpi label="Medium risk" value={analytics.risk_distribution.MEDIUM ?? 0} /></section>
    <section className="grid"><Panel title="Live transactions"><div className="table">{transactions.map((event, index) => <div className="row" key={`${event.transaction_id ?? event.id}-${index}`}><span>{event.transaction_id ?? "—"}</span><span>${event.amount?.toFixed(2) ?? "0.00"}</span><RiskBadge level={event.risk_level} /></div>)}{transactions.length === 0 && <p className="empty">Waiting for transaction events…</p>}</div></Panel>
      <Panel title="Fraud alerts"><div className="table">{alerts.map((event, index) => <div className="row" key={`${event.id}-${index}`}><span>{event.transaction_id ?? "Alert"}</span><span>{((event.risk_score ?? 0) * 100).toFixed(0)}%</span><RiskBadge level="HIGH" /></div>)}{alerts.length === 0 && <p className="empty">No open alerts</p>}</div></Panel></section>
  </main>;
}

function Kpi({ label, value, danger = false }: { label: string; value: number; danger?: boolean }) { return <div className={`kpi ${danger ? "danger" : ""}`}><span>{label}</span><strong>{value.toLocaleString()}</strong></div>; }
function Panel({ title, children }: { title: string; children: React.ReactNode }) { return <article className="panel"><h2>{title}</h2>{children}</article>; }

