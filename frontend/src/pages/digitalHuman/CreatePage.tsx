import { useState } from 'react';
import {
  Steps,
  Form,
  Input,
  Upload,
  Button,
  Card,
  message,
  Typography,
} from 'antd';
import {
  UserOutlined,
  PictureOutlined,
  CheckOutlined,
  UploadOutlined,
} from '@ant-design/icons';
import type { UploadFile } from 'antd';
import { useNavigate } from 'react-router-dom';
import { useDigitalHumanStore } from '../../store/digitalHumanStore';

const { Title, Paragraph } = Typography;
const { TextArea } = Input;

interface FormValues {
  name: string;
  description: string;
}

export const CreateDigitalHumanPage: React.FC = () => {
  const navigate = useNavigate();
  const { createDigitalHuman, loading } = useDigitalHumanStore();
  const [form] = Form.useForm<FormValues>();

  const [current, setCurrent] = useState(0);
  const [formValues, setFormValues] = useState<FormValues>({
    name: '',
    description: '',
  });
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [fileList, setFileList] = useState<UploadFile[]>([]);

  const steps = [
    {
      title: 'Basic Info',
      icon: <UserOutlined />,
    },
    {
      title: 'Upload Image',
      icon: <PictureOutlined />,
    },
    {
      title: 'Confirm',
      icon: <CheckOutlined />,
    },
  ];

  const next = async () => {
    if (current === 0) {
      try {
        const values = await form.validateFields();
        setFormValues(values);
        setCurrent(current + 1);
      } catch (error) {
        // Validation failed
      }
    } else {
      setCurrent(current + 1);
    }
  };

  const prev = () => {
    setCurrent(current - 1);
  };

  const handleSubmit = async () => {
    try {
      const digitalHuman = await createDigitalHuman({
        name: formValues.name,
        description: formValues.description,
        image: imageFile || undefined,
      });
      message.success('Digital human created successfully!');
      navigate(`/digital-humans/${digitalHuman.id}`);
    } catch (error) {
      // Error handled by store
    }
  };

  const handleUploadChange = (info: any) => {
    setFileList(info.fileList);
    if (info.file.originFileObj) {
      setImageFile(info.file.originFileObj);
    }
  };

  const beforeUpload = (file: File) => {
    const isImage = file.type.startsWith('image/');
    if (!isImage) {
      message.error('You can only upload image files!');
      return false;
    }
    const isLt5M = file.size / 1024 / 1024 < 5;
    if (!isLt5M) {
      message.error('Image must be smaller than 5MB!');
      return false;
    }
    return false; // Prevent auto upload
  };

  const renderStepContent = () => {
    switch (current) {
      case 0:
        return (
          <Form
            form={form}
            layout="vertical"
            initialValues={formValues}
            style={{ maxWidth: 600, margin: '0 auto' }}
          >
            <Form.Item
              label="Name"
              name="name"
              rules={[
                { required: true, message: 'Please enter a name' },
                { min: 2, message: 'Name must be at least 2 characters' },
              ]}
            >
              <Input
                placeholder="Enter digital human name"
                size="large"
              />
            </Form.Item>

            <Form.Item
              label="Description"
              name="description"
              rules={[
                { max: 500, message: 'Description must be less than 500 characters' },
              ]}
            >
              <TextArea
                placeholder="Enter a description (optional)"
                rows={4}
                showCount
                maxLength={500}
              />
            </Form.Item>
          </Form>
        );

      case 1:
        return (
          <div style={{ maxWidth: 600, margin: '0 auto', textAlign: 'center' }}>
            <Paragraph>
              Upload an image of the person you want to create a digital human for.
              This will be used as the base for video generation.
            </Paragraph>
            <Upload
              listType="picture-card"
              fileList={fileList}
              onChange={handleUploadChange}
              beforeUpload={beforeUpload}
              maxCount={1}
              accept="image/*"
            >
              {fileList.length === 0 && (
                <div>
                  <UploadOutlined style={{ fontSize: 32 }} />
                  <div style={{ marginTop: 8 }}>Upload Image</div>
                </div>
              )}
            </Upload>
            <Paragraph type="secondary" style={{ marginTop: 16 }}>
              Supported formats: JPG, PNG, JPEG. Max size: 5MB
            </Paragraph>
          </div>
        );

      case 2:
        return (
          <div style={{ maxWidth: 600, margin: '0 auto' }}>
            <Card>
              <Title level={4}>Review Your Digital Human</Title>
              <div style={{ marginTop: 16 }}>
                <p>
                  <strong>Name:</strong> {formValues.name}
                </p>
                <p>
                  <strong>Description:</strong>{' '}
                  {formValues.description || 'No description'}
                </p>
                <p>
                  <strong>Image:</strong>{' '}
                  {imageFile ? imageFile.name : 'No image uploaded'}
                </p>
              </div>
            </Card>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div>
      <Title level={2}>Create Digital Human</Title>

      <Steps current={current} items={steps} style={{ marginBottom: 32 }} />

      <div style={{ minHeight: 300 }}>{renderStepContent()}</div>

      <div style={{ marginTop: 24, textAlign: 'center' }}>
        {current > 0 && (
          <Button style={{ marginRight: 8 }} onClick={prev}>
            Previous
          </Button>
        )}
        {current < steps.length - 1 && (
          <Button type="primary" onClick={next}>
            Next
          </Button>
        )}
        {current === steps.length - 1 && (
          <Button type="primary" onClick={handleSubmit} loading={loading}>
            Create
          </Button>
        )}
        <Button
          style={{ marginLeft: 8 }}
          onClick={() => navigate('/digital-humans')}
        >
          Cancel
        </Button>
      </div>
    </div>
  );
};