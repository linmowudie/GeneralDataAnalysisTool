import React from 'react';
import '../modules/analysis/DataAnalysis.css';

// 导出消息接口
export interface Message {
  id: string;
  type: 'info' | 'success' | 'warning' | 'error';
  content: string;
  timestamp: Date;
}

interface MessagePanelProps {
  messages: Message[];
  onClear?: () => void;
  onDismiss?: (id: string) => void;
}

const MessagePanel: React.FC<MessagePanelProps> = ({ 
  messages, 
  onClear,
  onDismiss
}) => {
  const getTypeClass = (type: string) => {
    switch (type) {
      case 'success': return 'message-success';
      case 'warning': return 'message-warning';
      case 'error': return 'message-error';
      default: return 'message-info';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'success': return '✓';
      case 'warning': return '⚠';
      case 'error': return '✗';
      default: return 'ℹ';
    }
  };

  return (
    <div className="message-panel">
      <div className="message-panel-header">
        <h3>消息返回</h3>
        {onClear && (
          <button className="clear-messages-btn" onClick={onClear}>
            清空
          </button>
        )}
      </div>
      <div className="messages-content">
        {messages.length === 0 ? (
          <div className="no-messages">暂无消息</div>
        ) : (
          messages.map((message) => (
            <div 
              key={message.id} 
              className={`message-item ${getTypeClass(message.type)}`}
            >
              <span className="message-icon">{getTypeIcon(message.type)}</span>
              <span className="message-content">{message.content}</span>
              <span className="message-time">
                {message.timestamp.toLocaleTimeString()}
              </span>
              {onDismiss && (
                <button 
                  className="dismiss-message-btn"
                  onClick={() => onDismiss(message.id)}
                >
                  ×
                </button>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default MessagePanel;