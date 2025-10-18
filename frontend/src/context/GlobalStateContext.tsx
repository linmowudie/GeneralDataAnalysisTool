import React, { createContext, useContext, useState, useEffect } from 'react';
import type { ReactNode } from 'react';
import { sessionService } from '../services/sessionService';

// 定义全局状态类型
interface GlobalState {
  // 数据导入模块状态
  dataImport: {
    importType: 'file' | 'database' | 'api';
    uploadProgress: number;
    uploadStatus: 'idle' | 'uploading' | 'success' | 'error';
    uploadMessage: string;
    dbType: string;
    host: string;
    port: string;
    database: string;
    table: string;
    username: string;
    password: string;
    dbImportStatus: 'idle' | 'importing' | 'success' | 'error';
    dbImportMessage: string;
  };
  // 可以继续添加其他模块的状态
}

// 定义Context类型
interface GlobalStateContextType {
  state: GlobalState;
  updateDataImportState: (newState: Partial<GlobalState['dataImport']>) => void;
  resetState: () => void;
}

// 创建Context
const GlobalStateContext = createContext<GlobalStateContextType | undefined>(undefined);

// 定义Provider组件
export const GlobalStateProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  // 默认状态
  const defaultState: GlobalState = {
    dataImport: {
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
      dbImportMessage: '',
    }
  };

  const [state, setState] = useState<GlobalState>(defaultState);

  // 页面加载时检查是否需要清除痕迹
  useEffect(() => {
    const shouldClearTraces = sessionStorage.getItem('shouldClearTraces');
    if (shouldClearTraces === 'true') {
      // 清除痕迹，使用默认状态
      setState(defaultState);
      // 清除标记
      sessionStorage.removeItem('shouldClearTraces');
    }
  }, []);

  // 页面即将卸载时设置标记并结束会话
  useEffect(() => {
    const handleBeforeUnload = () => {
      // 设置标记，表示下次加载时需要清除痕迹
      sessionStorage.setItem('shouldClearTraces', 'true');
      
      // 结束当前会话
      const sessionId = sessionService.getCurrentSessionId();
      if (sessionId) {
        sessionService.deleteSession(sessionId).catch(error => {
          console.error('结束会话失败:', error);
        });
      }
    };

    window.addEventListener('beforeunload', handleBeforeUnload);
    
    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload);
    };
  }, []);

  // 更新数据导入模块状态
  const updateDataImportState = (newState: Partial<GlobalState['dataImport']>) => {
    setState(prevState => ({
      ...prevState,
      dataImport: {
        ...prevState.dataImport,
        ...newState
      }
    }));
  };

  // 重置状态到默认值
  const resetState = () => {
    setState(defaultState);
    // 同时清除会话
    const sessionId = sessionService.getCurrentSessionId();
    if (sessionId) {
      sessionService.deleteSession(sessionId).catch(error => {
        console.error('结束会话失败:', error);
      });
    }
  };

  const value = {
    state,
    updateDataImportState,
    resetState
  };

  return (
    <GlobalStateContext.Provider value={value}>
      {children}
    </GlobalStateContext.Provider>
  );
};

// 创建自定义Hook方便使用
export const useGlobalState = () => {
  const context = useContext(GlobalStateContext);
  if (context === undefined) {
    throw new Error('useGlobalState must be used within a GlobalStateProvider');
  }
  return context;
};