import React, { useState, useEffect, useContext } from 'react';
import './styles/layout.css';
import './styles/importTypes.css';
import './styles/forms.css';
import './styles/fileImport.css';
import './styles/dbImport.css';
import './styles/dbParams.css';
import './styles/buttons.css';
import './styles/progress.css';
import './styles/status.css';
import './styles/apiImport.css';
import { dataImportService } from '../../services/dataImportService';
import { sessionService } from '../../services/sessionService';
import { useGlobalState } from '../../context/GlobalStateContext';
import type { Message } from '../../components/MessagePanel';

// 添加消息的函数类型定义
type AddMessageType = (message: string, type?: 'info' | 'success' | 'warning' | 'error') => void;

// 创建 Context 用于传递 addMessage 函数
export const MessageContext = React.createContext<AddMessageType | null>(null);

/**
 * 数据导入模块
 * 提供文件、数据库和API三种数据导入方式
 * 
 * @component
 * @example
 * ```tsx
 * <DataImportModule />
 * ```
 */
const DataImportModule: React.FC = () => {
  const { state, updateDataImportState } = useGlobalState();
  const addMessage = useContext(MessageContext);
  
  // 导入类型切换状态
  const [importType, setImportType] = useState<'file' | 'database' | 'api'>(state.dataImport.importType);
  
  // 文件导入状态
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadProgress, setUploadProgress] = useState<number>(state.dataImport.uploadProgress);
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'uploading' | 'success' | 'error'>(state.dataImport.uploadStatus);
  const [uploadMessage, setUploadMessage] = useState(state.dataImport.uploadMessage);
  const [importMode, setImportMode] = useState<'normal' | 'streaming'>('normal'); // 新增：导入模式切换
  
  // 数据库导入状态
  const [dbType, setDbType] = useState(state.dataImport.dbType);
  const [host, setHost] = useState(state.dataImport.host);
  const [port, setPort] = useState(state.dataImport.port);
  const [database, setDatabase] = useState(state.dataImport.database);
  const [table, setTable] = useState(state.dataImport.table);
  const [username, setUsername] = useState(state.dataImport.username);
  const [password, setPassword] = useState(state.dataImport.password);
  const [dbImportStatus, setDbImportStatus] = useState<'idle' | 'importing' | 'success' | 'error'>(state.dataImport.dbImportStatus);
  const [dbImportMessage, setDbImportMessage] = useState(state.dataImport.dbImportMessage);
  
  /**
   * 更新全局状态
   * @param newState - 新的状态对象
   */
  const updateGlobalState = (newState: any) => {
    updateDataImportState(newState);
  };

  /**
   * 处理文件选择事件
   * @param e - 文件输入框的change事件
   */
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    console.log('文件选择事件触发:', e.target.files);
    if (e.target.files && e.target.files[0]) {
      console.log('选中的文件:', e.target.files[0]);
      setSelectedFile(e.target.files[0]);
      setUploadStatus('idle');
      setUploadMessage('');
      updateGlobalState({
        uploadStatus: 'idle',
        uploadMessage: ''
      });
      addMessage && addMessage(`已选择文件: ${e.target.files[0].name}`, 'info');
    } else {
      console.log('未选择文件或取消选择');
      addMessage && addMessage('未选择文件', 'warning');
    }
  };
  
  /**
   * 处理文件上传
   * 支持普通上传和流式上传两种模式
   */
  const handleFileUpload = async () => {
    console.log('开始处理文件上传，选中的文件:', selectedFile);
    if (!selectedFile) {
      setUploadMessage('请选择一个文件');
      updateGlobalState({
        uploadMessage: '请选择一个文件'
      });
      addMessage && addMessage('请选择一个文件', 'warning');
      return;
    }
    
    try {
      // 确保有会话ID
      let sessionId = sessionService.getCurrentSessionId();
      console.log('当前会话ID:', sessionId);
      if (!sessionId) {
        console.log('创建新会话...');
        await sessionService.createSession();
        sessionId = sessionService.getCurrentSessionId();
        console.log('新会话ID:', sessionId);
        if (!sessionId) {
          throw new Error('创建会话失败');
        }
      }
      
      setUploadStatus('uploading');
      setUploadProgress(0);
      setUploadMessage(`正在${importMode === 'streaming' ? '流式导入' : '上传'}文件...`);
      updateGlobalState({
        uploadStatus: 'uploading',
        uploadProgress: 0,
        uploadMessage: `正在${importMode === 'streaming' ? '流式导入' : '上传'}文件...`
      });
      addMessage && addMessage(`正在${importMode === 'streaming' ? '流式导入' : '上传'}文件...`, 'info');
      
      // 模拟进度更新
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return prev;
          }
          return prev + 10;
        });
      }, 300);
      
      // 上传文件
      console.log(`开始${importMode === 'streaming' ? '流式导入' : '上传'}文件到服务器...`);
      const response = importMode === 'streaming' 
        ? await dataImportService.streamingUploadFile(selectedFile, sessionId)
        : await dataImportService.uploadFile(selectedFile, sessionId);
      
      clearInterval(progressInterval);
      setUploadProgress(100);
      setUploadStatus('success');
      setUploadMessage(`${importMode === 'streaming' ? '流式导入' : '文件上传'}成功`);
      updateGlobalState({
        uploadProgress: 100,
        uploadStatus: 'success',
        uploadMessage: `${importMode === 'streaming' ? '流式导入' : '文件上传'}成功`
      });
      addMessage && addMessage(`${importMode === 'streaming' ? '流式导入' : '文件上传'}成功`, 'success');
      
      console.log('文件上传结果:', response);
      
      // 触发父组件的消息更新
      if (window && window.dispatchEvent) {
        window.dispatchEvent(new CustomEvent('dataImportSuccess', { 
          detail: { 
            importType: 'file', 
            fileName: selectedFile.name,
            importMode: importMode
          } 
        }));
      }
      
    } catch (error) {
      console.error('文件上传失败:', error);
      setUploadStatus('error');
      setUploadMessage(error instanceof Error ? error.message : '文件上传失败');
      updateGlobalState({
        uploadStatus: 'error',
        uploadMessage: error instanceof Error ? error.message : '文件上传失败'
      });
      addMessage && addMessage(error instanceof Error ? error.message : '文件上传失败', 'error');
    }
  };
  
  /**
   * 处理数据库类型变更
   * 根据数据库类型自动设置默认端口
   * @param newDbType - 新的数据库类型
   */
  const handleDbTypeChange = (newDbType: string) => {
    setDbType(newDbType);
    
    // 根据数据库类型设置默认端口
    switch (newDbType) {
      case 'mysql':
        setPort('3306');
        break;
      case 'postgresql':
        setPort('5432');
        break;
      case 'mssql':
        setPort('1433');
        break;
      case 'oracle':
        setPort('1521');
        break;
      case 'mongodb':
        setPort('27017');
        break;
      case 'redis':
        setPort('6379');
        break;
      case 'sqlite':
        setPort('');
        break;
      default:
        setPort('3306');
    }
    updateGlobalState({
      dbType: newDbType,
      port: newDbType === 'mysql' ? '3306' : 
            newDbType === 'postgresql' ? '5432' : 
            newDbType === 'mssql' ? '1433' : 
            newDbType === 'oracle' ? '1521' : 
            newDbType === 'mongodb' ? '27017' : 
            newDbType === 'redis' ? '6379' : 
            newDbType === 'sqlite' ? '' : '3306'
    });
  };
  
  /**
   * 处理数据库导入
   */
  const handleDatabaseImport = async () => {
    // 基本表单验证
    if (!host || !port || !database || !table) {
      setDbImportMessage('请填写必填字段');
      updateGlobalState({
        dbImportMessage: '请填写必填字段'
      });
      addMessage && addMessage('请填写必填字段', 'warning');
      return;
    }
    
    try {
      // 确保有会话ID
      let sessionId = sessionService.getCurrentSessionId();
      if (!sessionId) {
        await sessionService.createSession();
        sessionId = sessionService.getCurrentSessionId();
        if (!sessionId) {
          throw new Error('创建会话失败');
        }
      }
      
      setDbImportStatus('importing');
      setDbImportMessage('正在导入数据库数据...');
      updateGlobalState({
        dbImportStatus: 'importing',
        dbImportMessage: '正在导入数据库数据...'
      });
      addMessage && addMessage('正在导入数据库数据...', 'info');
      
      // 导入数据库数据
      const response = await dataImportService.importFromDatabase(
        dbType,
        host,
        parseInt(port),
        database,
        table,
        username,
        password,
        sessionId
      );
      
      if (response.success) {
        setDbImportStatus('success');
        setDbImportMessage('数据库数据导入成功');
        updateGlobalState({
          dbImportStatus: 'success',
          dbImportMessage: '数据库数据导入成功'
        });
        addMessage && addMessage('数据库数据导入成功', 'success');
        
        // 触发父组件的消息更新
        if (window && window.dispatchEvent) {
          window.dispatchEvent(new CustomEvent('dataImportSuccess', { 
            detail: { 
              importType: 'database', 
              dbType,
              table
            } 
          }));
        }
      } else {
        throw new Error(response.message || '数据库导入失败');
      }
      
    } catch (error) {
      console.error('数据库导入失败:', error);
      setDbImportStatus('error');
      setDbImportMessage(error instanceof Error ? error.message : '数据库导入失败');
      updateGlobalState({
        dbImportStatus: 'error',
        dbImportMessage: error instanceof Error ? error.message : '数据库导入失败'
      });
      addMessage && addMessage(error instanceof Error ? error.message : '数据库导入失败', 'error');
    }
  };
  
  /**
   * 处理API导入
   */
  const handleApiImport = async () => {
    addMessage && addMessage('API导入功能尚未实现', 'warning');
  };
  
  /**
   * 重置表单
   */
  const resetForm = () => {
    setSelectedFile(null);
    setUploadProgress(0);
    setUploadStatus('idle');
    setUploadMessage('');
    
    setDbType('mysql');
    setHost('localhost');
    setPort('3306');
    setDatabase('');
    setTable('');
    setUsername('');
    setPassword('');
    setDbImportStatus('idle');
    setDbImportMessage('');
    
    updateGlobalState({
      importType: 'file',
      uploadProgress: 0,
      uploadStatus: 'idle',
      uploadMessage: '',
      dbType: 'mysql',
      host: 'localhost',
      port: '3306',
      database: '',
      table: '',
      username: '',
      password: '',
      dbImportStatus: 'idle',
      dbImportMessage: ''
    });
  };

  return (
    <div className="data-import-container">
      <div className="import-type-selector">
        <div className="selector-buttons">
          <button 
            className={`import-type-btn ${importType === 'file' ? 'active' : ''}`}
            onClick={() => {
              setImportType('file');
              updateGlobalState({ importType: 'file' });
            }}
          >
            文件导入
          </button>
          <button 
            className={`import-type-btn ${importType === 'database' ? 'active' : ''}`}
            onClick={() => {
              setImportType('database');
              updateGlobalState({ importType: 'database' });
            }}
          >
            数据库导入
          </button>
          <button 
            className={`import-type-btn ${importType === 'api' ? 'active' : ''}`}
            onClick={() => {
              setImportType('api');
              updateGlobalState({ importType: 'api' });
            }}
          >
            API导入
          </button>
        </div>
      </div>

      <div className="import-content">
        {/* 文件导入表单 */}
        {importType === 'file' && (
          <div className="file-import-container">
            <h4>选择文件</h4>
            <div className="file-input-container">
              <input 
                type="file" 
                id="fileInput" 
                onChange={handleFileChange}
                className="file-input"
              />
              <button 
                className="import-btn primary"
                onClick={handleFileUpload}
                disabled={uploadStatus === 'uploading'}
              >
                {uploadStatus === 'uploading' ? `${importMode === 'streaming' ? '流式导入中...' : '上传中...'}` : `${importMode === 'streaming' ? '流式导入' : '上传'}`}
              </button>
            </div>
            
            {/* 导入模式选择 */}
            {selectedFile && (
              <div className="import-mode-selector">
                <label>导入模式：</label>
                <label className="radio-label">
                  <input 
                    type="radio" 
                    name="importMode" 
                    value="normal" 
                    checked={importMode === 'normal'}
                    onChange={() => setImportMode('normal')}
                    disabled={uploadStatus === 'uploading'}
                  />
                  普通导入
                </label>
                <label className="radio-label">
                  <input 
                    type="radio" 
                    name="importMode" 
                    value="streaming" 
                    checked={importMode === 'streaming'}
                    onChange={() => setImportMode('streaming')}
                    disabled={uploadStatus === 'uploading'}
                  />
                  流式导入（大文件推荐）
                </label>
              </div>
            )}
            
            {/* 显示选中的文件名 */}
            {selectedFile && (
              <div className="selected-file-info">
                <p>已选择文件: {selectedFile.name}</p>
                <p>文件大小: {selectedFile.size} 字节</p>
                <p>文件类型: {selectedFile.type}</p>
              </div>
            )}
            
            {/* 上传进度条 */}
            {(uploadStatus === 'uploading' || uploadStatus === 'success' || uploadStatus === 'error') && (
              <div className="progress-container">
                <div className="progress-bar">
                  <div 
                    className="progress-fill"
                    style={{ width: `${uploadProgress}%` }}
                  ></div>
                </div>
                <div className="progress-info">
                  <span className="progress-text">{uploadMessage}</span>
                  <span className="progress-percent">{uploadProgress}%</span>
                </div>
              </div>
            )}
          </div>
        )}

        {/* 数据库导入表单 */}
        {importType === 'database' && (
          <div className="database-import-container">
            <div className="database-type-selector">
              <h3>数据库类型</h3>
              <div className="db-type-options">
                {['mysql', 'postgresql', 'mssql', 'oracle', 'mongodb', 'redis', 'sqlite'].map((type) => (
                  <div
                    key={type}
                    className={`db-type-option ${dbType === type ? 'active' : ''}`}
                    onClick={() => handleDbTypeChange(type)}
                  >
                    {type}
                  </div>
                ))}
              </div>
            </div>
            
            <div className="database-params-form">
              <h3>数据库连接参数</h3>
              <div className="form-content">
                <div className="form-group">
                  <label htmlFor="host">主机地址:</label>
                  <input 
                    type="text" 
                    id="host" 
                    value={host} 
                    onChange={(e) => {
                      setHost(e.target.value);
                      updateGlobalState({ host: e.target.value });
                    }}
                    placeholder="例如: localhost"
                  />
                </div>
                
                <div className="form-group">
                  <label htmlFor="port">端口:</label>
                  <input 
                    type="text" 
                    id="port" 
                    value={port} 
                    onChange={(e) => {
                      setPort(e.target.value);
                      updateGlobalState({ port: e.target.value });
                    }}
                    placeholder="例如: 3306"
                  />
                </div>
                
                <div className="form-group">
                  <label htmlFor="database">数据库名:</label>
                  <input 
                    type="text" 
                    id="database" 
                    value={database} 
                    onChange={(e) => {
                      setDatabase(e.target.value);
                      updateGlobalState({ database: e.target.value });
                    }}
                    placeholder="输入数据库名称"
                  />
                </div>
                
                <div className="form-group">
                  <label htmlFor="table">表名:</label>
                  <input 
                    type="text" 
                    id="table" 
                    value={table} 
                    onChange={(e) => {
                      setTable(e.target.value);
                      updateGlobalState({ table: e.target.value });
                    }}
                    placeholder="输入表名"
                  />
                </div>
                
                <div className="form-group">
                  <label htmlFor="username">用户名:</label>
                  <input 
                    type="text" 
                    id="username" 
                    value={username} 
                    onChange={(e) => {
                      setUsername(e.target.value);
                      updateGlobalState({ username: e.target.value });
                    }}
                    placeholder="输入用户名"
                  />
                </div>
                
                <div className="form-group">
                  <label htmlFor="password">密码:</label>
                  <input 
                    type="password" 
                    id="password" 
                    value={password} 
                    onChange={(e) => {
                      setPassword(e.target.value);
                      updateGlobalState({ password: e.target.value });
                    }}
                    placeholder="输入密码"
                  />
                </div>
                
                <div className="form-actions">
                  <button 
                    className="import-btn primary"
                    onClick={handleDatabaseImport}
                    disabled={dbImportStatus === 'importing'}
                  >
                    {dbImportStatus === 'importing' ? '导入中...' : '导入'}
                  </button>
                  <button 
                    className="import-btn"
                    onClick={resetForm}
                  >
                    重置
                  </button>
                </div>
                
                {/* 数据库导入状态 */}
                {(dbImportStatus === 'importing' || dbImportStatus === 'success' || dbImportStatus === 'error') && (
                  <div className={`status-message ${dbImportStatus}`}>
                    <span className="status-icon">
                      {dbImportStatus === 'success' ? '✓' : dbImportStatus === 'error' ? '✗' : '⏳'}
                    </span>
                    <span className="status-message">{dbImportMessage}</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* API导入表单 */}
        {importType === 'api' && (
          <div className="api-import-placeholder">
            <h4>API导入</h4>
            <div className="api-import-content">
              <p>API导入功能正在开发中...</p>
              <button 
                className="import-btn primary"
                onClick={handleApiImport}
              >
                导入
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default DataImportModule;