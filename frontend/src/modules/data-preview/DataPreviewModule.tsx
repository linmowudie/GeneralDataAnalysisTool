import React, { useState, useEffect, useContext } from 'react';
import './DataPreviewModule.css';
import { dataPreviewService } from '../../services/dataPreviewService';
import { sessionService } from '../../services/sessionService';
import type { Message } from '../../components/MessagePanel';

// 添加消息的函数类型定义
type AddMessageType = (message: string, type?: 'info' | 'success' | 'warning' | 'error') => void;

// 创建 Context 用于传递 addMessage 函数
export const MessageContext = React.createContext<AddMessageType | null>(null);

const DataPreviewModule: React.FC = () => {
  const [previewData, setPreviewData] = useState<any>(null);
  const [datasetInfo, setDatasetInfo] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const addMessage = useContext(MessageContext);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        addMessage && addMessage('正在加载数据...', 'info');
        
        const sessionId = sessionService.getCurrentSessionId();
        if (!sessionId) {
          throw new Error('未找到有效的会话ID');
        }

        // 获取数据预览
        const preview = await dataPreviewService.getDataPreview(sessionId);
        setPreviewData(preview);

        // 获取数据集信息
        const info = await dataPreviewService.getDatasetInfo(sessionId);
        setDatasetInfo(info);
        addMessage && addMessage('数据加载成功', 'success');
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : '获取数据失败';
        setError(errorMessage);
        addMessage && addMessage(errorMessage, 'error');
        console.error('获取数据预览失败:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="data-preview-module">
        <h3>数据预览</h3>
        <div>正在加载数据...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="data-preview-module">
        <h3>数据预览</h3>
        <div className="error-message">错误: {error}</div>
      </div>
    );
  }

  return (
    <div className="data-preview-module">
      <h3>数据预览</h3>
      
      {datasetInfo && (
        <div className="dataset-info">
          <h4>数据集信息</h4>
          <div className="info-item">
            <span className="info-label">文件名:</span>
            <span className="info-value">{previewData?.file_name || datasetInfo.dataset_name}</span>
          </div>
          <div className="info-item">
            <span className="info-label">总行数:</span>
            <span className="info-value">{previewData?.total_rows || datasetInfo.total_records}</span>
          </div>
          <div className="info-item">
            <span className="info-label">总列数:</span>
            <span className="info-value">{previewData?.total_columns || (datasetInfo.features_count + 1)}</span>
          </div>
          <div className="info-item">
            <span className="info-label">目标变量:</span>
            <span className="info-value">{datasetInfo.target_variable}</span>
          </div>
        </div>
      )}

      {previewData && (
        <div className="data-preview">
          <h4>数据预览 (前5行)</h4>
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  {previewData.columns.map((col: string, index: number) => (
                    <th key={index}>{col}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {previewData.preview_data.map((row: any, rowIndex: number) => (
                  <tr key={rowIndex}>
                    {previewData.columns.map((col: string, colIndex: number) => (
                      <td key={colIndex}>{row[col]}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default DataPreviewModule;