import React, { createContext, useContext, useState, useEffect } from 'react';
import type { ReactNode } from 'react';

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
}

// 创建Context
const GlobalStateContext = createContext<GlobalStateContextType | undefined>(undefined);

// 定义Provider组件
export const GlobalStateProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  // 从localStorage加载保存的数据，如果没有则使用默认值
  const loadStateFromStorage = (): GlobalState => {
    const savedData = localStorage.getItem('globalAppState');
    if (savedData) {
      try {
        const parsedData = JSON.parse(savedData);
        return {
          dataImport: {
            importType: parsedData.dataImport?.importType || 'file',
            uploadProgress: parsedData.dataImport?.uploadProgress || 0,
            uploadStatus: parsedData.dataImport?.uploadStatus || 'idle',
            uploadMessage: parsedData.dataImport?.uploadMessage || '',
            dbType: parsedData.dataImport?.dbType || 'mysql',
            host: parsedData.dataImport?.host || 'localhost',
            port: parsedData.dataImport?.port || '3306',
            database: parsedData.dataImport?.database || '',
            table: parsedData.dataImport?.table || '',
            username: parsedData.dataImport?.username || '',
            password: parsedData.dataImport?.password || '',
            dbImportStatus: parsedData.dataImport?.dbImportStatus || 'idle',
            dbImportMessage: parsedData.dataImport?.dbImportMessage || '',
          }
        };
      } catch (e) {
        console.error('解析保存的数据时出错:', e);
      }
    }
    
    // 默认状态
    return {
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
  };

  const [state, setState] = useState<GlobalState>(loadStateFromStorage());

  // 保存数据到localStorage
  useEffect(() => {
    localStorage.setItem('globalAppState', JSON.stringify(state));
  }, [state]);

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

  const value = {
    state,
    updateDataImportState
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