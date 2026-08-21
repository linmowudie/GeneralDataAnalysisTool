import { apiService } from './apiService';

/**
 * 文档读取服务
 * 对应后端的document_reader.py
 */
export class DocumentReaderService {
  /**
   * 读取项目文档
   * @returns Promise<string> HTML格式的文档内容
   */
  async readProjectDocs(): Promise<string> {
    try {
      const response = await apiService.get('/api/docs/project');
      // 注意：实际实现需要根据后端API的返回格式进行调整
      // 这里假设后端返回的是HTML内容字符串
      return typeof response === 'string' ? response : '';
    } catch (error) {
      console.error('读取项目文档失败:', error);
      return '<h1>文档未找到</h1><p>无法加载项目文档。</p>';
    }
  }

  /**
   * 读取技术文档
   * @param file 文件路径（可选）
   * @returns Promise<string> HTML格式的文档内容
   */
  async readTechnicalDocs(file?: string): Promise<string> {
    try {
      const params: Record<string, string> = {};
      if (file) {
        params.file = file;
      }

      const response = await apiService.get('/api/docs/technical', params);
      // 注意：实际实现需要根据后端API的返回格式进行调整
      // 这里假设后端返回的是HTML内容字符串
      return typeof response === 'string' ? response : '';
    } catch (error) {
      console.error('读取技术文档失败:', error);
      return '<h1>文档未找到</h1><p>无法加载技术文档。</p>';
    }
  }

  /**
   * 获取常用技术文档列表
   * @returns Array<{name: string, path: string}> 文档列表
   */
  getCommonTechnicalDocs(): Array<{name: string, path: string}> {
    return [
      { name: 'API文档', path: 'API文档.md' },
      { name: '数据分析模块接口', path: 'ModuleInterfaces/数据分析.md' },
      { name: '数据可视化模块接口', path: 'ModuleInterfaces/数据可视化.md' },
      { name: '数据导入模块接口', path: 'ModuleInterfaces/数据导入.md' },
      { name: '数据清洗模块接口', path: 'ModuleInterfaces/数据清洗.md' },
      { name: '数据报表模块接口', path: 'ModuleInterfaces/数据报表.md' },
      { name: '核心处理模块接口', path: 'ModuleInterfaces/核心处理.md' },
      { name: '会话管理模块接口', path: 'ModuleInterfaces/会话管理.md' }
    ];
  }

  /**
   * 提取文档标题
   * @param htmlContent HTML内容
   * @returns string 文档标题
   */
  extractDocumentTitle(htmlContent: string): string {
    const titleMatch = htmlContent.match(/<h1[^>]*>(.*?)<\/h1>/i);
    if (titleMatch && titleMatch[1]) {
      return titleMatch[1].replace(/<[^>]*>/g, ''); // 移除HTML标签
    }
    return '文档标题';
  }
}

// 创建全局文档读取服务实例
export const documentReaderService = new DocumentReaderService();