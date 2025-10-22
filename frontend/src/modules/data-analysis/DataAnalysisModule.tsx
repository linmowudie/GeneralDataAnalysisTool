import React, { useState, useEffect, useContext, useCallback, useRef } from 'react';
import './DataAnalysisModule.css';
import { dataAnalysisService } from '../../services/dataAnalysisService';
import type { ModelConfig } from '../../services/dataAnalysisService';
import { sessionService } from '../../services/sessionService';

// 全局缓存，存储已加载的模型数据，避免重复请求
const MODELS_GLOBAL_CACHE = {
  loaded: false,
  models: [] as string[],
  descriptions: {} as Record<string, string>,
  config: null as ModelConfig | null
};

// 添加消息的函数类型定义
type AddMessageType = (message: string, type?: 'info' | 'success' | 'warning' | 'error') => void;

// 创建 Context 用于传递 addMessage 函数
export const MessageContext = React.createContext<AddMessageType | null>(null);

interface DataAnalysisModuleProps {
  onAnalysisComplete: (result: any) => void;
}

/**
 * 数据分析模块
 * 提供模型选择、参数配置、特征列和目标列选择功能
 * 
 * @component
 * @example
 * ```tsx
 * <DataAnalysisModule onAnalysisComplete={handleAnalysisComplete} />
 * ```
 */
const DataAnalysisModule: React.FC<DataAnalysisModuleProps> = ({ onAnalysisComplete }) => {
  // 添加组件实例ID，用于标识不同的组件实例
  const componentId = useRef(Math.random().toString(36).substr(2, 9));
  
  // 调试组件渲染
  useEffect(() => {
    console.log(`[组件渲染] DataAnalysisModule (ID: ${componentId.current}) 渲染，全局缓存状态: ${MODELS_GLOBAL_CACHE.loaded}`);
  });
  
  const [availableModels, setAvailableModels] = useState<string[]>([]);
  const [selectedModel, setSelectedModel] = useState<string>('');
  const [parameters, setParameters] = useState<Record<string, any>>({
    feature_cols: [] as string[],
    target_col: '',
    random_state: 42,
    is_split: true,
    split_ratio: 0.8,
    is_return_model_score: true,
    model_params: {}
  });
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [modelDescriptions, setModelDescriptions] = useState<Record<string, string>>({});
  const [modelConfig, setModelConfig] = useState<ModelConfig | null>(null);
  const [dataColumns, setDataColumns] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const contextAddMessage = useContext(MessageContext);
  
  // 调试contextAddMessage变化
  useEffect(() => {
    console.log(`[Context变化] DataAnalysisModule (ID: ${componentId.current}) contextAddMessage 引用变化:`, contextAddMessage);
  }, [contextAddMessage]);
  
  // 使用useCallback稳定addMessage的引用
  const addMessage = useCallback((message: string, type?: 'info' | 'success' | 'warning' | 'error') => {
    contextAddMessage?.(message, type);
  }, [contextAddMessage]);
  
  /**
   * 初始化时获取可用模型、配置和数据列 - 使用全局缓存避免重复请求
   */
  useEffect(() => {
    console.log(`[Effect执行] DataAnalysisModule (ID: ${componentId.current}) useEffect执行`);
    
    const initializeData = async () => {
      setLoading(true);
      try {
        // 获取模型相关数据
        if (MODELS_GLOBAL_CACHE.loaded && MODELS_GLOBAL_CACHE.config) {
          console.log(`[使用全局缓存] DataAnalysisModule (ID: ${componentId.current}) 使用全局缓存的数据`);
          // 使用缓存数据
          setAvailableModels(MODELS_GLOBAL_CACHE.models);
          setModelDescriptions(MODELS_GLOBAL_CACHE.descriptions);
          setModelConfig(MODELS_GLOBAL_CACHE.config);
        } else {
          console.log(`[API调用开始] DataAnalysisModule (ID: ${componentId.current}) 开始获取模型相关数据`);
          addMessage && addMessage('正在获取模型列表和配置...', 'info');
          
          // 并行获取模型列表和配置
          const [models, descriptions, config] = await Promise.all([
            dataAnalysisService.getAvailableModels(),
            Promise.resolve(dataAnalysisService.getModelTypeDescriptions()),
            dataAnalysisService.getModelConfig()
          ]);
          
          // 更新全局缓存
          MODELS_GLOBAL_CACHE.loaded = true;
          MODELS_GLOBAL_CACHE.models = models;
          MODELS_GLOBAL_CACHE.descriptions = descriptions;
          MODELS_GLOBAL_CACHE.config = config;
          
          // 更新组件状态
          setAvailableModels(models);
          setModelDescriptions(descriptions);
          setModelConfig(config);
          
          console.log(`[API调用成功] DataAnalysisModule (ID: ${componentId.current}) 模型相关数据获取成功`);
        }
        
        // 获取数据列信息
        const sessionId = sessionService.getCurrentSessionId();
        if (sessionId) {
          console.log(`[API调用开始] DataAnalysisModule (ID: ${componentId.current}) 开始获取数据列信息`);
          const columns = await dataAnalysisService.getDataColumns(sessionId);
          setDataColumns(columns);
          console.log(`[API调用成功] DataAnalysisModule (ID: ${componentId.current}) 数据列信息获取成功:`, columns);
        }
      } catch (err) {
        const errorMessage = '初始化数据失败: ' + (err instanceof Error ? err.message : '未知错误');
        setError(errorMessage);
        console.error(`[初始化失败] DataAnalysisModule (ID: ${componentId.current}) 初始化失败:`, err);
        addMessage && addMessage(errorMessage, 'error');
      } finally {
        setLoading(false);
      }
    };

    initializeData();
  }, []); // 空依赖数组，只在组件首次挂载时执行一次

  /**
   * 处理模型选择变化
   * @param model - 选中的模型
   */
  const handleModelChange = (model: string) => {
    setSelectedModel(model);
    // 重置为默认参数
    const defaultParams = dataAnalysisService.getDefaultParameters(model);
    
    // 保留特征列和目标列的选择
    setParameters(prev => ({
      ...defaultParams,
      feature_cols: prev.feature_cols || [],
      target_col: prev.target_col || '',
      // 如果有模型配置，更新模型特定参数
      model_params: getModelSpecificParams(model)
    }));
    
    addMessage && addMessage(`已选择模型: ${model}`, 'info');
  };

  /**
   * 根据模型配置获取模型特定参数
   * @param modelName - 模型名称
   * @returns 模型特定参数
   */
  const getModelSpecificParams = (modelName: string): Record<string, any> => {
    if (!modelConfig) return {};
    
    // 遍历所有模型类型查找匹配的模型
    for (const modelType in modelConfig) {
      const models = modelConfig[modelType];
      if (models[modelName]) {
        return { ...models[modelName].default_params };
      }
    }
    
    return {};
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
   * 处理模型特定参数变化
   * @param paramName - 参数名
   * @param value - 参数值
   */
  const handleModelParamChange = (paramName: string, value: any) => {
    setParameters(prev => ({
      ...prev,
      model_params: {
        ...prev.model_params,
        [paramName]: value
      }
    }));
  };

  /**
   * 处理特征列选择变化
   * @param column - 列名
   * @param checked - 是否选中
   */
  const handleFeatureColumnChange = (column: string, checked: boolean) => {
    setParameters(prev => {
      const featureCols = [...prev.feature_cols];
      if (checked) {
        if (!featureCols.includes(column)) {
          featureCols.push(column);
        }
      } else {
        const index = featureCols.indexOf(column);
        if (index > -1) {
          featureCols.splice(index, 1);
        }
      }
      return {
        ...prev,
        feature_cols: featureCols
      };
    });
  };

  /**
   * 处理目标列选择变化
   * @param column - 列名
   */
  const handleTargetColumnChange = (column: string) => {
    setParameters(prev => ({
      ...prev,
      target_col: column
    }));
  };

  /**
   * 获取当前模型的可配置参数列表
   * @returns 参数列表
   */
  const getCurrentModelParams = (): string[] => {
    if (!selectedModel || !modelConfig) return [];
    
    for (const modelType in modelConfig) {
      const models = modelConfig[modelType];
      if (models[selectedModel] && models[selectedModel].init_params) {
        return models[selectedModel].init_params;
      }
    }
    
    return [];
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

    // 验证特征列和目标列
    if (parameters.feature_cols.length === 0) {
      const errorMessage = '请至少选择一个特征列';
      setError(errorMessage);
      addMessage && addMessage(errorMessage, 'warning');
      return;
    }

    if (!parameters.target_col) {
      const errorMessage = '请选择一个目标列';
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

  // 渲染参数输入组件
  const renderParameterInput = (paramName: string, defaultValue: any) => {
    // 根据参数名判断输入类型
    if (typeof defaultValue === 'boolean') {
      return (
        <input 
          type="checkbox" 
          checked={parameters.model_params[paramName] ?? defaultValue}
          onChange={(e) => handleModelParamChange(paramName, e.target.checked)}
          disabled={isAnalyzing}
        />
      );
    } else if (typeof defaultValue === 'number') {
      return (
        <input 
          type="number" 
          step="any"
          value={parameters.model_params[paramName] ?? defaultValue}
          onChange={(e) => handleModelParamChange(paramName, parseFloat(e.target.value))}
          disabled={isAnalyzing}
        />
      );
    } else if (paramName === 'kernel' && parameters.model_params[paramName] === undefined) {
      // 对SVM的kernel参数特殊处理
      return (
        <select
          value={parameters.model_params[paramName] ?? 'rbf'}
          onChange={(e) => handleModelParamChange(paramName, e.target.value)}
          disabled={isAnalyzing}
        >
          <option value="linear">linear</option>
          <option value="poly">poly</option>
          <option value="rbf">rbf</option>
          <option value="sigmoid">sigmoid</option>
        </select>
      );
    } else {
      return (
        <input 
          type="text" 
          value={parameters.model_params[paramName] ?? defaultValue}
          onChange={(e) => handleModelParamChange(paramName, e.target.value)}
          disabled={isAnalyzing}
        />
      );
    }
  };

  if (loading) {
    return <div className="loading">加载中...</div>;
  }

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
          <option value="">请选择模型</option>
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
      
      {selectedModel && (
        <>
          {/* 特征列选择 */}
          <div className="parameter-group">
            <label>特征列选择:</label>
            <div className="column-selector feature-columns">
              {dataColumns.length > 0 ? (
                dataColumns.map(column => (
                  <label key={column} className="checkbox-label">
                    <input 
                      type="checkbox" 
                      checked={parameters.feature_cols.includes(column)}
                      onChange={(e) => handleFeatureColumnChange(column, e.target.checked)}
                      disabled={isAnalyzing || column === parameters.target_col}
                    />
                    {column}
                  </label>
                ))
              ) : (
                <div className="no-data-message">未找到数据列，请先导入数据</div>
              )}
            </div>
          </div>
          
          {/* 目标列选择 */}
          <div className="parameter-group">
            <label>目标列选择:</label>
            <select 
              value={parameters.target_col}
              onChange={(e) => handleTargetColumnChange(e.target.value)}
              disabled={isAnalyzing}
            >
              <option value="">请选择目标列</option>
              {dataColumns.map(column => (
                <option key={column} value={column}>{column}</option>
              ))}
            </select>
          </div>
          
          {/* 通用参数配置 */}
          <div className="parameter-section">
            <h4>通用参数</h4>
            
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
            
            {/* 返回模型分数选项 */}
            <div className="parameter-group">
              <label>
                <input 
                  type="checkbox" 
                  checked={parameters.is_return_model_score !== false}
                  onChange={(e) => handleParameterChange('is_return_model_score', e.target.checked)}
                  disabled={isAnalyzing}
                />
                返回模型评分
              </label>
            </div>
          </div>
          
          {/* 动态模型参数配置 */}
          <div className="parameter-section">
            <h4>模型特定参数</h4>
            
            {getCurrentModelParams().length > 0 ? (
              getCurrentModelParams().map(paramName => {
                // 获取参数默认值
                let defaultValue = parameters.model_params[paramName] ?? '';
                
                // 尝试从模型配置中获取默认值
                if (modelConfig) {
                  for (const modelType in modelConfig) {
                    const models = modelConfig[modelType];
                    if (models[selectedModel] && models[selectedModel].default_params) {
                      defaultValue = models[selectedModel].default_params[paramName] ?? defaultValue;
                      break;
                    }
                  }
                }
                
                return (
                  <div key={paramName} className="parameter-group">
                    <label>{paramName}:</label>
                    {renderParameterInput(paramName, defaultValue)}
                  </div>
                );
              })
            ) : (
              <div className="no-params-message">当前模型没有可配置的特定参数</div>
            )}
          </div>
          
          {/* 运行分析按钮 */}
          <button 
            className="run-analysis-btn"
            onClick={handleRunAnalysis}
            disabled={isAnalyzing || !selectedModel || parameters.feature_cols.length === 0 || !parameters.target_col}
          >
            {isAnalyzing ? '分析中...' : '运行分析'}
          </button>
        </>
      )}
    </div>
  );
};

export default DataAnalysisModule;