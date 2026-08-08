import React, { useCallback, useEffect, useState } from 'react';
import { Table, Button, Spin, message } from 'antd';
import { ReloadOutlined, RightOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { PageHeader, StatCard } from '../../components/common/Common';
import { useSession } from '../../context/SessionContext';
import { dataPreviewService } from '../../services/dataPreviewService';
import './DataPreviewModule.css';

const DataPreviewModule: React.FC = () => {
  const navigate = useNavigate();
  const { refreshStatus, ready } = useSession();
  const [loading, setLoading] = useState(false);
  const [preview, setPreview] = useState<any>(null);
  const [info, setInfo] = useState<any>(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [p, i] = await Promise.all([
        dataPreviewService.getDataPreview(),
        dataPreviewService.getDatasetInfo(),
      ]);
      setPreview(p);
      setInfo(i);
      await refreshStatus();
    } catch (e: any) {
      message.error(`加载失败：${e?.message || e}`);
    } finally {
      setLoading(false);
    }
  }, [refreshStatus]);

  useEffect(() => { if (ready) load(); }, [load, ready]);

  const columns: string[] = preview?.columns || [];
  const tableColumns = columns.map((col) => ({
    title: col,
    dataIndex: col,
    key: col,
    ellipsis: true,
    width: 140,
    render: (v: any) => (v === null || v === undefined ? <span className="df-null">null</span> : String(v)),
  }));

  const fieldData = info?.data_types
    ? Object.entries(info.data_types).map(([name, dtype]) => ({ name, dtype: dtype as string }))
    : [];

  const tableData = (preview?.preview_data || []).map((row: any, idx: number) => ({ ...row, _rowKey: idx }));

  return (
    <div className="df-page">
      <PageHeader
        eyebrow="STEP 02 · PREVIEW"
        title={<>数据<span className="df-lime-chip">预览</span></>}
        description="查看当前会话数据集的规模、字段类型与前几行样本数据。"
        extra={
          <>
            <Button icon={<ReloadOutlined />} onClick={load} loading={loading}>刷新</Button>
            <Button type="primary" onClick={() => navigate('/cleaning')}>
              下一步：清洗 <RightOutlined />
            </Button>
          </>
        }
      />

      <Spin spinning={loading}>
        <div className="df-grid-4">
          <StatCard label="记录数" value={preview?.total_rows ?? '—'} accent="lime" hint={preview?.file_name || '数据集'} />
          <StatCard label="字段数" value={preview?.total_columns ?? '—'} accent="violet" hint={info?.dataset_name || '—'} />
          <StatCard label="特征数" value={info?.features_count ?? '—'} accent="pink" hint="排除目标列" />
          <StatCard label="目标变量" value={info?.target_variable ?? '—'} accent="violet" hint="末列默认目标" />
        </div>

        <div className="df-card df-card-lg df-preview-block">
          <div className="df-eyebrow df-card-eyebrow">SAMPLE DATA</div>
          <h3 className="df-card-title">样本数据（前 5 行）</h3>
          <Table
            size="small"
            rowKey="_rowKey"
            columns={tableColumns}
            dataSource={tableData}
            pagination={false}
            scroll={{ x: 'max-content' }}
          />
        </div>

        <div className="df-card df-card-lg">
          <div className="df-eyebrow df-card-eyebrow">SCHEMA</div>
          <h3 className="df-card-title">字段信息</h3>
          <Table
            size="small"
            rowKey="name"
            pagination={false}
            dataSource={fieldData}
            columns={[
              { title: '字段名', dataIndex: 'name', key: 'name' },
              {
                title: '数据类型', dataIndex: 'dtype', key: 'dtype',
                render: (v: string) => <span className="df-pill df-code">{dataPreviewService.formatDataType(v)}</span>,
              },
            ]}
          />
        </div>
      </Spin>
    </div>
  );
};

export default DataPreviewModule;
