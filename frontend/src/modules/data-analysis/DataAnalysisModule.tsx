import React, { useEffect, useState, useCallback } from 'react';
import { Button, Select, Input, InputNumber, Switch, message } from 'antd';
import { PlayCircleOutlined, RightOutlined, ExperimentOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { PageHeader, StepStatusPill } from '../../components/common/Common';
import { useSession } from '../../context/SessionContext';
import { dataAnalysisService, type ModelInfo } from '../../services/dataAnalysisService';
import './DataAnalysisModule.css';

/** 根据默认值推断参数类型 */
function inferParamType(value: unknown): 'boolean' | 'number' | 'text' {
  if (typeof value === 'boolean') return 'boolean';
  if (typeof value === 'number') return 'number';
  return 'text';
}

const DataAnalysisModule: React.FC = () => {
  const navigate = useNavigate();
  const { refreshStatus, ready, sessionId } = useSession();

  const [models, setModels] = useState<string[]>([]);
  const [modelType, setModelType] = useState<string | undefined>();
  const [modelMeta, setModelMeta] = useState<ModelInfo | null>(null);
  const [columns, setColumns] = useState<string[]>([]);
  const [targetCol, setTargetCol] = useState<string | undefined>();
  const [splitRatio, setSplitRatio] = useState(0.8);
  const [paramValues, setParamValues] = useState<Record<string, unknown>>({});
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState<any>(null);
  const descriptions = dataAnalysisService.getModelTypeDescriptions();

  // 初始化：获取模型列表 + 模型配置
  useEffect(() => {
    (async () => {
      try {
        const [list, config] = await Promise.all([
          dataAnalysisService.getAvailableModels(),
          dataAnalysisService.getModelConfig(),
        ]);
        setModels(list);
        if (list.length) setModelType(list[0]);
        // 缓存配置供后续 getModelMeta 使用
        void config;
      } catch {
        message.error('获取模型信息失败');
      }
    })();
    if (ready && sessionId) {
      dataAnalysisService.getDataColumns(sessionId).then(setColumns);
    }
  }, [ready, sessionId]);

  // 模型切换时加载元信息并填充默认参数值
  useEffect(() => {
    if (!modelType) return;
    dataAnalysisService.getModelMeta(modelType).then((meta) => {
      setModelMeta(meta);
      if (meta) {
        const defaults: Record<string, unknown> = {};
        for (const key of meta.init_params) {
          defaults[key] = meta.default_params[key] ?? null;
        }
        setParamValues(defaults);
      } else {
        setParamValues({});
      }
    });
  }, [modelType]);

  const updateParam = useCallback((key: string, value: unknown) => {
    setParamValues((prev) => ({ ...prev, [key]: value }));
  }, []);

  const handleRun = async () => {
    if (!modelType) {
      message.warning('请先选择模型');
      return;
    }
    const parameters: Record<string, unknown> = {
      model_type: modelType,
      split_ratio: splitRatio,
      model_params: { ...paramValues },
    };
    if (targetCol) parameters.target_col = targetCol;

    setRunning(true);
    setResult(null);
    try {
      const res = await dataAnalysisService.runAnalysis(modelType, parameters as Record<string, any>);
      setResult(res);
      message.success('分析完成');
      await refreshStatus();
    } catch (e: any) {
      message.error(`分析失败：${e?.message || e}`);
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="df-page">
      <PageHeader
        eyebrow="STEP 04 · ANALYSIS"
        title={<>数据<span className="df-lime-chip">分析</span></>}
        description="选择模型类型与超参数执行训练评估，也可前往 Agent 页一键自动寻优。"
        extra={
          <>
            <StepStatusPill step="analysis" />
            <Button onClick={() => navigate('/agent')}>Agent 自动分析</Button>
          </>
        }
      />

      <div className="df-grid-2">
        <div className="df-card df-card-lg">
          <div className="df-eyebrow df-card-eyebrow">CONFIG</div>
          <h3 className="df-card-title">分析配置</h3>

          <div className="df-form-row">
            <span className="df-caption">模型类型</span>
            <Select
              style={{ width: 240 }}
              value={modelType}
              onChange={setModelType}
              options={models.map((m) => ({ value: m, label: `${m}` }))}
              placeholder="选择模型"
            />
          </div>
          {modelType && descriptions[modelType] && (
            <div className="df-caption df-model-desc">{descriptions[modelType]}</div>
          )}

          <div className="df-form-row">
            <span className="df-caption">目标列（可选）</span>
            <Select
              allowClear
              style={{ width: 240 }}
              value={targetCol}
              onChange={setTargetCol}
              options={columns.map((c) => ({ value: c, label: c }))}
              placeholder="自动推断"
            />
          </div>

          <div className="df-form-row">
            <span className="df-caption">训练集比例</span>
            <InputNumber min={0.5} max={0.95} step={0.05} value={splitRatio} onChange={(v) => setSplitRatio(v || 0.8)} />
          </div>

          {/* 动态模型参数字段 */}
          {modelMeta && modelMeta.init_params.length > 0 && (
            <>
              <div className="df-section-divider" />
              <div className="df-eyebrow" style={{ marginBottom: 8 }}>MODEL PARAMS</div>
              {modelMeta.init_params.map((key) => {
                const val = paramValues[key];
                const pType = inferParamType(modelMeta.default_params[key]);
                return (
                  <div className="df-form-row" key={key}>
                    <span className="df-caption">{key}</span>
                    {pType === 'boolean' ? (
                      <Switch checked={!!val} onChange={(v) => updateParam(key, v)} />
                    ) : pType === 'number' ? (
                      <InputNumber
                        style={{ width: 160 }}
                        value={val as number}
                        onChange={(v) => updateParam(key, v)}
                        placeholder="默认值"
                      />
                    ) : (
                      <Input
                        style={{ width: 160 }}
                        value={val === null ? '' : String(val ?? '')}
                        onChange={(e) => updateParam(key, e.target.value)}
                        placeholder="默认值"
                      />
                    )}
                  </div>
                );
              })}
            </>
          )}

          <Button type="primary" icon={<PlayCircleOutlined />} loading={running} onClick={handleRun} block style={{ marginTop: 16 }}>
            运行分析
          </Button>
        </div>

        <div className="df-card df-card-lg">
          <div className="df-eyebrow df-card-eyebrow">RESULT</div>
          <h3 className="df-card-title">分析结果</h3>
          {result ? (
            <>
              <div className="df-pill df-pill-done" style={{ marginBottom: 12 }}>
                {result.message || '分析完成'} · {result.model_type}
              </div>
              <pre className="df-code df-result-json">{JSON.stringify(result.result ?? result, null, 2)}</pre>
              <Button type="link" onClick={() => navigate('/visualization')}>
                下一步：可视化 <RightOutlined />
              </Button>
            </>
          ) : (
            <div className="df-empty">
              <ExperimentOutlined style={{ fontSize: 28 }} />
              <div>运行分析后，指标与结果将显示在这里</div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DataAnalysisModule;
