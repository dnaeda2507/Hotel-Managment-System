import React, { useState } from 'react';
import api from '../api/authApi';
import type { Issue, Task, ReportResponse } from '../types/aiReview';

const API_BASE = '/agents/review-ai';

export default function ReviewAnalysisPanel() {
  const [period, setPeriod] = useState<'daily' | 'weekly'>('daily');
  const [report, setReport] = useState<ReportResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [selectedIssues, setSelectedIssues] = useState<Issue[]>([]);
  const [createdTasks, setCreatedTasks] = useState<Task[]>([]);

  const fetchReport = async () => {
    setLoading(true);
    setReport(null);
    setCreatedTasks([]);
    try {
      const res = await api.get<ReportResponse>(`${API_BASE}/auto-report`, {
        params: { period },
      });
      setReport(res.data);
    } catch (err) {
      alert('Rapor alınamadı!');
    }
    setLoading(false);
  };

  const handleSelectIssue = (issue: Issue) => {
    setSelectedIssues((prev) => {
      if (prev.some((i) => i.room_id === issue.room_id && i.desc === issue.desc)) {
        return prev.filter((i) => !(i.room_id === issue.room_id && i.desc === issue.desc));
      } else {
        return [...prev, issue];
      }
    });
  };

  const assignTasks = async () => {
    if (selectedIssues.length === 0) {
      alert('Lütfen en az bir madde seçin!');
      return;
    }
    setLoading(true);
    try {
      const res = await api.post<{ created_tasks: Task[] }>(`${API_BASE}/assign-selected-tasks`, selectedIssues);
      setCreatedTasks(res.data.created_tasks ?? []);
    } catch (err) {
      alert('Görevler atanamadı!');
    }
    setLoading(false);
  };

  return (
    <div style={{ maxWidth: 800, margin: '0 auto', padding: 24 }}>
      <h2>Yorum Analizi ve Otomatik Görev Paneli</h2>
      <div style={{ marginBottom: 16 }}>
        <label>Rapor Türü: </label>
        <select value={period} onChange={e => setPeriod(e.target.value as 'daily' | 'weekly')}>
          <option value="daily">Günlük</option>
          <option value="weekly">Haftalık</option>
        </select>
        <button onClick={fetchReport} disabled={loading} style={{ marginLeft: 12 }}>
          Rapor Ver
        </button>
      </div>
      {loading && <div>Yükleniyor...</div>}
      {report && (
        <div style={{ marginTop: 24 }}>
          <h3>Rapor Özeti</h3>
          <pre>{report.report}</pre>
          <h4>Analiz Edilen Maddeler</h4>
          <ul>
            {(report.detected_issues ?? []).map((issue, idx) => (
              <li key={idx} style={{ marginBottom: 8 }}>
                <label>
                  <input
                    type="checkbox"
                    checked={selectedIssues.some(i => i.room_id === issue.room_id && i.desc === issue.desc)}
                    onChange={() => handleSelectIssue(issue)}
                  />
                  {` Oda: ${issue.room_id}, Tür: ${issue.type}, Açıklama: ${issue.desc}, Tarih: ${issue.date || ''}`}
                </label>
              </li>
            ))}
          </ul>
          <button onClick={assignTasks} disabled={loading || selectedIssues.length === 0}>
            Seçili Maddeler İçin Görev Ata
          </button>
        </div>
      )}
      {(createdTasks ?? []).length > 0 && (
        <div style={{ marginTop: 24 }}>
          <h4>Oluşturulan Görevler</h4>
          <ul>
            {(createdTasks ?? []).map((task, idx) => (
              <li key={idx}>{`Oda: ${task.room_id}, Tür: ${task.task_type}, Açıklama: ${task.desc}, Tarih: ${task.date}`}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
