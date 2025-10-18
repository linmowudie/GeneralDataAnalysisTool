import React, { useState, useEffect, useContext } from 'react';
import './DataAnalysisModule.css';
import { dataAnalysisService } from '../../services/dataAnalysisService';
import { sessionService } from '../../services/sessionService';
import type { Message } from '../../components/MessagePanel';

// 添加消息的函数类型定义
type AddMessageType = (message: string, type?: 'info' | 'success' | 'warning' | 'error') => void;

// 创建 Context 用于传递 addMessage 函数
export const MessageContext = React.createContext<AddMessageType | null>(null);

interface DataAnalysisModuleProps {
  onAnalysisComplete: (result: any) => void;
}

/**
 * 数据分析模块
 * 提供模型选择和参数配置功能
 * 
 * @component
 * @example
 * ```tsx
 * <DataAnalysisModule onAnalysisComplete={handleAnalysisComplete} />
 * ```
 */
const DataAnalysisModule: React.FC<DataAnalysisModuleProps> = ({ onAnalysisComplete }) => {
  const [availableModels, setAvailableModels] = useState<string[]>([]);
  const [selectedModel, setSelectedModel] = useState<string>('');
  const [parameters, setParameters] = useState<Record<string, any>>({});
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [modelDescriptions, setModelDescriptions] = useState<Record<string, string>>({});
  const addMessage = useContext(MessageContext);

  /**
   * 初始化时获取可用模型
   */
  useEffect(() => {
    const fetchAvailableModels = async () => {
      try {
        addMessage && addMessage('正在获取模型列表...', 'info');
        const models = await dataAnalysisService.getAvailableModels();
        const descriptions = dataAnalysisService.getModelTypeDescriptions();
        setAvailableModels(models);
        setModelDescriptions(descriptions);
        if (models.length > 0) {
          setSelectedModel(models[0]);
          setParameters(dataAnalysisService.getDefaultParameters(models[0]));
        }
        addMessage && addMessage('模型列表获取成功', 'success');
      } catch (err) {
        const errorMessage = '获取模型列表失败: ' + (err instanceof Error ? err.message : '未知错误');
        setError(errorMessage);
        addMessage && addMessage(errorMessage, 'error');
        console.error('获取模型列表失败:', err);
      }
    };

    fetchAvailableModels();
  }, []);

  /**
   * 处理模型选择变化
   * @param model - 选中的模型
   */
  const handleModelChange = (model: string) => {
    setSelectedModel(model);
    setParameters(dataAnalysisService.getDefaultParameters(model));
    addMessage && addMessage(`已选择模型: ${model}`, 'info');
  };

  /**
   * 处理参数变化
   * @param key - 参数名
   * @param value - 参数值
   */
  const handleParameterChange = (key: string, value: any) => {
    setParameters(prev => ({
      ...prev,
      [key]: value
    }));
  };

  /**
   * 运行数据分析
   */
  const handleRunAnalysis = async () => {
    if (!selectedModel) {
      const errorMessage = '请选择一个模型';
      setError(errorMessage);
      addMessage && addMessage(errorMessage, 'warning');
      return;
    }

    const sessionId = sessionService.getCurrentSessionId();
    if (!sessionId) {
      const errorMessage = '未找到有效的会话ID，请先创建会话';
      setError(errorMessage);
      addMessage && addMessage(errorMessage, 'error');
      return;
    }

    try {
      setIsAnalyzing(true);
      setError(null);
      addMessage && addMessage('正在运行数据分析...', 'info');
      
      const result = await dataAnalysisService.runAnalysis(
        selectedModel,
        parameters,
        sessionId
      );
      
      onAnalysisComplete(result);
      addMessage && addMessage('数据分析完成', 'success');
    } catch (err) {
      const errorMessage = '数据分析失败: ' + (err instanceof Error ? err.message : '未知错误');
      setError(errorMessage);
      addMessage && addMessage(errorMessage, 'error');
      console.error('数据分析失败:', err);
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="data-analysis-module">
      <h3>数据分析</h3>
      {error && <div className="error-message">{error}</div>}
      
      {/* 模型选择 */}
      <div className="parameter-group">
        <label>选择模型:</label>
        <select 
          value={selectedModel} 
          onChange={(e) => handleModelChange(e.target.value)}
          disabled={isAnalyzing}
        >
          {availableModels.map(model => (
            <option key={model} value={model}>{model}</option>
          ))}
        </select>
        {selectedModel && modelDescriptions[selectedModel] && (
          <div className="model-description">
            {modelDescriptions[selectedModel]}
          </div>
        )}
      </div>
      
      {/* 随机种子参数 */}
      <div className="parameter-group">
        <label>随机种子:</label>
        <input 
          type="number" 
          value={parameters.random_state || 42}
          onChange={(e) => handleParameterChange('random_state', parseInt(e.target.value))}
          disabled={isAnalyzing}
        />
      </div>
      
      {/* 数据集分割选项 */}
      <div className="parameter-group">
        <label>
          <input 
            type="checkbox" 
            checked={parameters.is_split !== false}
            onChange={(e) => handleParameterChange('is_split', e.target.checked)}
            disabled={isAnalyzing}
          />
          是否分割数据集
        </label>
      </div>
      
      {/* 分割比例参数 */}
      {parameters.is_split !== false && (
        <div className="parameter-group">
          <label>分割比例:</label>
          <input 
            type="number" 
            min="0.1" 
            max="0.9" 
            step="0.1"
            value={parameters.split_ratio || 0.8}
            onChange={(e) => handleParameterChange('split_ratio', parseFloat(e.target.value))}
            disabled={isAnalyzing}
          />
        </div>
      )}
      
      {/* 特殊模型参数 */}
      {selectedModel === 'rf' && parameters.model_params && (
        <div className="parameter-group">
          <label>决策树数量 (n_estimators):</label>
          <input 
            type="number" 
            min="1" 
            value={parameters.model_params.n_estimators || 100}
            onChange={(e) => handleParameterChange('model_params', {
              ...parameters.model_params,
              n_estimators: parseInt(e.target.value)
            })}
            disabled={isAnalyzing}
          />
        </div>
      )}
      
      {selectedModel === 'xgb' && parameters.model_params && (
        <div className="parameter-group">
          <label>决策树数量 (n_estimators):</label>
          <input 
            type="number" 
            min="1" 
            value={parameters.model_params.n_estimators || 100}
            onChange={(e) => handleParameterChange('model_params', {
              ...parameters.model_params,
              n_estimators: parseInt(e.target.value)
            })}
            disabled={isAnalyzing}
          />
        </div>
      )}
      
      {selectedModel === 'xgb' && parameters.model_params && (
        <div className="parameter-group">
          <label>学习率 (learning_rate):</label>
          <input 
            type="number" 
            min="0.01" 
            max="1" 
            step="0.01"
            value={parameters.model_params.learning_rate || 0.1}
            onChange={(e) => handleParameterChange('model_params', {
              ...parameters.model_params,
              learning_rate: parseFloat(e.target.value)
            })}
            disabled={isAnalyzing}
          />
        </div>
      )}
      
      {/* 运行分析按钮 */}
      <button 
        className="run-analysis-btn"
        onClick={handleRunAnalysis}
        disabled={isAnalyzing}
      >
        {isAnalyzing ? '分析中...' : '运行分析'}
      </button>
    </div>
  );
};

export default DataAnalysisModule;