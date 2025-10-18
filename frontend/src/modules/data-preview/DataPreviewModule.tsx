import React, { useState, useEffect, useContext, useRef } from 'react';
import './DataPreviewModule.css';
import { dataPreviewService } from '../../services/dataPreviewService';
import { sessionService } from '../../services/sessionService';

// 添加消息的函数类型定义
type AddMessageType = (message: string, type?: 'info' | 'success' | 'warning' | 'error') => void;

// 创建 Context 用于传递 addMessage 函数
export const MessageContext = React.createContext<AddMessageType | null>(null);

/**
 * 数据预览模块
 * 展示导入数据的基本信息和预览内容
 * 
 * @component
 * @example
 * ```tsx
 * <DataPreviewModule />
 * ```
 */
const DataPreviewModule: React.FC = () => {
  const [previewData, setPreviewData] = useState<any>(null);
  const [datasetInfo, setDatasetInfo] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [visibleRows, setVisibleRows] = useState<number>(5); // 默认显示5行
  const [showTable, setShowTable] = useState<boolean>(false); // 控制是否显示悬浮表格
  const [isDragging, setIsDragging] = useState<boolean>(false); // 控制是否正在拖动
  const [dragPosition, setDragPosition] = useState({ x: 100, y: 100 }); // 悬浮表格的位置
  const [startDrag, setStartDrag] = useState({ x: 0, y: 0 }); // 拖动开始时的鼠标位置
  const addMessage = useContext(MessageContext);
  
  // 拖动相关的引用
  const tableContainerRef = useRef<HTMLDivElement>(null);
  
  /**
   * 处理鼠标滚轮事件，将垂直滚动转换为水平滚动
   */
  useEffect(() => {
    const handleWheel = (event: WheelEvent) => {
      if (tableContainerRef.current && !event.ctrlKey) { // 不拦截Ctrl+滚轮（缩放操作）
        event.preventDefault();
        const container = tableContainerRef.current;
        // 滚动速度系数，可以调整
        const scrollAmount = event.deltaY * 0.8;
        container.scrollLeft += scrollAmount;
      }
    };

    const container = tableContainerRef.current;
    if (container) {
      container.addEventListener('wheel', handleWheel, { passive: false });
    }

    return () => {
      if (container) {
        container.removeEventListener('wheel', handleWheel);
      }
    };
  }, []);
  
  /**
   * 处理鼠标按下事件，开始拖动
   * @param e - 鼠标事件
   */
  const handleMouseDown = (e: React.MouseEvent) => {
    if (e.target instanceof HTMLDivElement && e.target.className.includes('draggable-header')) {
      setIsDragging(true);
      setStartDrag({
        x: e.clientX - dragPosition.x,
        y: e.clientY - dragPosition.y
      });
    }
  };
  
  /**
   * 处理鼠标移动事件，更新拖动位置
   * @param e - 鼠标事件
   */
  const handleMouseMove = (e: MouseEvent) => {
    if (isDragging) {
      setDragPosition({
        x: e.clientX - startDrag.x,
        y: e.clientY - startDrag.y
      });
    }
  };
  
  /**
   * 处理鼠标释放事件，结束拖动
   */
  const handleMouseUp = () => {
    setIsDragging(false);
  };
  
  /**
   * 添加全局鼠标事件监听器
   */
  useEffect(() => {
    if (isDragging) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      return () => {
        document.removeEventListener('mousemove', handleMouseMove);
        document.removeEventListener('mouseup', handleMouseUp);
      };
    }
  }, [isDragging, startDrag]);
  
  /**
   * 获取数据预览信息
   */
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // 使用真实的API获取数据，而不是模拟数据
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
        
        setLoading(false);
        
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : '获取数据失败';
        setError(errorMessage);
        console.error('获取数据预览失败:', err);
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  /**
   * 处理可见行数变化
   * @param e - 选择框变化事件
   */
  const handleVisibleRowsChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setVisibleRows(Number(e.target.value));
  };

  // 加载状态显示
  if (loading) {
    return (
      <div className="data-preview-module">
        <h3>数据预览</h3>
        <div>正在加载数据...</div>
      </div>
    );
  }

  // 错误状态显示
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
      
      {/* 数据集信息展示 */}
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

      {/* 数据预览展示 */}
      {previewData && (
        <div className="data-preview">
          {/* 列名显示区域 */}
          <div className="columns-display">
            <h4>数据集列名</h4>
            <div className="columns-textbox">
              {previewData.columns.map((col: string, index: number) => (
                <span key={index} className="column-name">
                  {col}{index < previewData.columns.length - 1 ? ', ' : ''}
                </span>
              ))}
            </div>
          </div>
          
          {/* 预览按钮 */}
          <button 
            className="preview-button"
            onClick={() => setShowTable(!showTable)}
          >
            {showTable ? '隐藏数据预览' : '显示数据预览'}
          </button>
          
          {/* 悬浮可拖动的表格 */}
          {showTable && (
            <div 
              className="floating-table-container"
              style={{
                left: `${dragPosition.x}px`,
                top: `${dragPosition.y}px`
              }}
              onMouseDown={handleMouseDown}
            >
              {/* 可拖动的标题栏 */}
              <div className="draggable-header">
                <span>数据预览表格 (拖动此处移动)</span>
                <button 
                  className="close-button"
                  onClick={() => setShowTable(false)}
                >
                  ×
                </button>
              </div>
              
              {/* 表格设置区域 */}
              <div className="table-controls">
                <label htmlFor="visible-rows">显示行数: </label>
                <select 
                  id="visible-rows" 
                  value={visibleRows} 
                  onChange={handleVisibleRowsChange}
                >
                  <option value="5">5行</option>
                  <option value="10">10行</option>
                  <option value="20">20行</option>
                  <option value="50">50行</option>
                </select>
              </div>
              
              {/* 表格容器 */}
              <div 
                className="table-container"
                ref={tableContainerRef}
              >
                <table className="data-table">
                  <thead>
                    <tr>
                      {previewData.columns.map((col: string, index: number) => (
                        <th key={index}>{col}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {previewData.preview_data.slice(0, visibleRows).map((row: any, rowIndex: number) => (
                      <tr key={rowIndex}>
                        {previewData.columns.map((col: string, colIndex: number) => (
                          <td key={colIndex}>{row[col]}</td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              
              <div className="table-footer">
                <p>显示 {Math.min(visibleRows, previewData.preview_data.length)} 行，共 {previewData.preview_data.length} 行</p>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default DataPreviewModule;