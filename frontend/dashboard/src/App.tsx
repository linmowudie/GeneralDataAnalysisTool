import { useState } from 'react'
import './App.css'
import { useSession } from './hooks/useSession'
import { useDataPreview } from './hooks/useDataPreview'
import { useDataAnalysis } from './hooks/useDataAnalysis'
import type { AnalysisParameters, CleaningParameters, DatabaseImportParameters } from './types'
import frontendLogger from './utils/logger'

// 简单的日志记录函数
const logFrontendAction = (action: string, details?: any) => {
  const timestamp = new Date().toISOString();
  console.log(`[Frontend App ${timestamp}] ${action}`, details || '');
};

function App() {
  const [activeTab, setActiveTab] = useState('dashboard')
  const [importType, setImportType] = useState('file')
  const [resultMessage, setResultMessage] = useState('')
  const [selectedModel, setSelectedModel] = useState('')
  const [showAdvancedOptions, setShowAdvancedOptions] = useState(false)
  const [analysisParams, setAnalysisParams] = useState<AnalysisParameters>({
    random_state: 42,
    is_split: true,
    split_ratio: 0.8,
    feature_cols: undefined,
    target_col: undefined,
    is_return_model_param: false,
    metrics_list: undefined,
    is_return_model_score: true,
    is_return_training_set: false,
    is_return_model_predicting_set: false,
    feature_cols_encoding: 'onehot',
    target_col_encoding: 'label',
    test_set: undefined,
    model_params: undefined
  })
  const [cleaningMode, setCleaningMode] = useState('standard')
  const [customCleaningParams, setCustomCleaningParams] = useState('')
  const [file, setFile] = useState<File | null>(null)
  const [dbParams, setDbParams] = useState({
    dbType: '',
    host: 'localhost',
    port: 3306,
    database: '',
    table: '',
    username: '',
    password: ''
  })

  const { sessionId, loading: sessionLoading, error: sessionError } = useSession()
  const { dataPreview, datasetInfo, loading: previewLoading, error: previewError, refetch: fetchDataPreview } = useDataPreview(sessionId)
  const { loading: analysisLoading, error: analysisError, runAnalysis, cleanData, generateChart, importFromDatabase } = useDataAnalysis()

  // 模拟执行操作并显示结果
  const handleAction = (action: string) => {
    frontendLogger.info(`执行操作: ${action}`);
    setResultMessage(`执行了${action}操作，结果将在此处显示...`)
    
    // 3秒后清除消息
    setTimeout(() => {
      setResultMessage('')
    }, 3000)
  }

  // 处理文件上传
  const handleFileUpload = async () => {
    if (!sessionId) {
      frontendLogger.warn('会话未创建，无法上传文件');
      setResultMessage('会话未创建')
      return
    }

    if (!file) {
      frontendLogger.warn('未选择文件');
      setResultMessage('请选择要上传的文件')
      return
    }

    try {
      frontendLogger.info('开始上传文件', { fileName: file.name });
      // 调用实际的上传API
      const formData = new FormData()
      formData.append('session_id', sessionId)
      formData.append('file', file)

      const response = await fetch('http://localhost:8000/api/import/upload-file', {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        const errorText = await response.text();
        frontendLogger.error('文件上传失败', { status: response.status, error: errorText });
        throw new Error(`上传失败: ${response.status} ${response.statusText}`)
      }

      const result = await response.json()
      frontendLogger.info('文件上传成功', { fileName: file.name });
      setResultMessage(result.message || '文件上传成功')
      
      // 上传成功后自动获取预览
      setTimeout(fetchDataPreview, 1000)
    } catch (error) {
      frontendLogger.error('文件上传异常', { error: (error as Error).message });
      setResultMessage('文件上传失败: ' + (error as Error).message)
    }
  }

  // 处理模型选择变化
  const handleModelChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedModel(e.target.value)
  }

  // 处理清洗模式变化
  const handleCleaningModeChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setCleaningMode(e.target.value)
  }

  // 处理参数变化
  const handleParamChange = (param: string, value: string | number | boolean) => {
    setAnalysisParams(prev => ({
      ...prev,
      [param]: value
    }))
  }

  // 处理文件选择
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0])
    }
  }

  // 处理数据库参数变化
  const handleDbParamChange = (param: string, value: string | number) => {
    setDbParams(prev => ({
      ...prev,
      [param]: value
    }))
  }

  // 处理数据库导入
  const handleDatabaseImport = async () => {
    if (!sessionId) {
      setResultMessage('会话未创建')
      return
    }

    try {
      await importFromDatabase(sessionId, {
        db_type: dbParams.dbType,
        host: dbParams.host,
        port: dbParams.port,
        database: dbParams.database,
        table: dbParams.table,
        username: dbParams.username,
        password: dbParams.password
      })
      setResultMessage('数据库导入成功')
      fetchDataPreview()
    } catch (error) {
      setResultMessage('数据库导入失败: ' + (error as Error).message)
    }
  }

  // 处理数据分析
  const handleRunAnalysis = async () => {
    if (!sessionId) {
      setResultMessage('会话未创建')
      return
    }

    if (!selectedModel) {
      setResultMessage('请选择分析模型')
      return
    }

    try {
      // 解析特征列
      let featureCols: string[] | undefined
      if (analysisParams.feature_cols && Array.isArray(analysisParams.feature_cols)) {
        featureCols = analysisParams.feature_cols
      }

      // 解析评估指标
      let metricsList: string[] | undefined
      if (analysisParams.metrics_list && Array.isArray(analysisParams.metrics_list)) {
        metricsList = analysisParams.metrics_list
      }

      const params: AnalysisParameters = {
        ...analysisParams,
        feature_cols: featureCols,
        metrics_list: metricsList
      }

      await runAnalysis(sessionId, selectedModel, params)
      setResultMessage('数据分析执行成功')
    } catch (error) {
      setResultMessage('数据分析失败: ' + (error as Error).message)
    }
  }

  // 处理数据清洗
  const handleCleanData = async () => {
    if (!sessionId) {
      setResultMessage('会话未创建')
      return
    }

    try {
      let cleaningParams: CleaningParameters = {}
      if (cleaningMode === 'custom' && customCleaningParams) {
        try {
          cleaningParams = JSON.parse(customCleaningParams)
        } catch (e) {
          setResultMessage('自定义参数格式错误，请输入有效的JSON')
          return
        }
      }

      await cleanData(
        sessionId,
        cleaningMode,
        cleaningMode === 'custom',
        cleaningParams,
        analysisParams.target_col
      )
      setResultMessage('数据清洗执行成功')
      fetchDataPreview()
    } catch (error) {
      setResultMessage('数据清洗失败: ' + (error as Error).message)
    }
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>通用数据分析工具</h1>
        <nav>
          <button 
            className={activeTab === 'dashboard' ? 'active' : ''}
            onClick={() => setActiveTab('dashboard')}
          >
            仪表板
          </button>
          <button 
            className={activeTab === 'import' ? 'active' : ''}
            onClick={() => setActiveTab('import')}
          >
            数据导入
          </button>
          <button 
            className={activeTab === 'preview' ? 'active' : ''}
            onClick={() => {
              setActiveTab('preview')
              fetchDataPreview()
            }}
          >
            数据预览
          </button>
          <button 
            className={activeTab === 'cleaning' ? 'active' : ''}
            onClick={() => setActiveTab('cleaning')}
          >
            数据清洗
          </button>
          <button 
            className={activeTab === 'analysis' ? 'active' : ''}
            onClick={() => setActiveTab('analysis')}
          >
            数据分析
          </button>
          <button 
            className={activeTab === 'visualization' ? 'active' : ''}
            onClick={() => setActiveTab('visualization')}
          >
            数据可视化
          </button>
          <button 
            className={activeTab === 'report' ? 'active' : ''}
            onClick={() => setActiveTab('report')}
          >
            报表生成
          </button>
        </nav>
      </header>

      <main className="app-main">
        {activeTab === 'dashboard' && (
          <div className="dashboard">
            <h2>仪表板</h2>
            <div className="dashboard-grid">
              <div className="card">
                <h3>数据概览</h3>
                {datasetInfo ? (
                  <>
                    <p>数据集名称: {datasetInfo.dataset_name}</p>
                    <p>总记录数: {datasetInfo.total_records}</p>
                    <p>特征数量: {datasetInfo.features_count}</p>
                    <p>目标变量: {datasetInfo.target_variable}</p>
                  </>
                ) : (
                  <p>暂无数据</p>
                )}
              </div>
              <div className="card">
                <h3>最近分析</h3>
                <p>暂无分析记录</p>
              </div>
              <div className="card">
                <h3>可视化图表</h3>
                <p>暂无图表</p>
              </div>
              <div className="card">
                <h3>系统状态</h3>
                <p>{sessionId ? '会话已创建' : '会话未创建'}</p>
                {sessionError && <p style={{color: 'red'}}>错误: {sessionError}</p>}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'import' && (
          <div className="data-import">
            <h2>数据导入</h2>
            <div className="import-options">
              <button 
                className={importType === 'file' ? 'active' : ''}
                onClick={() => setImportType('file')}
              >
                从文件导入
              </button>
              <button 
                className={importType === 'database' ? 'active' : ''}
                onClick={() => setImportType('database')}
              >
                从数据库导入
              </button>
              <button 
                className={importType === 'api' ? 'active' : ''}
                onClick={() => setImportType('api')}
              >
                从API导入
              </button>
            </div>

            {importType === 'file' && (
              <div className="file-upload">
                <p>拖拽文件到此处或点击选择文件</p>
                <input type="file" onChange={handleFileChange} />
                <button onClick={handleFileUpload}>导入文件</button>
              </div>
            )}

            {importType === 'database' && (
              <div className="database-import">
                <div className="form-group">
                  <label>数据库类型:</label>
                  <select value={dbParams.dbType} onChange={(e) => handleDbParamChange('dbType', e.target.value)}>
                    <option value="">请选择数据库类型</option>
                    <option value="mysql">MySQL</option>
                    <option value="postgresql">PostgreSQL</option>
                    <option value="mongodb">MongoDB</option>
                    <option value="sqlite">SQLite</option>
                    <option value="redis">Redis</option>
                  </select>
                </div>
                <div className="form-group">
                  <label>主机地址:</label>
                  <input 
                    type="text" 
                    placeholder="localhost" 
                    value={dbParams.host}
                    onChange={(e) => handleDbParamChange('host', e.target.value)}
                  />
                </div>
                <div className="form-group">
                  <label>端口:</label>
                  <input 
                    type="number" 
                    placeholder="3306" 
                    value={dbParams.port}
                    onChange={(e) => handleDbParamChange('port', parseInt(e.target.value) || 0)}
                  />
                </div>
                <div className="form-group">
                  <label>数据库名:</label>
                  <input 
                    type="text" 
                    placeholder="database_name" 
                    value={dbParams.database}
                    onChange={(e) => handleDbParamChange('database', e.target.value)}
                  />
                </div>
                <div className="form-group">
                  <label>表名或集合名:</label>
                  <input 
                    type="text" 
                    placeholder="table_name" 
                    value={dbParams.table}
                    onChange={(e) => handleDbParamChange('table', e.target.value)}
                  />
                </div>
                <div className="form-group">
                  <label>用户名:</label>
                  <input 
                    type="text" 
                    placeholder="username" 
                    value={dbParams.username}
                    onChange={(e) => handleDbParamChange('username', e.target.value)}
                  />
                </div>
                <div className="form-group">
                  <label>密码:</label>
                  <input 
                    type="password" 
                    placeholder="password" 
                    value={dbParams.password}
                    onChange={(e) => handleDbParamChange('password', e.target.value)}
                  />
                </div>
                <button onClick={handleDatabaseImport} disabled={analysisLoading}>
                  {analysisLoading ? '导入中...' : '连接并导入'}
                </button>
              </div>
            )}

            {importType === 'api' && (
              <div className="api-import">
                <div className="form-group">
                  <label>API地址:</label>
                  <input type="text" placeholder="https://api.example.com/data" />
                </div>
                <div className="form-group">
                  <label>请求方法:</label>
                  <select>
                    <option value="GET">GET</option>
                    <option value="POST">POST</option>
                  </select>
                </div>
                <div className="form-group">
                  <label>请求头 (可选):</label>
                  <textarea placeholder='{"Authorization": "Bearer token"}' />
                </div>
                <div className="form-group">
                  <label>请求体 (POST):</label>
                  <textarea placeholder='{"key": "value"}' />
                </div>
                <button onClick={() => handleAction('API获取并导入')}>获取并导入</button>
              </div>
            )}
          </div>
        )}

        {activeTab === 'preview' && (
          <div className="data-preview">
            <h2>数据预览</h2>
            <div className="preview-controls">
              <button onClick={fetchDataPreview} disabled={previewLoading}>
                {previewLoading ? '加载中...' : '刷新数据'}
              </button>
            </div>
            
            {previewError && <p style={{color: 'red'}}>错误: {previewError}</p>}
            
            {dataPreview && dataPreview.success ? (
              <div className="preview-content">
                <div className="preview-info">
                  <p><strong>文件名:</strong> {dataPreview.file_name}</p>
                  <p><strong>总行数:</strong> {dataPreview.total_rows}</p>
                  <p><strong>总列数:</strong> {dataPreview.total_columns}</p>
                </div>
                
                <div className="preview-table-container">
                  <table className="preview-table">
                    <thead>
                      <tr>
                        {dataPreview.columns.map((col: string, index: number) => (
                          <th key={index}>{col}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {dataPreview.preview_data.map((row: any, rowIndex: number) => (
                        <tr key={rowIndex}>
                          {dataPreview.columns.map((col: string, colIndex: number) => (
                            <td key={colIndex}>{row[col]}</td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            ) : (
              <div className="preview-error">
                <p>{dataPreview?.message || '暂无数据可预览'}</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'cleaning' && (
          <div className="data-cleaning">
            <h2>数据清洗</h2>
            <div className="cleaning-options">
              <div className="form-group">
                <label>清洗模式:</label>
                <select value={cleaningMode} onChange={handleCleaningModeChange}>
                  <option value="standard">标准模式</option>
                  <option value="strict">严格模式</option>
                  <option value="relaxed">宽松模式</option>
                  <option value="custom">自定义模式</option>
                </select>
              </div>
              
              {cleaningMode === 'custom' && (
                <div className="form-group">
                  <label>自定义参数:</label>
                  <textarea 
                    placeholder='{"custom_params": ["handle_missing=drop", "outlier_method=iqr", "outlier_threshold=1.5"]}'
                    value={customCleaningParams}
                    onChange={(e) => setCustomCleaningParams(e.target.value)}
                  />
                </div>
              )}
              
              <button onClick={handleCleanData} disabled={analysisLoading}>
                {analysisLoading ? '清洗中...' : '开始清洗'}
              </button>
            </div>
            
            <div className="cleaning-info">
              <h3>清洗模式说明</h3>
              <ul>
                <li><strong>标准模式:</strong> 去重 + 智能填充缺失值（数值用中位数，类别用众数）</li>
                <li><strong>严格模式:</strong> 删除所有缺失值和重复行</li>
                <li><strong>宽松模式:</strong> 仅去重，保留缺失值</li>
                <li><strong>自定义模式:</strong> 根据自定义参数进行清洗</li>
              </ul>
            </div>
          </div>
        )}

        {activeTab === 'analysis' && (
          <div className="data-analysis">
            <h2>数据分析</h2>
            <div className="analysis-options">
              <select value={selectedModel} onChange={handleModelChange}>
                <option value="">选择分析模型</option>
                <optgroup label="回归分析">
                  <option value="linearregression">线性回归</option>
                  <option value="ridge">岭回归</option>
                  <option value="lasso">Lasso回归</option>
                </optgroup>
                <optgroup label="分类分析">
                  <option value="logisticregression">逻辑回归</option>
                  <option value="decisiontreeclassifier">决策树分类</option>
                  <option value="kneighborsclassifier">K近邻分类</option>
                  <option value="svc">支持向量机分类</option>
                </optgroup>
                <optgroup label="聚类分析">
                  <option value="kmeans">K均值聚类</option>
                  <option value="meanshift">Mean Shift聚类</option>
                  <option value="dbscan">DBSCAN聚类</option>
                </optgroup>
                <optgroup label="降维分析">
                  <option value="pca">主成分分析(PCA)</option>
                  <option value="tsne">t-SNE降维</option>
                  <option value="standardscaler">标准化</option>
                  <option value="minmaxscaler">归一化</option>
                </optgroup>
                <optgroup label="关联规则学习">
                  <option value="apriori">Apriori算法</option>
                  <option value="associationrules">关联规则</option>
                </optgroup>
              </select>
              <button onClick={handleRunAnalysis} disabled={analysisLoading}>
                {analysisLoading ? '分析中...' : '开始分析'}
              </button>
            </div>

            {/* 高级选项 */}
            <div className="advanced-options">
              <button 
                className="toggle-advanced"
                onClick={() => setShowAdvancedOptions(!showAdvancedOptions)}
              >
                {showAdvancedOptions ? '隐藏高级选项' : '显示高级选项'}
              </button>
              
              {showAdvancedOptions && (
                <div className="advanced-options-content">
                  <div className="form-group">
                    <label>随机种子:</label>
                    <input 
                      type="number" 
                      value={analysisParams.random_state || 42}
                      onChange={(e) => handleParamChange('random_state', parseInt(e.target.value) || 42)}
                    />
                  </div>
                  
                  <div className="form-group">
                    <label>
                      <input 
                        type="checkbox" 
                        checked={analysisParams.is_split ?? true}
                        onChange={(e) => handleParamChange('is_split', e.target.checked)}
                      />
                      数据集划分
                    </label>
                  </div>
                  
                  {analysisParams.is_split && (
                    <div className="form-group">
                      <label>训练集比例:</label>
                      <input 
                        type="number" 
                        min="0" 
                        max="1" 
                        step="0.1"
                        value={analysisParams.split_ratio || 0.8}
                        onChange={(e) => handleParamChange('split_ratio', parseFloat(e.target.value) || 0.8)}
                      />
                    </div>
                  )}
                  
                  <div className="form-group">
                    <label>特征列 (逗号分隔):</label>
                    <input 
                      type="text" 
                      placeholder="col1,col2,col3"
                      value={analysisParams.feature_cols || ''}
                      onChange={(e) => handleParamChange('feature_cols', e.target.value)}
                    />
                  </div>
                  
                  <div className="form-group">
                    <label>目标列:</label>
                    <input 
                      type="text" 
                      placeholder="target_column"
                      value={analysisParams.target_col || ''}
                      onChange={(e) => handleParamChange('target_col', e.target.value)}
                    />
                  </div>
                  
                  <div className="form-group">
                    <label>评估指标 (逗号分隔):</label>
                    <input 
                      type="text" 
                      placeholder="accuracy,precision,recall"
                      value={analysisParams.metrics_list || ''}
                      onChange={(e) => handleParamChange('metrics_list', e.target.value)}
                    />
                  </div>
                  
                  <div className="form-group">
                    <label>
                      <input 
                        type="checkbox" 
                        checked={analysisParams.is_return_model_param ?? false}
                        onChange={(e) => handleParamChange('is_return_model_param', e.target.checked)}
                      />
                      返回模型参数
                    </label>
                  </div>
                  
                  <div className="form-group">
                    <label>
                      <input 
                        type="checkbox" 
                        checked={analysisParams.is_return_model_score ?? true}
                        onChange={(e) => handleParamChange('is_return_model_score', e.target.checked)}
                      />
                      返回模型评分
                    </label>
                  </div>
                  
                  <div className="form-group">
                    <label>
                      <input 
                        type="checkbox" 
                        checked={analysisParams.is_return_training_set ?? false}
                        onChange={(e) => handleParamChange('is_return_training_set', e.target.checked)}
                      />
                      返回训练集
                    </label>
                  </div>
                  
                  <div className="form-group">
                    <label>
                      <input 
                        type="checkbox" 
                        checked={analysisParams.is_return_model_predicting_set ?? false}
                        onChange={(e) => handleParamChange('is_return_model_predicting_set', e.target.checked)}
                      />
                      返回预测结果
                    </label>
                  </div>
                </div>
              )}
            </div>

            {/* 模型特定参数 (示例) */}
            {selectedModel && (
              <div className="model-specific-params">
                <h3>{getModelDisplayName(selectedModel)} 参数设置</h3>
                {renderModelSpecificParams(selectedModel)}
              </div>
            )}
          </div>
        )}

        {activeTab === 'visualization' && (
          <div className="data-visualization">
            <h2>数据可视化</h2>
            <div className="visualization-options">
              <select>
                <option>选择图表类型</option>
                <option>散点图</option>
                <option>折线图</option>
                <option>柱状图</option>
                <option>饼图</option>
              </select>
              <button onClick={() => handleAction('生成图表')} disabled={analysisLoading}>
                {analysisLoading ? '生成中...' : '生成图表'}
              </button>
            </div>
          </div>
        )}

        {activeTab === 'report' && (
          <div className="report-generation">
            <h2>报表生成</h2>
            <div className="report-options">
              <select>
                <option>选择报告格式</option>
                <option>PDF</option>
                <option>HTML</option>
                <option>Word</option>
              </select>
              <button onClick={() => handleAction('生成报告')} disabled={analysisLoading}>
                {analysisLoading ? '生成中...' : '生成报告'}
              </button>
            </div>
          </div>
        )}

        {/* 结果显示容器 */}
        {resultMessage && (
          <div className="result-container">
            <p>{resultMessage}</p>
          </div>
        )}
        {analysisError && (
          <div className="result-container" style={{backgroundColor: '#ffe6e6', borderColor: '#ff9999'}}>
            <p style={{color: '#cc0000'}}>错误: {analysisError}</p>
          </div>
        )}
      </main>
    </div>
  )
}

// 获取模型显示名称
function getModelDisplayName(modelKey: string): string {
  const modelNames: Record<string, string> = {
    'linearregression': '线性回归',
    'ridge': '岭回归',
    'lasso': 'Lasso回归',
    'logisticregression': '逻辑回归',
    'decisiontreeclassifier': '决策树分类',
    'kneighborsclassifier': 'K近邻分类',
    'svc': '支持向量机分类',
    'kmeans': 'K均值聚类',
    'meanshift': 'Mean Shift聚类',
    'dbscan': 'DBSCAN聚类',
    'pca': '主成分分析(PCA)',
    'tsne': 't-SNE降维',
    'standardscaler': '标准化',
    'minmaxscaler': '归一化',
    'apriori': 'Apriori算法',
    'associationrules': '关联规则'
  }
  
  return modelNames[modelKey] || modelKey
}

// 渲染模型特定参数设置
function renderModelSpecificParams(modelKey: string) {
  switch (modelKey) {
    case 'linearregression':
      return (
        <div className="form-group">
          <label>
            <input type="checkbox" />
            是否拟合截距
          </label>
        </div>
      )
      
    case 'ridge':
      return (
        <>
          <div className="form-group">
            <label>正则化强度 (alpha):</label>
            <input type="number" step="0.1" defaultValue="1.0" />
          </div>
          <div className="form-group">
            <label>随机种子:</label>
            <input type="number" defaultValue="42" />
          </div>
        </>
      )
      
    case 'decisiontreeclassifier':
      return (
        <>
          <div className="form-group">
            <label>最大深度:</label>
            <input type="number" placeholder="无限制" />
          </div>
          <div className="form-group">
            <label>最小分割样本数:</label>
            <input type="number" defaultValue="2" />
          </div>
          <div className="form-group">
            <label>随机种子:</label>
            <input type="number" defaultValue="42" />
          </div>
        </>
      )
      
    case 'kmeans':
      return (
        <>
          <div className="form-group">
            <label>聚类数量:</label>
            <input type="number" defaultValue="3" />
          </div>
          <div className="form-group">
            <label>随机种子:</label>
            <input type="number" defaultValue="42" />
          </div>
        </>
      )
      
    case 'apriori':
      return (
        <>
          <div className="form-group">
            <label>最小支持度:</label>
            <input type="number" step="0.01" defaultValue="0.1" />
          </div>
        </>
      )
      
    default:
      return (
        <p>该模型没有可配置的特定参数</p>
      )
  }
}

export default App