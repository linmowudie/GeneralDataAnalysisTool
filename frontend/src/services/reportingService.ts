import { apiService } from './apiService';
import { sessionService } from './sessionService';

/**
 * 报告生成服务
 */
export class ReportingService {
  /**
   * 生成分析报告
   * @param reportType 报告类型
   * @param sessionId 会话ID（可选，如果不提供则使用当前会话ID）
   * @returns Promise<any> 报告生成结果
   */
  async generateReport(
    reportType: string = 'full',
    sessionId?: string
  ): Promise<any> {
    try {
      const targetSessionId = sessionId || sessionService.getCurrentSessionId();
      if (!targetSessionId) {
        throw new Error('没有可用的会话ID，请先创建会话');
      }

      const response = await apiService.post('/api/reporting/generate?session_id=' + targetSessionId + '&report_type=' + reportType);
      return response;
    } catch (error) {
      console.error('生成报告失败:', error);
      throw error;
    }
  }

  /**
   * 导出报告
   * @param reportId 报告ID
   * @param format 导出格式（pdf/excel/html）
   * @returns Promise<Blob> 报告文件Blob
   */
  async exportReport(
    reportId: string,
    format: 'pdf' | 'excel' | 'html' = 'pdf'
  ): Promise<Blob> {
    try {
      const response = await apiService.get(`/api/reporting/export/${reportId}`, {
        params: { format }
      });
      return response as Blob;
    } catch (error) {
      console.error('导出报告失败:', error);
      throw error;
    }
  }

  /**
   * 获取可用的报告模板
   * @returns Promise<any[]> 报告模板列表
   */
  async getReportTemplates(): Promise<any[]> {
    try {
      const response: any = await apiService.get('/api/reporting/templates');
      return response.templates || [];
    } catch (error) {
      console.error('获取报告模板失败:', error);
      // 返回默认模板列表作为备选
      return [
        { id: 'full', name: '完整报告', description: '包含所有分析结果和可视化图表的详细报告' },
        { id: 'summary', name: '摘要报告', description: '只包含关键发现和主要图表的简短报告' },
        { id: 'technical', name: '技术报告', description: '面向技术人员的详细分析报告' },
        { id: 'executive', name: '执行摘要', description: '面向管理层的简洁报告' }
      ];
    }
  }

  /**
   * 保存报告配置
   * @param config 报告配置信息
   * @returns Promise<any> 保存结果
   */
  async saveReportConfig(config: Record<string, any>): Promise<any> {
    try {
      const response = await apiService.post('/api/reporting/save-config', config);
      return response;
    } catch (error) {
      console.error('保存报告配置失败:', error);
      throw error;
    }
  }

  /**
   * 下载报告文件
   * @param blob 文件Blob数据
   * @param filename 文件名
   */
  downloadReport(blob: Blob, filename: string): void {
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }
}

// 创建全局报告生成服务实例
export const reportingService = new ReportingService();