import React, { useEffect, useState } from 'react';
import { Button, Select, message } from 'antd';
import { FileTextOutlined, DownloadOutlined, RocketOutlined } from '@ant-design/icons';
import { PageHeader, StepStatusPill, LimeSquiggle } from '../../components/common/Common';
import { useSession } from '../../context/SessionContext';
import { reportingService } from '../../services/reportingService';
import './ReportingModule.css';

const API_BASE = (import.meta as any).env?.VITE_API_BASE_URL || 'http://localhost:8000';

const ReportingModule: React.FC = () => {
  const { refreshStatus } = useSession();
  const [templates, setTemplates] = useState<any[]>([]);
  const [reportType, setReportType] = useState('full');
  const [generating, setGenerating] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [report, setReport] = useState<any>(null);

  useEffect(() => {
    reportingService.getReportTemplates()
      .then((list) => {
        setTemplates(list);
        if (list.length && list[0].id) setReportType(list[0].id);
      })
      .catch(() => undefined);
  }, []);

  const handleGenerate = async () => {
    setGenerating(true);
    setReport(null);
    try {
      const res = await reportingService.generateReport(reportType);
      setReport(res);
      message.success('报告生成成功');
      await refreshStatus();
    } catch (e: any) {
      message.error(`生成失败：${e?.message || e}`);
    } finally {
      setGenerating(false);
    }
  };

  const handleExport = async (format: 'html' | 'pdf' | 'excel') => {
    if (!report?.report_id) return;
    setExporting(true);
    try {
      const resp = await fetch(
        `${API_BASE}/api/reporting/export/${encodeURIComponent(report.report_id)}?format=${format}`
      );
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      const blob = await resp.blob();
      reportingService.downloadReport(blob, `report_${report.report_id}.${format === 'excel' ? 'xlsx' : format}`);
      message.success('导出成功');
    } catch (e: any) {
      message.error(`导出失败：${e?.message || e}`);
    } finally {
      setExporting(false);
    }
  };

  return (
    <div className="df-page">
      <PageHeader
        eyebrow="STEP 06 · REPORT"
        title={<>数据<span className="df-lime-chip">报表</span></>}
        description="汇总本次会话的导入、清洗、分析与可视化结果，生成报告并导出。"
        extra={<StepStatusPill step="report" />}
      />

      <div className="df-grid-2">
        <div className="df-card df-card-lg">
          <div className="df-eyebrow df-card-eyebrow">TEMPLATE</div>
          <h3 className="df-card-title">选择报告模板</h3>
          <div className="df-template-list">
            {templates.map((t) => (
              <div
                key={t.id}
                className={`df-template-item ${reportType === t.id ? 'df-template-active' : ''}`}
                onClick={() => setReportType(t.id)}
              >
                <div className="df-template-name">
                  <FileTextOutlined /> {t.name || t.id}
                </div>
                <div className="df-caption">{t.description || ''}</div>
              </div>
            ))}
          </div>
          <Button type="primary" icon={<RocketOutlined />} loading={generating} onClick={handleGenerate} block>
            生成报告
          </Button>
        </div>

        <div className="df-card df-card-lg">
          <div className="df-eyebrow df-card-eyebrow">EXPORT</div>
          <h3 className="df-card-title">导出报告</h3>
          {report ? (
            <>
              <div className="df-pill df-pill-done" style={{ marginBottom: 12 }}>
                {report.message || '报告生成成功'}
              </div>
              <div className="df-caption df-report-id">
                报告 ID：<span className="df-code">{report.report_id}</span>
              </div>
              <div className="df-export-row">
                <Button icon={<DownloadOutlined />} loading={exporting} onClick={() => handleExport('html')}>
                  导出 HTML
                </Button>
                <Select
                  defaultValue="html"
                  style={{ width: 140 }}
                  options={[
                    { value: 'html', label: 'HTML（推荐）', key: 'html' },
                    { value: 'pdf', label: 'PDF', key: 'pdf' },
                    { value: 'excel', label: 'Excel', key: 'excel' },
                  ]}
                  onChange={(v: 'html' | 'pdf' | 'excel') => handleExport(v)}
                  placeholder="选择格式导出"
                />
              </div>
              <LimeSquiggle />
            </>
          ) : (
            <div className="df-empty">
              <FileTextOutlined style={{ fontSize: 28 }} />
              <div>生成报告后，可在此导出文件</div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ReportingModule;
