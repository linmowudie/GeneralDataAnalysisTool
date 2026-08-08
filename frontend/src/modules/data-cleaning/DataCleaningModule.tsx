import React, { useEffect, useState } from 'react';
import { Button, Select, Switch, Input, message } from 'antd';
import { ThunderboltOutlined, RightOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { PageHeader, StepStatusPill } from '../../components/common/Common';
import { useSession } from '../../context/SessionContext';
import { dataCleaningService } from '../../services/dataCleaningService';
import { dataAnalysisService } from '../../services/dataAnalysisService';
import './DataCleaningModule.css';

const DataCleaningModule: React.FC = () => {
  const navigate = useNavigate();
  const { refreshStatus, ready, sessionId } = useSession();
  const [modes, setModes] = useState<string[]>([]);
  const [mode, setMode] = useState('standard');
  const [isCustom, setIsCustom] = useState(false);
  const [targetCol, setTargetCol] = useState<string | undefined>();
  const [paramsText, setParamsText] = useState('{}');
  const [columns, setColumns] = useState<string[]>([]);
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState<any>(null);
  const descriptions = dataCleaningService.getCleaningModeDescriptions();

  useEffect(() => {
    dataCleaningService.getCleaningModes().then(setModes);
    if (ready && sessionId) {
      dataAnalysisService.getDataColumns(sessionId).then(setColumns);
    }
  }, [ready, sessionId]);

  const handleClean = async () => {
    let parameters: Record<string, any> = {};
    if (isCustom) {
      try {
        parameters = JSON.parse(paramsText || '{}');
      } catch {
        message.error('自定义参数必须是合法 JSON');
        return;
      }
    }
    setRunning(true);
    setResult(null);
    try {
      const res = await dataCleaningService.cleanData(mode, isCustom, parameters, targetCol);
      setResult(res);
      message.success('数据清洗完成');
      await refreshStatus();
    } catch (e: any) {
      message.error(`清洗失败：${e?.message || e}`);
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="df-page">
      <PageHeader
        eyebrow="STEP 03 · CLEANING"
        title={<>数据<span className="df-lime-chip">清洗</span></>}
        description="选择清洗模式处理缺失值、异常值与重复数据，清洗结果将覆盖后续分析使用的数据集。"
        extra={<StepStatusPill step="cleaning" />}
      />

      <div className="df-grid-2">
        <div className="df-card df-card-lg">
          <div className="df-eyebrow df-card-eyebrow">MODE</div>
          <h3 className="df-card-title">清洗模式</h3>
          <div className="df-mode-list">
            {(modes.length ? modes : ['standard', 'strict', 'relaxed', 'custom']).map((m) => (
              <div
                key={m}
                className={`df-mode-item ${mode === m ? 'df-mode-active' : ''}`}
                onClick={() => {
                  setMode(m);
                  setIsCustom(m === 'custom');
                }}
              >
                <div className="df-mode-name df-code">{m}</div>
                <div className="df-caption">{descriptions[m] || '自定义清洗模式'}</div>
              </div>
            ))}
          </div>

          <div className="df-clean-option">
            <span className="df-caption">指定目标列（可选）</span>
            <Select
              allowClear
              style={{ width: 220 }}
              placeholder="全部列"
              value={targetCol}
              onChange={setTargetCol}
              options={columns.map((c) => ({ value: c, label: c }))}
            />
          </div>

          <div className="df-clean-option">
            <span className="df-caption">自定义清洗</span>
            <Switch checked={isCustom} onChange={setIsCustom} />
          </div>

          {isCustom && (
            <Input.TextArea
              rows={4}
              className="df-code"
              value={paramsText}
              onChange={(e) => setParamsText(e.target.value)}
              placeholder='{"fill_missing": "mean", "remove_duplicates": true}'
            />
          )}

          <Button type="primary" icon={<ThunderboltOutlined />} loading={running} onClick={handleClean} block>
            执行清洗
          </Button>
        </div>

        <div className="df-card df-card-lg">
          <div className="df-eyebrow df-card-eyebrow">RESULT</div>
          <h3 className="df-card-title">清洗结果</h3>
          {result ? (
            <>
              <div className="df-pill df-pill-done" style={{ marginBottom: 12 }}>{result.message || '清洗完成'}</div>
              <pre className="df-code df-result-json">{JSON.stringify(result, null, 2)}</pre>
              <Button type="link" onClick={() => navigate('/analysis')}>
                下一步：数据分析 <RightOutlined />
              </Button>
            </>
          ) : (
            <div className="df-empty">
              <ThunderboltOutlined style={{ fontSize: 28 }} />
              <div>执行清洗后，结果将显示在这里</div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DataCleaningModule;
