import React, { useContext } from 'react';
import './DataCleaningModule.css';

// 添加消息的函数类型定义
type AddMessageType = (message: string, type?: 'info' | 'success' | 'warning' | 'error') => void;

// 创建 Context 用于传递 addMessage 函数
export const MessageContext = React.createContext<AddMessageType | null>(null);

const DataCleaningModule: React.FC = () => {
  const addMessage = useContext(MessageContext);
  
  return (
    <div className="data-cleaning-module">
      <h3>数据清洗</h3>
      <div>数据清洗参数设置区域</div>
      {addMessage && (
        <div>
          <button onClick={() => addMessage('数据清洗模块加载成功', 'success')}>
            测试成功消息
          </button>
          <button onClick={() => addMessage('这是一条警告信息', 'warning')}>
            测试警告消息
          </button>
          <button onClick={() => addMessage('这是一条错误信息', 'error')}>
            测试错误消息
          </button>
        </div>
      )}
    </div>
  );
};

export default DataCleaningModule;