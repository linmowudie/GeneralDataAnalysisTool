import { useState } from 'react';
import * as api from '../services/api';
import type { AnalysisParameters, CleaningParameters, VisualizationParameters, DatabaseImportParameters } from '../types';

export function useDataAnalysis() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const runAnalysis = async (
    sessionId: string,
    modelType: string,
    parameters: AnalysisParameters
  ) => {
    setLoading(true);
    setError(null);
    try {
      const result = await api.runAnalysis(sessionId, modelType, parameters);
      return result;
    } catch (err) {
      setError((err as Error).message || '数据分析执行失败');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const cleanData = async (
    sessionId: string,
    mode: string,
    isCustom: boolean = false,
    parameters: CleaningParameters = {},
    targetCol?: string
  ) => {
    setLoading(true);
    setError(null);
    try {
      const result = await api.cleanData(sessionId, mode, isCustom, parameters, targetCol);
      return result;
    } catch (err) {
      setError((err as Error).message || '数据清洗执行失败');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const generateChart = async (
    sessionId: string,
    chartType: string,
    parameters: VisualizationParameters
  ) => {
    setLoading(true);
    setError(null);
    try {
      const result = await api.generateChart(sessionId, chartType, parameters);
      return result;
    } catch (err) {
      setError((err as Error).message || '图表生成失败');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const importFromDatabase = async (
    sessionId: string,
    params: DatabaseImportParameters
  ) => {
    setLoading(true);
    setError(null);
    try {
      const result = await api.importFromDatabase(
        sessionId,
        params.db_type,
        params.host,
        params.port,
        params.database,
        params.table,
        params.username,
        params.password
      );
      return result;
    } catch (err) {
      setError((err as Error).message || '数据库导入失败');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return {
    loading,
    error,
    runAnalysis,
    cleanData,
    generateChart,
    importFromDatabase
  };
}