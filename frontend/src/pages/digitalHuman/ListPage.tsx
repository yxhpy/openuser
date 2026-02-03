import { useEffect, useState } from 'react';
import {
  Card,
  Row,
  Col,
  Button,
  Typography,
  Empty,
  Spin,
  message,
  Modal,
  Image,
} from 'antd';
import {
  PlusOutlined,
  UserOutlined,
  DeleteOutlined,
  PlayCircleOutlined,
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useDigitalHumanStore } from '../../store/digitalHumanStore';
import type { DigitalHuman } from '../../types/digitalHuman';

const { Title, Text, Paragraph } = Typography;

export const DigitalHumansListPage: React.FC = () => {
  const navigate = useNavigate();
  const {
    digitalHumans,
    loading,
    error,
    fetchDigitalHumans,
    deleteDigitalHuman,
    clearError,
  } = useDigitalHumanStore();

  const [deleteModalVisible, setDeleteModalVisible] = useState(false);
  const [selectedDigitalHuman, setSelectedDigitalHuman] =
    useState<DigitalHuman | null>(null);

  useEffect(() => {
    fetchDigitalHumans();
  }, [fetchDigitalHumans]);

  useEffect(() => {
    if (error) {
      message.error(error);
      clearError();
    }
  }, [error, clearError]);

  const handleDelete = async () => {
    if (!selectedDigitalHuman) return;

    try {
      await deleteDigitalHuman(selectedDigitalHuman.id);
      message.success('Digital human deleted successfully');
      setDeleteModalVisible(false);
      setSelectedDigitalHuman(null);
    } catch (err) {
      // Error handled by store
    }
  };

  const showDeleteModal = (digitalHuman: DigitalHuman) => {
    setSelectedDigitalHuman(digitalHuman);
    setDeleteModalVisible(true);
  };

  return (
    <div>
      <div style={{ marginBottom: 24, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Title level={2}>Digital Humans</Title>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={() => navigate('/digital-humans/create')}
        >
          Create Digital Human
        </Button>
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '50px 0' }}>
          <Spin size="large" />
        </div>
      ) : digitalHumans.length === 0 ? (
        <Empty
          description="No digital humans yet"
          image={Empty.PRESENTED_IMAGE_SIMPLE}
        >
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => navigate('/digital-humans/create')}
          >
            Create Your First Digital Human
          </Button>
        </Empty>
      ) : (
        <Row gutter={[16, 16]}>
          {digitalHumans.map((dh) => (
            <Col xs={24} sm={12} md={8} lg={6} key={dh.id}>
              <Card
                hoverable
                cover={
                  dh.image_path ? (
                    <Image
                      alt={dh.name}
                      src={dh.image_path}
                      style={{ height: 200, objectFit: 'cover' }}
                      preview={false}
                    />
                  ) : (
                    <div
                      style={{
                        height: 200,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        background: '#f0f0f0',
                      }}
                    >
                      <UserOutlined style={{ fontSize: 64, color: '#bfbfbf' }} />
                    </div>
                  )
                }
                actions={[
                  <Button
                    type="text"
                    icon={<PlayCircleOutlined />}
                    onClick={() => navigate(`/digital-humans/${dh.id}/generate`)}
                  >
                    Generate
                  </Button>,
                  <Button
                    type="text"
                    danger
                    icon={<DeleteOutlined />}
                    onClick={() => showDeleteModal(dh)}
                  >
                    Delete
                  </Button>,
                ]}
                onClick={() => navigate(`/digital-humans/${dh.id}`)}
              >
                <Card.Meta
                  title={dh.name}
                  description={
                    <div>
                      <Paragraph
                        ellipsis={{ rows: 2 }}
                        style={{ marginBottom: 8 }}
                      >
                        {dh.description || 'No description'}
                      </Paragraph>
                      <Text type="secondary" style={{ fontSize: 12 }}>
                        Created: {new Date(dh.created_at).toLocaleDateString()}
                      </Text>
                    </div>
                  }
                />
              </Card>
            </Col>
          ))}
        </Row>
      )}

      <Modal
        title="Delete Digital Human"
        open={deleteModalVisible}
        onOk={handleDelete}
        onCancel={() => {
          setDeleteModalVisible(false);
          setSelectedDigitalHuman(null);
        }}
        okText="Delete"
        okButtonProps={{ danger: true }}
        confirmLoading={loading}
      >
        <p>
          Are you sure you want to delete{' '}
          <strong>{selectedDigitalHuman?.name}</strong>? This action cannot be
          undone.
        </p>
      </Modal>
    </div>
  );
};
