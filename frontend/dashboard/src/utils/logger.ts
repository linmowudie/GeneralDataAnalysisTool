// 前端日志工具

class FrontendLogger {
  private logs: string[] = [];
  private logFileName: string;

  constructor(logFileName: string = 'frontend.log') {
    this.logFileName = logFileName;
    this.info('前端日志系统初始化');
  }

  private formatLog(level: string, message: string, details?: any): string {
    const timestamp = new Date().toISOString();
    const logEntry = `[${timestamp}] [${level}] ${message}`;
    
    if (details) {
      return `${logEntry} ${JSON.stringify(details)}`;
    }
    
    return logEntry;
  }

  private addToLogs(logEntry: string) {
    this.logs.push(logEntry);
    // 限制日志数量，避免占用过多内存
    if (this.logs.length > 1000) {
      this.logs.shift();
    }
  }

  info(message: string, details?: any) {
    const logEntry = this.formatLog('INFO', message, details);
    console.log(logEntry);
    this.addToLogs(logEntry);
  }

  warn(message: string, details?: any) {
    const logEntry = this.formatLog('WARN', message, details);
    console.warn(logEntry);
    this.addToLogs(logEntry);
  }

  error(message: string, details?: any) {
    const logEntry = this.formatLog('ERROR', message, details);
    console.error(logEntry);
    this.addToLogs(logEntry);
  }

  debug(message: string, details?: any) {
    const logEntry = this.formatLog('DEBUG', message, details);
    console.debug(logEntry);
    this.addToLogs(logEntry);
  }

  // 获取所有日志
  getLogs(): string[] {
    return [...this.logs];
  }

  // 清除日志
  clearLogs() {
    this.logs = [];
  }

  // 将日志保存到文件（在支持的环境中）
  saveLogsToFile() {
    try {
      const logContent = this.logs.join('\n');
      const blob = new Blob([logContent], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      
      const a = document.createElement('a');
      a.href = url;
      a.download = this.logFileName;
      document.body.appendChild(a);
      a.click();
      
      // 清理
      setTimeout(() => {
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      }, 0);
    } catch (error) {
      console.error('保存日志文件失败:', error);
    }
  }
}

// 创建全局前端日志实例
const frontendLogger = new FrontendLogger('frontend.log');

export default frontendLogger;