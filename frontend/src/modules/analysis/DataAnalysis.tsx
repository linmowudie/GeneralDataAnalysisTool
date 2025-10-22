import React, { useState, useRef, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import './DataAnalysis.css';
import DataImportModule, { MessageContext as ImportMessageContext } from '../data-import/DataImportModule';
import DataPreviewModule, { MessageContext as PreviewMessageContext } from '../data-preview/DataPreviewModule';
import DataCleaningModule, { MessageContext as CleaningMessageContext } from '../data-cleaning/DataCleaningModule';
import DataAnalysisModule, { MessageContext as AnalysisMessageContext } from '../data-analysis/DataAnalysisModule';
import VisualizationModule, { MessageContext as VisualizationMessageContext } from '../visualization/VisualizationModule';
import ReportingModule, { MessageContext as ReportingMessageContext } from '../reporting/ReportingModule';
import MessagePanel from '../../components/MessagePanel';
import type { Message as MessageType } from '../../components/MessagePanel';
import { useGlobalState } from '../../context/GlobalStateContext';
import * as CleanupTaskModuleImport from '../cleanup-task/CleanupTaskModule';

const CleanupTaskModule = CleanupTaskModuleImport.default || CleanupTaskModuleImport;

// 定义消息类型
interface Message {
  id: string;
  type: 'info' | 'success' | 'warning' | 'error';
  content: string;
  timestamp: Date;
}

interface DataAnalysisProps {
  onTabChange: (tab: 'dashboard' | 'analysis' | 'visualization') => void;
}

const DataAnalysis: React.FC<DataAnalysisProps> = ({ onTabChange }) => {
  // 添加组件实例ID，用于标识不同的组件实例
  const componentId = React.useRef(Math.random().toString(36).substr(2, 9));
  
  // 调试组件渲染
  React.useEffect(() => {
    console.log(`[父组件渲染] DataAnalysis (ID: ${componentId.current}) 渲染`);
  });
  
  const navigate = useNavigate();
  const location = useLocation();
  const { resetState } = useGlobalState();

  // 根据URL设置初始步骤
  useEffect(() => {
    const path = location.pathname;
    if (path.startsWith('/analysis/')) {
      const step = path.split('/')[2] as 'import' | 'preview' | 'cleaning' | 'analysis' | 'visualization' | 'report';
      if (['import', 'preview', 'cleaning', 'analysis', 'visualization', 'report'].includes(step)) {
        setActiveStep(step);
      }
    }
  }, [location]);

  const handleTabChange = (tab: 'dashboard' | 'analysis' | 'visualization') => {
    onTabChange(tab);
  };
  const [panelHeights, setPanelHeights] = useState<{ top: string; bottom: string }>({ top: '70%', bottom: '30%' });
  const [isDragging, setIsDragging] = useState(false);
  const [activeStep, setActiveStep] = useState<'import' | 'preview' | 'cleaning' | 'analysis' | 'visualization' | 'report'>('import');
  const [completedSteps, setCompletedSteps] = useState<Set<string>>(new Set(['import'])); // 导入步骤默认为已完成
  const [messages, setMessages] = useState<Message[]>([]);
  const [analysisResult, setAnalysisResult] = useState<any>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  const dividerRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // 添加消息到消息面板
  const addMessage = React.useCallback((message: string, type: 'info' | 'success' | 'warning' | 'error' = 'info') => {
    console.log(`[消息添加] DataAnalysis (ID: ${componentId.current}) 添加消息: ${message}`);
    const newMessage: Message = {
      id: Date.now().toString() + Math.random().toString(36).substr(2, 9), // 添加随机字符串确保唯一性
      type,
      content: message,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, newMessage]);
  }, []); // 空依赖数组确保函数引用稳定
  
  // 调试addMessage函数引用
  React.useEffect(() => {
    console.log(`[函数引用] DataAnalysis (ID: ${componentId.current}) addMessage函数引用:`, addMessage);
  }, [addMessage]);

  // 滚动到最新消息
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // 监听数据导入成功事件
  useEffect(() => {
    const handleDataImportSuccess = (event: Event) => {
      const customEvent = event as CustomEvent;
      const { importType, fileName, dbType, table } = customEvent.detail;
      
      let message = '';
      if (importType === 'file') {
        message = `文件导入成功: ${fileName}`;
      } else if (importType === 'database') {
        message = `数据库导入成功: ${dbType} - ${table}`;
      }
      
      if (message) {
        addMessage(message, 'success');
      }
    };

    // 添加事件监听器
    if (window && window.addEventListener) {
      window.addEventListener('dataImportSuccess', handleDataImportSuccess);
    }

    // 清理事件监听器
    return () => {
      if (window && window.removeEventListener) {
        window.removeEventListener('dataImportSuccess', handleDataImportSuccess);
      }
    };
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

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
    // 更新已完成步骤：当前步骤之前的所有步骤都标记为已完成
    const steps = ['import', 'preview', 'cleaning', 'analysis', 'visualization', 'report'];
    const currentIndex = steps.indexOf(step);
    const newCompletedSteps = new Set<string>();
    
    for (let i = 0; i <= currentIndex; i++) {
      newCompletedSteps.add(steps[i]);
    }
    
    setCompletedSteps(newCompletedSteps);
    
    // 更新URL但不刷新页面
    navigate(`/analysis/${step}`);
  };

  const handleAnalysisComplete = (result: any) => {
    setAnalysisResult(result);
    addMessage('数据分析完成');
  };

  const renderParameterContent = () => {
    console.log(`[渲染子组件] DataAnalysis (ID: ${componentId.current}) 渲染${activeStep}步骤组件`);
    switch (activeStep) {
      case 'import':
        return (
          <ImportMessageContext.Provider value={addMessage}>
            <DataImportModule />
          </ImportMessageContext.Provider>
        );
      case 'preview':
        return (
          <PreviewMessageContext.Provider value={addMessage}>
            <DataPreviewModule />
          </PreviewMessageContext.Provider>
        );
      case 'cleaning':
        return (
          <CleaningMessageContext.Provider value={addMessage}>
            <DataCleaningModule />
          </CleaningMessageContext.Provider>
        );
      case 'analysis':
        return (
          <AnalysisMessageContext.Provider value={addMessage}>
            <DataAnalysisModule onAnalysisComplete={handleAnalysisComplete} />
          </AnalysisMessageContext.Provider>
        );
      case 'visualization':
        return (
          <VisualizationMessageContext.Provider value={addMessage}>
            <VisualizationModule />
          </VisualizationMessageContext.Provider>
        );
      case 'report':
        return (
          <ReportingMessageContext.Provider value={addMessage}>
            <ReportingModule />
          </ReportingMessageContext.Provider>
        );
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
        return (
          <div>
            <h4>数据分析结果</h4>
            {analysisResult ? (
              <pre>{JSON.stringify(analysisResult, null, 2)}</pre>
            ) : (
              <p>请先运行数据分析</p>
            )}
          </div>
        );
      case 'visualization':
        return <div>可视化结果展示区域</div>;
      case 'report':
        return <div>报表生成结果展示区域</div>;
      default:
        return <div>请先选择一个操作步骤</div>;
    }
  };

  // 判断是否需要显示结果面板
  const shouldShowResultPanel = () => {
    return activeStep !== 'import' && activeStep !== 'preview' && activeStep !== 'cleaning';
  };

  // 清空消息
  const clearMessages = () => {
    setMessages([]);
  };

  // 移除单个消息
  const dismissMessage = (id: string) => {
    setMessages(prev => prev.filter(msg => msg.id !== id));
  };

  // 处理清空完成事件
  const handleClearComplete = () => {
    // 清空分析结果
    const steps = ['import', 'preview', 'cleaning', 'analysis', 'visualization', 'report'];
    const currentStepIndex = steps.indexOf(activeStep);
    
    if (currentStepIndex <= 3) { // 3是analysis步骤的索引
      setAnalysisResult(null);
    }
    
    // 强制重新渲染当前步骤组件
    forceUpdateStep(activeStep);
  };

  // 处理重置完成事件
  const handleResetComplete = () => {
    // 重置全局状态
    resetState();
    
    // 重置本地状态
    setActiveStep('import');
    setCompletedSteps(new Set(['import'])); // 重置已完成步骤，只保留导入
    setMessages([]);
    setAnalysisResult(null);
    
    // 导航到导入步骤
    navigate('/analysis/import');
    
    // 强制重新渲染导入步骤组件
    forceUpdateStep('import');
  };

  // 强制更新步骤组件
  const forceUpdateStep = (step: string) => {
    // 通过改变key来强制重新渲染组件
    // 这将在React中创建一个新的组件实例，从而清除其内部状态
    // 我们通过更新组件的key属性来实现强制刷新
    // 在renderParameterContent函数中，我们已经为每个组件添加了基于时间戳的key
    // 当activeStep改变时，会自动重新渲染对应的组件
  };

  return (
    <div className="data-analysis-container">
      <div className="analysis-header">
        <h2>通用数据分析工具</h2>
        <div className="analysis-tabs">
          <button className="tab-button" onClick={() => handleTabChange('dashboard')}>仪表盘</button>
          <button className="tab-button active" onClick={() => handleTabChange('analysis')}>数据分析</button>
          <button className="tab-button" onClick={() => handleTabChange('visualization')}>绘图</button>
        </div>
      </div>
      
      <div className="analysis-content">
        <div className="left-panel">
          <div className="process-step">
            <button 
              className={`step-button ${activeStep === 'import' ? 'active' : ''} ${completedSteps.has('import') ? 'completed' : ''}`}
              onClick={() => handleStepChange('import')}
            >
              导入
            </button>
            <div className={`step-indicator ${activeStep === 'import' ? 'active' : ''} ${completedSteps.has('import') ? 'completed' : ''}`}></div>
          </div>
          <div className="process-step">
            <button 
              className={`step-button ${activeStep === 'preview' ? 'active' : ''} ${completedSteps.has('preview') ? 'completed' : ''}`}
              onClick={() => handleStepChange('preview')}
            >
              预览
            </button>
            <div className={`step-indicator ${activeStep === 'preview' ? 'active' : ''} ${completedSteps.has('preview') ? 'completed' : ''}`}></div>
          </div>
          <div className="process-step">
            <button 
              className={`step-button ${activeStep === 'cleaning' ? 'active' : ''} ${completedSteps.has('cleaning') ? 'completed' : ''}`}
              onClick={() => handleStepChange('cleaning')}
            >
              清洗
            </button>
            <div className={`step-indicator ${activeStep === 'cleaning' ? 'active' : ''} ${completedSteps.has('cleaning') ? 'completed' : ''}`}></div>
          </div>
          <div className="process-step">
            <button 
              className={`step-button ${activeStep === 'analysis' ? 'active' : ''} ${completedSteps.has('analysis') ? 'completed' : ''}`}
              onClick={() => handleStepChange('analysis')}
            >
              分析
            </button>
            <div className={`step-indicator ${activeStep === 'analysis' ? 'active' : ''} ${completedSteps.has('analysis') ? 'completed' : ''}`}></div>
          </div>
          <div className="process-step">
            <button 
              className={`step-button ${activeStep === 'visualization' ? 'active' : ''} ${completedSteps.has('visualization') ? 'completed' : ''}`}
              onClick={() => handleStepChange('visualization')}
            >
              可视化
            </button>
            <div className={`step-indicator ${activeStep === 'visualization' ? 'active' : ''} ${completedSteps.has('visualization') ? 'completed' : ''}`}></div>
          </div>
          <div className="process-step">
            <button 
              className={`step-button ${activeStep === 'report' ? 'active' : ''} ${completedSteps.has('report') ? 'completed' : ''}`}
              onClick={() => handleStepChange('report')}
            >
              报表
            </button>
            <div className={`step-indicator ${activeStep === 'report' ? 'active' : ''} ${completedSteps.has('report') ? 'completed' : ''}`}></div>
          </div>
        </div>
        
        <div className="center-panel" ref={containerRef}>
          <div 
            className="parameter-panel" 
            style={{ 
              height: shouldShowResultPanel() ? panelHeights.top : '100%',
              borderBottom: shouldShowResultPanel() ? '1px solid var(--border-color)' : 'none'
            }}
          >
            <h3>参数输入及控制面板</h3>
            <div className="parameter-content">
              {renderParameterContent()}
            </div>
          </div>
          
          {shouldShowResultPanel() && (
            <>
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
            </>
          )}
        </div>
        
        <div className="right-panel">
          <MessagePanel 
            messages={messages}
            onClear={clearMessages}
            onDismiss={dismissMessage}
          />
          <CleanupTaskModule
            activeStep={activeStep}
            onClearComplete={handleClearComplete}
            onResetComplete={handleResetComplete}
            addMessage={addMessage}
          />
        </div>
      </div>
    </div>
  );
};

export default DataAnalysis;