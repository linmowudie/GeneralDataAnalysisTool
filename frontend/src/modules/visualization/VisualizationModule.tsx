import React, { useContext } from 'react';
import './VisualizationModule.css';
import type { Message } from '../../components/MessagePanel';

// 添加消息的函数类型定义
type AddMessageType = (message: string, type?: 'info' | 'success' | 'warning' | 'error') => void;

// 创建 Context 用于传递 addMessage 函数
export const MessageContext = React.createContext<AddMessageType | null>(null);

const VisualizationModule: React.FC = () => {
  const addMessage = useContext(MessageContext);
  
  return (
    <div className="visualization-module">
      <h3>可视化</h3>
      <div>可视化参数设置区域</div>
      <button onClick={() => addMessage && addMessage('可视化模块加载成功', 'success')}>测试消息</button>
    </div>
  );
};

export default VisualizationModule;