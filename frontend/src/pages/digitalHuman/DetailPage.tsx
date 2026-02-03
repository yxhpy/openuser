import { useEffect } from 'react';
import {
  Card,
  Descriptions,
  Button,
  Typography,
  Spin,
  message,
  Image,
  Space,
} from 'antd';
import {
  PlayCircleOutlined,
  EditOutlined,
  DeleteOutlined,
  ArrowLeftOutlined,
} from '@ant-design/icons';
import { useNavigate, useParams } from 'react-router-dom';
import { useDigitalHumanStore } from '../../store/digitalHumanStore';

const { Title } = Typography;

export const DigitalHumanDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const {
    currentDigitalHuman,
    loading,
    error,
    fetchDigitalHuman,
    deleteDigitalHuman,
    clearError,
  } = useDigitalHumanStore();

  useEffect(() => {
    if (id) {
      fetchDigitalHuman(parseInt(id));
    }
  }, [id, fetchDigitalHuman]);

  useEffect(() => {
    if (error) {
      message.error(error);
      clearError();
    }
  }, [error, clearError]);

  const handleDelete = async () => {
    if (!currentDigitalHuman) return;

    try {
      await deleteDigitalHuman(currentDigitalHuman.id);
      message.success('Digital human deleted successfully');
      navigate('/digital-humans');
    } catch (err) {
      // Error handled by store
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px 0' }}>
        <Spin size="large" />
      </div>
    );
  }

  if (!currentDigitalHuman) {
    return (
      <div>
        <Title level={2}>Digital Human Not Found</Title>
        <Button onClick={() => navigate('/digital-humans')}>
          Back to List
        </Button>
      </div>
    );
  }

  return (
    <div>
      <Button
        icon={<ArrowLeftOutlined />}
        onClick={() => navigate('/digital-humans')}
        style={{ marginBottom: 16 }}
      >
        Back to List
      </Button>

      <Card>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
          <Title level={2} style={{ margin: 0 }}>
            {currentDigitalHuman.name}
          </Title>
          <Space>
            <Button
              type="primary"
              icon={<PlayCircleOutlined />}
              onClick={() => navigate(`/digital-humans/${currentDigitalHuman.id}/generate`)}
            >
              Generate Video
            </Button>
            <Button
              icon={<EditOutlined />}
              onClick={() => message.info('Edit functionality coming soon')}
            >
              Edit
            </Button>
            <Button
              danger
              icon={<DeleteOutlined />}
              onClick={handleDelete}
              loading={loading}
            >
              Delete
            </Button>
          </Space>
        </div>

        {currentDigitalHuman.image_path && (
          <div style={{ marginBottom: 24, textAlign: 'center' }}>
            <Image
              src={currentDigitalHuman.image_path}
              alt={currentDigitalHuman.name}
              style={{ maxWidth: 400, maxHeight: 400 }}
            />
          </div>
        )}

        <Descriptions bordered column={1}>
          <Descriptions.Item label="ID">
            {currentDigitalHuman.id}
          </Descriptions.Item>
          <Descriptions.Item label="Name">
            {currentDigitalHuman.name}
          </Descriptions.Item>
          <Descriptions.Item label="Description">
            {currentDigitalHuman.description || 'No description'}
          </Descriptions.Item>
          <Descriptions.Item label="Status">
            {currentDigitalHuman.is_active ? 'Active' : 'Inactive'}
          </Descriptions.Item>
          <Descriptions.Item label="Image Path">
            {currentDigitalHuman.image_path || 'No image'}
          </Descriptions.Item>
          <Descriptions.Item label="Voice Model Path">
            {currentDigitalHuman.voice_model_path || 'No voice model'}
          </Descriptions.Item>
          <Descriptions.Item label="Video Path">
            {currentDigitalHuman.video_path || 'No video'}
          </Descriptions.Item>
          <Descriptions.Item label="Created At">
            {new Date(currentDigitalHuman.created_at).toLocaleString()}
          </Descriptions.Item>
          <Descriptions.Item label="Updated At">
            {new Date(currentDigitalHuman.updated_at).toLocaleString()}
          </Descriptions.Item>
        </Descriptions>
      </Card>
    </div>
  );
};
