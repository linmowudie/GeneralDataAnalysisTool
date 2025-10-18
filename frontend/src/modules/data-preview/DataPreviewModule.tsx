import React, { useState, useEffect, useContext, useRef } from 'react';
import './DataPreviewModule.css';
import { dataPreviewService } from '../../services/dataPreviewService';
import { sessionService } from '../../services/sessionService';

// 添加消息的函数类型定义
type AddMessageType = (message: string, type?: 'info' | 'success' | 'warning' | 'error') => void;

// 创建 Context 用于传递 addMessage 函数
export const MessageContext = React.createContext<AddMessageType | null>(null);

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
  
  // 模拟数据用于测试表格滚动
  const mockData = {
    columns: [
      'id', 'name', 'age', 'gender', 'email', 'phone', 
      'address', 'city', 'state', 'country', 'postal_code',
      'occupation', 'income', 'education', 'marital_status',
      'children', 'height', 'weight', 'blood_type', 'allergies'
    ],
    preview_data: Array(20).fill(0).map((_, index) => ({
      'id': index + 1,
      'name': `测试用户${index + 1}`,
      'age': Math.floor(Math.random() * 50) + 20,
      'gender': ['男', '女'][Math.floor(Math.random() * 2)],
      'email': `test${index + 1}@example.com`,
      'phone': `1380000000${index}`,
      'address': `测试地址${index + 1}号`,
      'city': '测试城市',
      'state': '测试省份',
      'country': '中国',
      'postal_code': '100000',
      'occupation': '工程师',
      'income': Math.floor(Math.random() * 20000) + 5000,
      'education': ['本科', '硕士', '博士'][Math.floor(Math.random() * 3)],
      'marital_status': ['已婚', '未婚'][Math.floor(Math.random() * 2)],
      'children': Math.floor(Math.random() * 3),
      'height': Math.floor(Math.random() * 40) + 160,
      'weight': Math.floor(Math.random() * 30) + 50,
      'blood_type': ['A', 'B', 'O', 'AB'][Math.floor(Math.random() * 4)],
      'allergies': ['无', '花粉', '海鲜', '药物'][Math.floor(Math.random() * 4)]
    })),
    file_name: 'test_dataset.csv',
    total_rows: 1000,
    total_columns: 20
  };

  // 处理鼠标滚轮事件，将垂直滚动转换为水平滚动
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
  
  // 处理鼠标按下事件，开始拖动
  const handleMouseDown = (e: React.MouseEvent) => {
    if (e.target instanceof HTMLDivElement && e.target.className.includes('draggable-header')) {
      setIsDragging(true);
      setStartDrag({
        x: e.clientX - dragPosition.x,
        y: e.clientY - dragPosition.y
      });
    }
  };
  
  // 处理鼠标移动事件，更新拖动位置
  const handleMouseMove = (e: MouseEvent) => {
    if (isDragging) {
      setDragPosition({
        x: e.clientX - startDrag.x,
        y: e.clientY - startDrag.y
      });
    }
  };
  
  // 处理鼠标释放事件，结束拖动
  const handleMouseUp = () => {
    setIsDragging(false);
  };
  
  // 添加全局鼠标事件监听器
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
  
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // 使用模拟数据进行测试，避免依赖会话ID
        // 实际使用时可以取消下面的注释，使用真实API
        /*
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
        */
        
        // 使用模拟数据
        setTimeout(() => {
          setPreviewData(mockData);
          setDatasetInfo({
            dataset_name: 'test_dataset.csv',
            total_records: 1000,
            features_count: 19,
            target_variable: 'income'
          });
          setLoading(false);
        }, 500);
        
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : '获取数据失败';
        setError(errorMessage);
        console.error('获取数据预览失败:', err);
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const handleVisibleRowsChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setVisibleRows(Number(e.target.value));
  };

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