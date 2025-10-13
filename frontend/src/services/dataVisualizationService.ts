import { apiService } from './apiService';
import { sessionService } from './sessionService';

/**
 * 数据可视化服务
 * 对应后端的data_visualization.py
 */
export class DataVisualizationService {
  /**
   * 生成图表
   * @param chartType 图表类型
   * @param parameters 图表参数
   * @param sessionId 会话ID（可选，如果不提供则使用当前会话ID）
   * @returns Promise<any> 图表数据
   */
  async generateChart(
    chartType: string,
    parameters: Record<string, any> = {},
    sessionId?: string
  ): Promise<any> {
    try {
      const targetSessionId = sessionId || sessionService.getCurrentSessionId();
      if (!targetSessionId) {
        throw new Error('没有可用的会话ID，请先创建会话');
      }

      const formData = new FormData();
      formData.append('session_id', targetSessionId);
      formData.append('chart_type', chartType);
      formData.append('parameters', JSON.stringify(parameters));

      const response = await apiService.upload('/api/visualization/generate-chart', formData);
      return response;
    } catch (error) {
      console.error('图表生成失败:', error);
      throw error;
    }
  }

  /**
   * 获取可用的图表类型
   * @returns Promise<string[]> 图表类型列表
   */
  async getAvailableCharts(): Promise<string[]> {
    try {
      const response: any = await apiService.get('/api/visualization/available-charts');
      return response.chart_types || [];
    } catch (error) {
      console.error('获取图表类型失败:', error);
      // 返回默认图表类型作为备选
      return ['scatter', 'line', 'bar', 'histogram', 'box', 'violin'];
    }
  }

  /**
   * 获取图表类型的描述
   * @returns Record<string, string> 图表名称和描述的映射
   */
  getChartTypeDescriptions(): Record<string, string> {
    return {
      'scatter': '散点图 - 展示两个变量之间的关系',
      'line': '折线图 - 展示数据随时间变化的趋势',
      'bar': '柱状图 - 比较不同类别的数据',
      'histogram': '直方图 - 展示数据的分布情况',
      'box': '箱线图 - 展示数据的分布特征和异常值',
      'violin': '小提琴图 - 结合箱线图和密度图的特征'
    };
  }

  /**
   * 根据任务类型获取推荐的图表类型
   * @param taskType 任务类型（classification/regression/clustering）
   * @returns string[] 推荐的图表类型列表
   */
  getRecommendedChartsForTask(taskType: string): string[] {
    const recommendations: Record<string, string[]> = {
      'classification': ['bar', 'scatter', 'histogram'],
      'regression': ['line', 'scatter', 'residual'],
      'clustering': ['scatter', 'bar', 'box']
    };
    
    return recommendations[taskType] || ['scatter', 'bar', 'line'];
  }
}

// 创建全局数据可视化服务实例
export const dataVisualizationService = new DataVisualizationService();