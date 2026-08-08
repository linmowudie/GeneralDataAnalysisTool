import React, { useEffect, useState } from 'react';
import { Button, Select, message } from 'antd';
import { BarChartOutlined, LineChartOutlined, RightOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { PageHeader, StepStatusPill } from '../../components/common/Common';
import { useSession } from '../../context/SessionContext';
import { dataVisualizationService } from '../../services/dataVisualizationService';
import { dataAnalysisService } from '../../services/dataAnalysisService';
import './VisualizationModule.css';

const VisualizationModule: React.FC = () => {
  const navigate = useNavigate();
  const { refreshStatus, ready, sessionId } = useSession();
  const [charts, setCharts] = useState<string[]>([]);
  const [chartType, setChartType] = useState<string | undefined>();
  const [columns, setColumns] = useState<string[]>([]);
  const [xCol, setXCol] = useState<string | undefined>();
  const [yCol, setYCol] = useState<string | undefined>();
  const [loading, setLoading] = useState(false);
  const [chartResult, setChartResult] = useState<any>(null);
  const descriptions = dataVisualizationService.getChartTypeDescriptions();

  useEffect(() => {
    dataVisualizationService.getAvailableCharts()
      .then((list) => {
        setCharts(list);
        if (list.length) setChartType(list[0]);
      })
      .catch(() => undefined);
    if (ready && sessionId) {
      dataAnalysisService.getDataColumns(sessionId).then(setColumns);
    }
  }, [ready, sessionId]);

  const handleGenerate = async () => {
    if (!chartType) return;
    const parameters: Record<string, any> = {};
    if (xCol) parameters.x = xCol;
    if (yCol) parameters.y = yCol;
    setLoading(true);
    setChartResult(null);
    try {
      const res = await dataVisualizationService.generateChart(chartType, parameters);
      setChartResult(res);
      message.success('图表生成成功');
      await refreshStatus();
    } catch (e: any) {
      message.error(`图表生成失败：${e?.message || e}`);
    } finally {
      setLoading(false);
    }
  };

  // 尝试从 chart_data 字符串中解析出 base64 图片
  const extractImages = (): string[] => {
    try {
      const parsed = JSON.parse(chartResult?.chart_data?.replace(/'/g, '"') || '{}');
      const imgs: string[] = [];
      const walk = (v: any) => {
        if (typeof v === 'string' && v.length > 500 && /^[A-Za-z0-9+/=\s]+$/.test(v.slice(0, 100))) {
          imgs.push(v.replace(/\s/g, ''));
        } else if (v && typeof v === 'object') {
          Object.values(v).forEach(walk);
        }
      };
      walk(parsed);
      return imgs;
    } catch {
      return [];
    }
  };

  const images = chartResult ? extractImages() : [];

  return (
    <div className="df-page">
      <PageHeader
        eyebrow="STEP 05 · VISUALIZATION"
        title={<>数据<span className="df-lime-chip">可视化</span></>}
        description="基于当前数据集生成统计图表，选择图表类型与坐标字段后一键生成。"
        extra={<StepStatusPill step="visualization" />}
      />

      <div className="df-card df-card-lg df-viz-config">
        <div className="df-viz-fields">
          <div className="df-form-row">
            <span className="df-caption">图表类型</span>
            <Select
              style={{ width: 200 }}
              value={chartType}
              onChange={setChartType}
              options={charts.map((c) => ({ value: c, label: descriptions[c] || c }))}
            />
          </div>
          <div className="df-form-row">
            <span className="df-caption">X 轴字段</span>
            <Select allowClear style={{ width: 200 }} value={xCol} onChange={setXCol}
              options={columns.map((c) => ({ value: c, label: c }))} placeholder="自动选择" />
          </div>
          <div className="df-form-row">
            <span className="df-caption">Y 轴字段</span>
            <Select allowClear style={{ width: 200 }} value={yCol} onChange={setYCol}
              options={columns.map((c) => ({ value: c, label: c }))} placeholder="自动选择" />
          </div>
          <Button type="primary" icon={<BarChartOutlined />} loading={loading} onClick={handleGenerate}>
            生成图表
          </Button>
        </div>
      </div>

      <div className="df-card df-card-lg">
        <div className="df-eyebrow df-card-eyebrow">OUTPUT</div>
        <h3 className="df-card-title">图表输出</h3>
        {chartResult ? (
          images.length > 0 ? (
            <div className="df-viz-images">
              {images.map((src, i) => (
                <img key={i} src={`data:image/png;base64,${src}`} alt={`chart-${i}`} className="df-viz-img" />
              ))}
            </div>
          ) : (
            <pre className="df-code df-result-json">{chartResult.chart_data}</pre>
          )
        ) : (
          <div className="df-empty">
            <LineChartOutlined style={{ fontSize: 28 }} />
            <div>生成图表后，结果将显示在这里</div>
          </div>
        )}
        {chartResult && (
          <Button type="link" onClick={() => navigate('/report')}>
            下一步：数据报表 <RightOutlined />
          </Button>
        )}
      </div>
    </div>
  );
};

export default VisualizationModule;
