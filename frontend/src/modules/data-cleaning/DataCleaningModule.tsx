import React, { useState, useEffect, useContext } from 'react';
import './DataCleaningModule.css';
import { dataCleaningService } from '../../services/dataCleaningService';
import { sessionService } from '../../services/sessionService';

// 添加消息的函数类型定义
type AddMessageType = (message: string, type?: 'info' | 'success' | 'warning' | 'error') => void;

// 创建 Context 用于传递 addMessage 函数
export const MessageContext = React.createContext<AddMessageType | null>(null);

/**
 * 数据清洗模块
 * 提供多种数据清洗模式和参数配置
 * 
 * @component
 * @example
 * ```tsx
 * <DataCleaningModule />
 * ```
 */
const DataCleaningModule: React.FC = () => {
  const addMessage = useContext(MessageContext);
  
  // 清洗模式状态
  const [cleanMode, setCleanMode] = useState<'standard' | 'strict' | 'relaxed' | 'custom'>('standard');
  
  // 自定义参数状态
  const [customParams, setCustomParams] = useState({
    columns: '',
    dropDuplicates: true,
    handleMissing: 'auto',
    fillMethod: 'mean',
    outlierMethod: 'iqr',
    validateSchema: false
  });
  
  // 清洗状态
  const [isCleaning, setIsCleaning] = useState(false);
  const [cleanResult, setCleanResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  /**
   * 处理清洗模式变更
   * @param mode - 新的清洗模式
   */
  const handleModeChange = (mode: 'standard' | 'strict' | 'relaxed' | 'custom') => {
    setCleanMode(mode);
  };

  /**
   * 处理自定义参数变更
   * @param param - 参数名
   * @param value - 参数值
   */
  const handleParamChange = (param: string, value: any) => {
    setCustomParams(prev => ({
      ...prev,
      [param]: value
    }));
  };

  /**
   * 执行数据清洗
   */
  const handleCleanData = async () => {
    try {
      setIsCleaning(true);
      setError(null);
      
      // 获取当前会话ID
      const sessionId = sessionService.getCurrentSessionId();
      if (!sessionId) {
        throw new Error('未找到有效的会话ID');
      }

      // 准备参数
      let params: any = {};
      if (cleanMode === 'custom') {
        // 处理自定义参数
        params = {
          ...customParams,
          columns: customParams.columns ? customParams.columns.split(',').map(col => col.trim()) : null
        };
      }

      // 调用数据清洗服务
      const result = await dataCleaningService.cleanData(
        cleanMode,
        cleanMode === 'custom',
        params
      );

      setCleanResult(result);
      addMessage && addMessage('数据清洗完成', 'success');
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '数据清洗失败';
      setError(errorMessage);
      addMessage && addMessage(errorMessage, 'error');
      console.error('数据清洗失败:', err);
    } finally {
      setIsCleaning(false);
    }
  };

  return (
    <div className="data-cleaning-module">
      <h3>数据清洗</h3>
      
      {/* 清洗模式选择 */}
      <div className="clean-mode-selector">
        <h4>清洗模式</h4>
        <div className="mode-options">
          <button 
            className={`mode-btn ${cleanMode === 'standard' ? 'active' : ''}`}
            onClick={() => handleModeChange('standard')}
          >
            标准模式
          </button>
          <button 
            className={`mode-btn ${cleanMode === 'strict' ? 'active' : ''}`}
            onClick={() => handleModeChange('strict')}
          >
            严格模式
          </button>
          <button 
            className={`mode-btn ${cleanMode === 'relaxed' ? 'active' : ''}`}
            onClick={() => handleModeChange('relaxed')}
          >
            宽松模式
          </button>
          <button 
            className={`mode-btn ${cleanMode === 'custom' ? 'active' : ''}`}
            onClick={() => handleModeChange('custom')}
          >
            自定义模式
          </button>
        </div>
      </div>

      {/* 参数配置区域 */}
      {cleanMode === 'custom' && (
        <div className="custom-params">
          <h4>自定义参数</h4>
          <div className="params-form">
            <div className="form-group">
              <label>保留列名（逗号分隔）:</label>
              <input
                type="text"
                value={customParams.columns}
                onChange={(e) => handleParamChange('columns', e.target.value)}
                placeholder="例如: col1,col2,col3"
              />
            </div>
            
            <div className="form-group checkbox-group">
              <label>
                <input
                  type="checkbox"
                  checked={customParams.dropDuplicates}
                  onChange={(e) => handleParamChange('dropDuplicates', e.target.checked)}
                />
                删除重复行
              </label>
            </div>
            
            <div className="form-group">
              <label>缺失值处理:</label>
              <select
                value={customParams.handleMissing}
                onChange={(e) => handleParamChange('handleMissing', e.target.value)}
              >
                <option value="auto">自动处理</option>
                <option value="drop">删除</option>
                <option value="fill">填充</option>
              </select>
            </div>
            
            {customParams.handleMissing === 'fill' && (
              <div className="form-group">
                <label>填充方法:</label>
                <select
                  value={customParams.fillMethod}
                  onChange={(e) => handleParamChange('fillMethod', e.target.value)}
                >
                  <option value="mean">均值</option>
                  <option value="median">中位数</option>
                  <option value="mode">众数</option>
                  <option value="ffill">前向填充</option>
                  <option value="bfill">后向填充</option>
                </select>
              </div>
            )}
            
            <div className="form-group">
              <label>异常值处理:</label>
              <select
                value={customParams.outlierMethod}
                onChange={(e) => handleParamChange('outlierMethod', e.target.value)}
              >
                <option value="iqr">IQR方法</option>
                <option value="zscore">Z-Score方法</option>
                <option value="none">不处理</option>
              </select>
            </div>
            
            <div className="form-group checkbox-group">
              <label>
                <input
                  type="checkbox"
                  checked={customParams.validateSchema}
                  onChange={(e) => handleParamChange('validateSchema', e.target.checked)}
                />
                启用Schema验证
              </label>
            </div>
          </div>
        </div>
      )}

      {/* 操作按钮 */}
      <div className="action-buttons">
        <button 
          className="clean-btn primary"
          onClick={handleCleanData}
          disabled={isCleaning}
        >
          {isCleaning ? '清洗中...' : '开始清洗'}
        </button>
      </div>

      {/* 错误信息 */}
      {error && (
        <div className="error-message">
          错误: {error}
        </div>
      )}

      {/* 清洗结果 */}
      {cleanResult && (
        <div className="clean-result">
          <h4>清洗结果</h4>
          <div className="result-info">
            <p>清洗前数据行数: {cleanResult.before_rows}</p>
            <p>清洗后数据行数: {cleanResult.after_rows}</p>
            <p>删除行数: {cleanResult.deleted_rows}</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default DataCleaningModule;