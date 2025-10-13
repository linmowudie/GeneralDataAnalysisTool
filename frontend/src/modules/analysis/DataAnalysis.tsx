import React, { useState, useRef, useEffect } from 'react';
import './DataAnalysis.css';

interface DataAnalysisProps {
  onTabChange: (tab: 'dashboard' | 'analysis' | 'visualization') => void;
}

const DataAnalysis: React.FC<DataAnalysisProps> = ({ onTabChange }) => {
  const [panelHeights, setPanelHeights] = useState<{ top: string; bottom: string }>({ top: '50%', bottom: '50%' });
  const [isDragging, setIsDragging] = useState(false);
  const [activeStep, setActiveStep] = useState<'import' | 'preview' | 'cleaning' | 'analysis' | 'visualization' | 'report'>('analysis');
  const dividerRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!isDragging || !containerRef.current) return;
      
      const containerRect = containerRef.current.getBoundingClientRect();
      const y = e.clientY - containerRect.top;
      const containerHeight = containerRect.height;
      
      // 计算百分比，限制在10%到90%之间
      const percentage = Math.min(Math.max((y / containerHeight) * 100, 10), 90);
      
      setPanelHeights({
        top: `${percentage}%`,
        bottom: `${100 - percentage}%`
      });
    };

    const handleMouseUp = () => {
      setIsDragging(false);
    };

    if (isDragging) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isDragging]);

  const handleMouseDown = (e: React.MouseEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleStepChange = (step: 'import' | 'preview' | 'cleaning' | 'analysis' | 'visualization' | 'report') => {
    setActiveStep(step);
  };

  const renderParameterContent = () => {
    switch (activeStep) {
      case 'import':
        return <div>数据导入参数设置区域</div>;
      case 'preview':
        return <div>数据预览控制区域</div>;
      case 'cleaning':
        return <div>数据清洗参数设置区域</div>;
      case 'analysis':
        return <div>数据分析参数设置区域</div>;
      case 'visualization':
        return <div>可视化参数设置区域</div>;
      case 'report':
        return <div>报表生成参数设置区域</div>;
      default:
        return <div>请选择一个操作步骤</div>;
    }
  };

  const renderResultContent = () => {
    switch (activeStep) {
      case 'import':
        return <div>数据导入结果展示区域</div>;
      case 'preview':
        return <div>数据预览结果展示区域</div>;
      case 'cleaning':
        return <div>数据清洗结果展示区域</div>;
      case 'analysis':
        return <div>数据分析结果展示区域</div>;
      case 'visualization':
        return <div>可视化结果展示区域</div>;
      case 'report':
        return <div>报表生成结果展示区域</div>;
      default:
        return <div>请先选择一个操作步骤</div>;
    }
  };

  return (
    <div className="data-analysis-container">
      <div className="analysis-header">
        <h2>通用数据分析工具</h2>
        <div className="analysis-tabs">
          <button className="tab-button" onClick={() => onTabChange('dashboard')}>仪表盘</button>
          <button className="tab-button active" onClick={() => onTabChange('analysis')}>数据分析</button>
          <button className="tab-button" onClick={() => onTabChange('visualization')}>绘图</button>
        </div>
      </div>
      
      <div className="analysis-content">
        <div className="left-panel">
          <div className="process-step">
            <button 
              className={`step-button ${activeStep === 'import' ? 'active' : ''}`}
              onClick={() => handleStepChange('import')}
            >
              导入
            </button>
            <div className={`step-indicator ${activeStep === 'import' ? 'active' : ''}`}></div>
          </div>
          <div className="process-step">
            <button 
              className={`step-button ${activeStep === 'preview' ? 'active' : ''}`}
              onClick={() => handleStepChange('preview')}
            >
              预览
            </button>
            <div className={`step-indicator ${activeStep === 'preview' ? 'active' : ''}`}></div>
          </div>
          <div className="process-step">
            <button 
              className={`step-button ${activeStep === 'cleaning' ? 'active' : ''}`}
              onClick={() => handleStepChange('cleaning')}
            >
              清洗
            </button>
            <div className={`step-indicator ${activeStep === 'cleaning' ? 'active' : ''}`}></div>
          </div>
          <div className="process-step">
            <button 
              className={`step-button ${activeStep === 'analysis' ? 'active' : ''}`}
              onClick={() => handleStepChange('analysis')}
            >
              分析
            </button>
            <div className={`step-indicator ${activeStep === 'analysis' ? 'active' : ''}`}></div>
          </div>
          <div className="process-step">
            <button 
              className={`step-button ${activeStep === 'visualization' ? 'active' : ''}`}
              onClick={() => handleStepChange('visualization')}
            >
              可视化
            </button>
            <div className={`step-indicator ${activeStep === 'visualization' ? 'active' : ''}`}></div>
          </div>
          <div className="process-step">
            <button 
              className={`step-button ${activeStep === 'report' ? 'active' : ''}`}
              onClick={() => handleStepChange('report')}
            >
              报表
            </button>
            <div className={`step-indicator ${activeStep === 'report' ? 'active' : ''}`}></div>
          </div>
        </div>
        
        <div className="center-panel" ref={containerRef}>
          <div 
            className="parameter-panel" 
            style={{ height: panelHeights.top }}
          >
            <h3>参数输入及控制面板</h3>
            <div className="parameter-content">
              {renderParameterContent()}
            </div>
          </div>
          
          <div 
            className="draggable-divider" 
            ref={dividerRef}
            onMouseDown={handleMouseDown}
          ></div>
          
          <div 
            className="result-panel" 
            style={{ height: panelHeights.bottom }}
          >
            <h3>分析结果展示</h3>
            <div className="result-content">
              {renderResultContent()}
            </div>
          </div>
        </div>
        
        <div className="right-panel">
          <div className="message-panel">
            <h3>消息返回</h3>
            {/* 系统消息将在这里显示 */}
          </div>
          <div className="control-buttons">
            <button className="control-btn">清空</button>
            <button className="control-btn">重置</button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DataAnalysis;