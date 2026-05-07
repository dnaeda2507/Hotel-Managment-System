import { useState } from 'react';
import api from '../api/authApi';
import type { Issue, ReportResponse } from '../types/aiReview';

const API_BASE = '/agents/review-ai';

export default function ReviewAnalysisPanel() {
  const [period, setPeriod] = useState<'daily' | 'weekly'>('daily');
  const [report, setReport] = useState<ReportResponse | null>(null);
  const [loading, setLoading] = useState(false);

  const fetchReport = async () => {
    setLoading(true);
    setReport(null);
    try {
      const res = await api.get<ReportResponse>(`${API_BASE}/auto-report`, {
        params: { period },
      });
      setReport(res.data);
    } catch {
      alert('Rapor alınamadı!');
    }
    setLoading(false);
  };

  const cleaningIssues = (report?.detected_issues ?? []).filter(i => i.type === 'cleaning');
  const maintenanceIssues = (report?.detected_issues ?? []).filter(i => i.type === 'maintenance');
  const cleaningTasks = (report?.generated_tasks ?? []).filter(t => t.task_type === 'cleaning');
  const maintenanceTasks = (report?.generated_tasks ?? []).filter(t => t.task_type === 'maintenance');

  return (
    <div style={{ maxWidth: 860, margin: '0 auto', padding: 24, fontFamily: 'sans-serif' }}>
      <h2 style={{ marginBottom: 4 }}>Yorum Analizi</h2>
      <p style={{ color: '#6b7280', marginTop: 0, marginBottom: 20, fontSize: 14 }}>
        Misafir yorumları analiz edilir, sorunlar otomatik olarak tespit edilip görev oluşturulur.
      </p>

      {/* Kontroller */}
      <div style={{ display: 'flex', gap: 12, alignItems: 'center', marginBottom: 24 }}>
        <select
          value={period}
          onChange={e => setPeriod(e.target.value as 'daily' | 'weekly')}
          style={{ padding: '6px 12px', borderRadius: 6, border: '1px solid #d1d5db' }}
        >
          <option value="daily">Günlük</option>
          <option value="weekly">Haftalık</option>
        </select>
        <button
          onClick={fetchReport}
          disabled={loading}
          style={{
            padding: '7px 20px', borderRadius: 6, border: 'none',
            background: loading ? '#9ca3af' : '#2563eb', color: '#fff',
            cursor: loading ? 'not-allowed' : 'pointer', fontWeight: 600,
          }}
        >
          {loading ? 'Analiz ediliyor…' : 'Rapor Ver'}
        </button>
      </div>

      {loading && (
        <div style={{ padding: 20, textAlign: 'center', color: '#6b7280' }}>
          LangGraph analiz yapıyor — classifier → temizlik ajanı + bakım ajanı → koordinatör…
        </div>
      )}

      {report && (
        <div>
          {/* Rapor Özeti */}
          <section style={{
            background: '#f0f9ff', border: '1px solid #bae6fd',
            borderRadius: 8, padding: 16, marginBottom: 20,
          }}>
            <h3 style={{ margin: '0 0 10px', color: '#0369a1' }}>Rapor Özeti</h3>
            <p style={{ margin: 0, lineHeight: 1.6, whiteSpace: 'pre-wrap' }}>{report.report}</p>
          </section>

          {/* Otomatik Oluşturulan Görevler */}
          {(report.generated_tasks ?? []).length > 0 && (
            <section style={{ marginBottom: 24 }}>
              <h3 style={{ marginBottom: 12 }}>
                Otomatik Oluşturulan Görevler
                <span style={{
                  marginLeft: 8, fontSize: 13, fontWeight: 400,
                  background: '#dcfce7', color: '#16a34a',
                  padding: '2px 8px', borderRadius: 12,
                }}>
                  {report.generated_tasks!.length} görev
                </span>
              </h3>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                {/* Temizlik görevleri */}
                <div>
                  <h4 style={{ margin: '0 0 8px', color: '#0891b2', fontSize: 14 }}>
                    Temizlik ({cleaningTasks.length})
                  </h4>
                  {cleaningTasks.length === 0
                    ? <p style={{ color: '#9ca3af', fontSize: 13 }}>Görev yok</p>
                    : cleaningTasks.map((task, idx) => (
                      <div key={idx} style={{
                        background: '#fff', border: '1px solid #e0f2fe',
                        borderRadius: 6, padding: '8px 12px', marginBottom: 8,
                        borderLeft: '3px solid #0891b2',
                      }}>
                        <div style={{ fontWeight: 600, fontSize: 13 }}>Oda {task.room_id}</div>
                        <div style={{ fontSize: 12, color: '#374151', marginTop: 2 }}>{task.desc}</div>
                        <div style={{ fontSize: 11, color: '#9ca3af', marginTop: 4 }}>
                          {new Date(task.date).toLocaleString('tr-TR')}
                        </div>
                      </div>
                    ))
                  }
                </div>

                {/* Bakım görevleri */}
                <div>
                  <h4 style={{ margin: '0 0 8px', color: '#7c3aed', fontSize: 14 }}>
                    Bakım ({maintenanceTasks.length})
                  </h4>
                  {maintenanceTasks.length === 0
                    ? <p style={{ color: '#9ca3af', fontSize: 13 }}>Görev yok</p>
                    : maintenanceTasks.map((task, idx) => (
                      <div key={idx} style={{
                        background: '#fff', border: '1px solid #ede9fe',
                        borderRadius: 6, padding: '8px 12px', marginBottom: 8,
                        borderLeft: '3px solid #7c3aed',
                      }}>
                        <div style={{ fontWeight: 600, fontSize: 13 }}>Oda {task.room_id}</div>
                        <div style={{ fontSize: 12, color: '#374151', marginTop: 2 }}>{task.desc}</div>
                        <div style={{ fontSize: 11, color: '#9ca3af', marginTop: 4 }}>
                          {new Date(task.date).toLocaleString('tr-TR')}
                        </div>
                      </div>
                    ))
                  }
                </div>
              </div>
            </section>
          )}

          {/* Tespit Edilen Sorunlar — sadece görüntüleme */}
          {(report.detected_issues ?? []).length > 0 && (
            <section>
              <h3 style={{ marginBottom: 12 }}>Tespit Edilen Sorunlar</h3>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                {/* Temizlik sorunları */}
                <div>
                  <h4 style={{ margin: '0 0 8px', color: '#0891b2', fontSize: 14 }}>
                    Temizlik ({cleaningIssues.length})
                  </h4>
                  {cleaningIssues.map((issue, idx) => (
                    <IssueCard key={idx} issue={issue} />
                  ))}
                </div>
                {/* Bakım sorunları */}
                <div>
                  <h4 style={{ margin: '0 0 8px', color: '#7c3aed', fontSize: 14 }}>
                    Bakım ({maintenanceIssues.length})
                  </h4>
                  {maintenanceIssues.map((issue, idx) => (
                    <IssueCard key={idx} issue={issue} />
                  ))}
                </div>
              </div>
            </section>
          )}

          {(report.detected_issues ?? []).length === 0 && (
            <div style={{ textAlign: 'center', color: '#9ca3af', padding: 32 }}>
              Bu dönemde tespit edilen sorun yok.
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function IssueCard({ issue }: { issue: Issue }) {
  return (
    <div style={{
      background: '#fafafa', border: '1px solid #e5e7eb',
      borderRadius: 6, padding: '8px 12px', marginBottom: 8,
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span style={{ fontWeight: 600, fontSize: 13 }}>Oda {issue.room_id}</span>
        {issue.auto_assigned && (
          <span style={{
            fontSize: 11, background: '#dcfce7', color: '#16a34a',
            padding: '1px 7px', borderRadius: 10,
          }}>
            Görev oluşturuldu
          </span>
        )}
      </div>
      <div style={{ fontSize: 12, color: '#4b5563', marginTop: 3 }}>{issue.desc}</div>
    </div>
  );
}
