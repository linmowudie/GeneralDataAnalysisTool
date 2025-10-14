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
  
  // 更新全局状态
  const updateGlobalState = (newState: any) => {
    updateDataImportState(newState);
  };

  // 处理文件选择
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
      setUploadStatus('idle');
      setUploadMessage('');
      updateGlobalState({
        uploadStatus: 'idle',
        uploadMessage: ''
      });
    }
  };
  
  // 处理文件上传
  const handleFileUpload = async () => {
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
      if (!sessionId) {
        await sessionService.createSession();
        sessionId = sessionService.getCurrentSessionId();
        if (!sessionId) {
          throw new Error('创建会话失败');
        }
      }
      
      setUploadStatus('uploading');
      setUploadProgress(0);
      setUploadMessage('正在上传文件...');
      updateGlobalState({
        uploadStatus: 'uploading',
        uploadProgress: 0,
        uploadMessage: '正在上传文件...'
      });
      addMessage && addMessage('正在上传文件...', 'info');
      
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
      const response = await dataImportService.uploadFile(selectedFile, sessionId);
      
      clearInterval(progressInterval);
      setUploadProgress(100);
      setUploadStatus('success');
      setUploadMessage('文件上传成功');
      updateGlobalState({
        uploadProgress: 100,
        uploadStatus: 'success',
        uploadMessage: '文件上传成功'
      });
      addMessage && addMessage('文件上传成功', 'success');
      
      console.log('文件上传结果:', response);
      
      // 触发父组件的消息更新
      if (window && window.dispatchEvent) {
        window.dispatchEvent(new CustomEvent('dataImportSuccess', { detail: { importType: 'file', fileName: selectedFile.name } }));
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
  
  // 处理数据库类型变更，更新默认端口和参数
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
  
  // 处理数据库导入
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
      setDbImportMessage('正在从数据库导入...');
      updateGlobalState({
        dbImportStatus: 'importing',
        dbImportMessage: '正在从数据库导入...'
      });
      addMessage && addMessage('正在从数据库导入...', 'info');
      
      // 导入数据
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
      
      setDbImportStatus('success');
      setDbImportMessage('数据库导入成功');
      updateGlobalState({
        dbImportStatus: 'success',
        dbImportMessage: '数据库导入成功'
      });
      addMessage && addMessage('数据库导入成功', 'success');
      
      console.log('数据库导入结果:', response);
      
      // 触发父组件的消息更新
      if (window && window.dispatchEvent) {
        window.dispatchEvent(new CustomEvent('dataImportSuccess', { detail: { importType: 'database', dbType, table } }));
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
  
  // 渲染文件导入界面
  const renderFileImport = () => (
    <div className="file-import-container">
      <div className="import-section">
        <div className="form-group">
          <label htmlFor="file-upload">选择文件</label>
          <input 
            type="file" 
            id="file-upload" 
            onChange={handleFileChange} 
            accept=".csv,.xlsx,.xls,.json,.html,.db"
          />
          {selectedFile && (
            <div className="selected-file">
              <span>{selectedFile.name}</span>
              <button 
                className="remove-file-btn" 
                onClick={() => {
                  setSelectedFile(null);
                  setUploadStatus('idle');
                  setUploadMessage('');
                  updateGlobalState({
                    uploadStatus: 'idle',
                    uploadMessage: ''
                  });
                }}
              >
                移除
              </button>
            </div>
          )}
        </div>
        
        <div className="form-group">
          <button 
            className="import-btn primary" 
            onClick={handleFileUpload}
            disabled={!selectedFile || uploadStatus === 'uploading'}
          >
            {uploadStatus === 'uploading' ? '上传中...' : '上传文件'}
          </button>
        </div>
        
        {uploadProgress > 0 && (
          <div className="progress-container">
            <div className="progress-bar">
              <div 
                className="progress-fill" 
                style={{ width: `${uploadProgress}%` }}
              ></div>
            </div>
          </div>
        )}
        
        {uploadMessage && (
          <div className={`status-message ${uploadStatus}`}>
            {uploadMessage}
          </div>
        )}
        
        <div className="supported-formats">
          <p>支持的文件格式: {dataImportService.getSupportedFileFormats().join(', ')}</p>
        </div>
      </div>
    </div>
  );
  
  // 获取数据库的默认端口占位符
  const getDefaultPortPlaceholder = (dbType: string) => {
    switch (dbType) {
      case 'mysql': return '3306';
      case 'postgresql': return '5432';
      case 'mssql': return '1433';
      case 'oracle': return '1521';
      case 'mongodb': return '27017';
      case 'redis': return '6379';
      case 'sqlite': return '';
      default: return '3306';
    }
  };
  
  // 获取数据库名占位符
  const getDatabasePlaceholder = (dbType: string) => {
    switch (dbType) {
      case 'mongodb': return '数据库名称/集合名称';
      case 'redis': return '数据库索引(0-15)';
      case 'sqlite': return '数据库文件路径';
      default: return '数据库名称';
    }
  };
  
  // 获取表名占位符
  const getTablePlaceholder = (dbType: string) => {
    switch (dbType) {
      case 'mongodb': return '集合名称';
      case 'redis': return '键模式';
      default: return '表名称';
    }
  };
  
  // 获取数据库显示名称
  const getDbDisplayName = (dbType: string) => {
    switch (dbType) {
      case 'mysql': return 'MySQL';
      case 'postgresql': return 'PostgreSQL';
      case 'mssql': return 'SQL Server';
      case 'oracle': return 'Oracle';
      case 'sqlite': return 'SQLite';
      case 'mongodb': return 'MongoDB';
      case 'redis': return 'Redis';
      default: return '数据库';
    }
  };
  
  // 渲染数据库导入界面
  const renderDatabaseImport = () => (
    <div className="import-section database-import-container">
      {/* 左侧数据库类型选择器 */}
      <div className="database-type-selector">
        <h3>选择数据库类型</h3>
        <div className="db-type-options">
          <button 
            className={`db-type-option ${dbType === 'mysql' ? 'active' : ''}`}
            onClick={() => handleDbTypeChange('mysql')}
          >
            MySQL
          </button>
          <button 
            className={`db-type-option ${dbType === 'postgresql' ? 'active' : ''}`}
            onClick={() => handleDbTypeChange('postgresql')}
          >
            PostgreSQL
          </button>
          <button 
            className={`db-type-option ${dbType === 'mssql' ? 'active' : ''}`}
            onClick={() => handleDbTypeChange('mssql')}
          >
            SQL Server
          </button>
          <button 
            className={`db-type-option ${dbType === 'oracle' ? 'active' : ''}`}
            onClick={() => handleDbTypeChange('oracle')}
          >
            Oracle
          </button>
          <button 
            className={`db-type-option ${dbType === 'sqlite' ? 'active' : ''}`}
            onClick={() => handleDbTypeChange('sqlite')}
          >
            SQLite
          </button>
          <button 
            className={`db-type-option ${dbType === 'mongodb' ? 'active' : ''}`}
            onClick={() => handleDbTypeChange('mongodb')}
          >
            MongoDB
          </button>
          <button 
            className={`db-type-option ${dbType === 'redis' ? 'active' : ''}`}
            onClick={() => handleDbTypeChange('redis')}
          >
            Redis
          </button>
        </div>
      </div>
      
      {/* 右侧连接参数表单 */}
      <div className="database-params-form">
        <h3>{dbType.toUpperCase()} 连接参数</h3>
        <div className="form-content">
          <div className="form-group">
            <label htmlFor="db-host">主机名</label>
            <input 
              type="text" 
              id="db-host" 
              value={host} 
              onChange={(e) => {
                setHost(e.target.value);
                updateGlobalState({
                  host: e.target.value
                });
              }}
              placeholder="localhost"
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="db-port">端口</label>
            <input 
              type="text" 
              id="db-port" 
              value={port} 
              onChange={(e) => {
                setPort(e.target.value);
                updateGlobalState({
                  port: e.target.value
                });
              }}
              placeholder={getDefaultPortPlaceholder(dbType)}
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="db-name">{getDatabasePlaceholder(dbType)}</label>
            <input 
              type="text" 
              id="db-name" 
              value={database} 
              onChange={(e) => {
                setDatabase(e.target.value);
                updateGlobalState({
                  database: e.target.value
                });
              }}
              placeholder={getDatabasePlaceholder(dbType)}
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="db-table">{getTablePlaceholder(dbType)}</label>
            <input 
              type="text" 
              id="db-table" 
              value={table} 
              onChange={(e) => {
                setTable(e.target.value);
                updateGlobalState({
                  table: e.target.value
                });
              }}
              placeholder={getTablePlaceholder(dbType)}
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="db-username">用户名</label>
            <input 
              type="text" 
              id="db-username" 
              value={username} 
              onChange={(e) => {
                setUsername(e.target.value);
                updateGlobalState({
                  username: e.target.value
                });
              }}
              placeholder="可选"
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="db-password">密码</label>
            <input 
              type="password" 
              id="db-password" 
              value={password} 
              onChange={(e) => {
                setPassword(e.target.value);
                updateGlobalState({
                  password: e.target.value
                });
              }}
              placeholder="可选"
            />
          </div>
          
          <div className="form-group">
            <button 
              className="import-btn primary" 
              onClick={handleDatabaseImport}
              disabled={dbImportStatus === 'importing'}
            >
              {dbImportStatus === 'importing' ? '导入中...' : `从${getDbDisplayName(dbType)}导入`}
            </button>
          </div>
          
          {dbImportMessage && (
            <div className={`status-message ${dbImportStatus}`}>
              {dbImportMessage}
            </div>
          )}
        </div>
      </div>
    </div>
  );
  
  // 渲染API导入界面（后端未实现）
  const renderApiImport = () => (
    <div className="import-section">
      <div className="api-import-placeholder">
        <h4>API导入功能即将上线</h4>
        <p>此功能正在开发中，敬请期待...</p>
        
        <div className="api-import-preview">
          <div className="form-group">
            <label>API URL</label>
            <input 
              type="text" 
              placeholder="https://api.example.com/data" 
              disabled
            />
          </div>
          
          <div className="form-group">
            <label>请求方法</label>
            <select disabled>
              <option value="GET">GET</option>
              <option value="POST">POST</option>
            </select>
          </div>
          
          <div className="form-group">
            <label>认证方式</label>
            <select disabled>
              <option value="none">无</option>
              <option value="basic">Basic Auth</option>
              <option value="token">API Token</option>
            </select>
          </div>
          
          <button 
            className="import-btn primary disabled"
            disabled
          >
            从API导入
          </button>
        </div>
      </div>
    </div>
  );
  
// 移除旧的useEffect，因为现在使用全局状态管理

  return (
    <div className="data-import-module">
      <div className="import-type-selector">
        <button 
          className={`import-type-btn ${importType === 'file' ? 'active' : ''}`}
          onClick={() => {
            setImportType('file');
            updateGlobalState({
              importType: 'file'
            });
          }}
        >
          文件导入
        </button>
        <button 
          className={`import-type-btn ${importType === 'database' ? 'active' : ''}`}
          onClick={() => {
            setImportType('database');
            updateGlobalState({
              importType: 'database'
            });
          }}
        >
          数据库导入
        </button>
        <button 
          className={`import-type-btn ${importType === 'api' ? 'active' : ''}`}
          onClick={() => {
            setImportType('api');
            updateGlobalState({
              importType: 'api'
            });
          }}
        >
          API导入
        </button>
      </div>
      
      <div className="import-content">
        {importType === 'file' && renderFileImport()}
        {importType === 'database' && renderDatabaseImport()}
        {importType === 'api' && renderApiImport()}
      </div>
    </div>
  );
};

export default DataImportModule;