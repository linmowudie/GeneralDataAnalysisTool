import { useState, useEffect } from 'react'
import './App.css'

function App() {
  const [activeTab, setActiveTab] = useState('dashboard')
  const [importType, setImportType] = useState('file')
  const [resultMessage, setResultMessage] = useState('')
  const [selectedModel, setSelectedModel] = useState('')
  const [showAdvancedOptions, setShowAdvancedOptions] = useState(false)
  const [analysisParams, setAnalysisParams] = useState({
    randomState: 42,
    isSplit: true,
    splitRatio: 0.8,
    featureCols: '',
    targetCol: '',
    // 可以继续添加更多参数
  })
  const [dataPreview, setDataPreview] = useState<any>(null)
  const [loadingPreview, setLoadingPreview] = useState(false)

  // 模拟执行操作并显示结果
  const handleAction = (action: string) => {
    setResultMessage(`执行了${action}操作，结果将在此处显示...`)
    
    // 3秒后清除消息
    setTimeout(() => {
      setResultMessage('')
    }, 3000)
  }

  // 获取数据预览
  const fetchDataPreview = async () => {
    setLoadingPreview(true)
    try {
      // 这里应该调用后端API获取数据预览
      // 暂时使用模拟数据
      const mockData = {
        success: true,
        file_name: 'sample_data.csv',
        total_rows: 150,
        total_columns: 5,
        columns: ['sepal_length', 'sepal_width', 'petal_length', 'petal_width', 'species'],
        preview_data: [
          {
            sepal_length: 5.1,
            sepal_width: 3.5,
            petal_length: 1.4,
            petal_width: 0.2,
            species: 'setosa'
          },
          {
            sepal_length: 4.9,
            sepal_width: 3.0,
            petal_length: 1.4,
            petal_width: 0.2,
            species: 'setosa'
          },
          {
            sepal_length: 4.7,
            sepal_width: 3.2,
            petal_length: 1.3,
            petal_width: 0.2,
            species: 'setosa'
          },
          {
            sepal_length: 4.6,
            sepal_width: 3.1,
            petal_length: 1.5,
            petal_width: 0.2,
            species: 'setosa'
          },
          {
            sepal_length: 5.0,
            sepal_width: 3.6,
            petal_length: 1.4,
            petal_width: 0.2,
            species: 'setosa'
          }
        ]
      }
      setDataPreview(mockData)
    } catch (error) {
      setResultMessage('获取数据预览失败: ' + (error as Error).message)
    } finally {
      setLoadingPreview(false)
    }
  }

  // 处理模型选择变化
  const handleModelChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedModel(e.target.value)
  }

  // 处理参数变化
  const handleParamChange = (param: string, value: string | number | boolean) => {
    setAnalysisParams(prev => ({
      ...prev,
      [param]: value
    }))
  }

  // 组件挂载时获取数据预览
  useEffect(() => {
    fetchDataPreview()
  }, [])

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
                <p>当前数据集: 无</p>
                <p>数据行数: 0</p>
                <p>数据列数: 0</p>
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
                <p>运行正常</p>
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
                <input type="file" />
                <button onClick={() => handleAction('文件导入')}>导入文件</button>
              </div>
            )}

            {importType === 'database' && (
              <div className="database-import">
                <div className="form-group">
                  <label>数据库类型:</label>
                  <select>
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
                  <input type="text" placeholder="localhost" />
                </div>
                <div className="form-group">
                  <label>端口:</label>
                  <input type="text" placeholder="3306" />
                </div>
                <div className="form-group">
                  <label>数据库名:</label>
                  <input type="text" placeholder="database_name" />
                </div>
                <div className="form-group">
                  <label>表名或集合名:</label>
                  <input type="text" placeholder="table_name" />
                </div>
                <div className="form-group">
                  <label>用户名:</label>
                  <input type="text" placeholder="username" />
                </div>
                <div className="form-group">
                  <label>密码:</label>
                  <input type="password" placeholder="password" />
                </div>
                <button onClick={() => handleAction('数据库连接并导入')}>连接并导入</button>
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
              <button onClick={fetchDataPreview} disabled={loadingPreview}>
                {loadingPreview ? '加载中...' : '刷新数据'}
              </button>
            </div>
            
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

        {activeTab === 'analysis' && (
          <div className="data-analysis">
            <h2>数据分析</h2>
            <div className="analysis-options">
              <select value={selectedModel} onChange={handleModelChange}>
                <option>选择分析模型</option>
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
              </select>
              <button onClick={() => handleAction('数据分析')}>开始分析</button>
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
                      value={analysisParams.randomState}
                      onChange={(e) => handleParamChange('randomState', parseInt(e.target.value))}
                    />
                  </div>
                  
                  <div className="form-group">
                    <label>
                      <input 
                        type="checkbox" 
                        checked={analysisParams.isSplit}
                        onChange={(e) => handleParamChange('isSplit', e.target.checked)}
                      />
                      数据集划分
                    </label>
                  </div>
                  
                  {analysisParams.isSplit && (
                    <div className="form-group">
                      <label>训练集比例:</label>
                      <input 
                        type="number" 
                        min="0" 
                        max="1" 
                        step="0.1"
                        value={analysisParams.splitRatio}
                        onChange={(e) => handleParamChange('splitRatio', parseFloat(e.target.value))}
                      />
                    </div>
                  )}
                  
                  <div className="form-group">
                    <label>特征列 (逗号分隔):</label>
                    <input 
                      type="text" 
                      placeholder="col1,col2,col3"
                      value={analysisParams.featureCols}
                      onChange={(e) => handleParamChange('featureCols', e.target.value)}
                    />
                  </div>
                  
                  <div className="form-group">
                    <label>目标列:</label>
                    <input 
                      type="text" 
                      placeholder="target_column"
                      value={analysisParams.targetCol}
                      onChange={(e) => handleParamChange('targetCol', e.target.value)}
                    />
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
              <button onClick={() => handleAction('生成图表')}>生成图表</button>
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
              <button onClick={() => handleAction('生成报告')}>生成报告</button>
            </div>
          </div>
        )}

        {/* 结果显示容器 */}
        {resultMessage && (
          <div className="result-container">
            <p>{resultMessage}</p>
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
    'minmaxscaler': '归一化'
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
      
    default:
      return (
        <p>该模型没有可配置的特定参数</p>
      )
  }
}

export default App