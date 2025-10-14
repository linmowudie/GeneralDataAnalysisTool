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

const DataAnalysisModule: React.FC<DataAnalysisModuleProps> = ({ onAnalysisComplete }) => {
  const [availableModels, setAvailableModels] = useState<string[]>([]);
  const [selectedModel, setSelectedModel] = useState<string>('');
  const [parameters, setParameters] = useState<Record<string, any>>({});
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const addMessage = useContext(MessageContext);

  // 初始化时获取可用模型
  useEffect(() => {
    const fetchAvailableModels = async () => {
      try {
        addMessage && addMessage('正在获取模型列表...', 'info');
        const models = await dataAnalysisService.getAvailableModels();
        setAvailableModels(models);
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

  // 处理模型选择变化
  const handleModelChange = (model: string) => {
    setSelectedModel(model);
    setParameters(dataAnalysisService.getDefaultParameters(model));
    addMessage && addMessage(`已选择模型: ${model}`, 'info');
  };

  // 处理参数变化
  const handleParameterChange = (key: string, value: any) => {
    setParameters(prev => ({
      ...prev,
      [key]: value
    }));
  };

  // 运行数据分析
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
      </div>
      
      <div className="parameter-group">
        <label>随机种子:</label>
        <input 
          type="number" 
          value={parameters.random_state || 42}
          onChange={(e) => handleParameterChange('random_state', parseInt(e.target.value))}
          disabled={isAnalyzing}
        />
      </div>
      
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