import { useState, useEffect } from 'react';
import * as api from '../services/api';

export interface DataPreview {
  success: boolean;
  file_name: string;
  total_rows: number;
  total_columns: number;
  columns: string[];
  preview_data: Record<string, any>[];
  [key: string]: any;
}

export interface DatasetInfo {
  dataset_name: string;
  total_records: number;
  features_count: number;
  target_variable: string;
  data_types: Record<string, string>;
  [key: string]: any;
}

export function useDataPreview(sessionId: string | null) {
  const [dataPreview, setDataPreview] = useState<DataPreview | null>(null);
  const [datasetInfo, setDatasetInfo] = useState<DatasetInfo | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchDataPreview = async () => {
    if (!sessionId) {
      setError('会话未创建');
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const previewData = await api.getDataPreview(sessionId);
      setDataPreview(previewData);
      
      const infoData = await api.getDatasetInfo(sessionId);
      setDatasetInfo(infoData);
    } catch (err) {
      setError('获取数据预览失败: ' + (err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (sessionId) {
      fetchDataPreview();
    }
  }, [sessionId]);

  return { dataPreview, datasetInfo, loading, error, refetch: fetchDataPreview };
}