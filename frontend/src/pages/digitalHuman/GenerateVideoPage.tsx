import { useEffect, useState } from 'react';
import {
  Card,
  Form,
  Input,
  Select,
  Upload,
  Button,
  Typography,
  Spin,
  message,
  Radio,
  Space,
} from 'antd';
import {
  ArrowLeftOutlined,
  UploadOutlined,
  PlayCircleOutlined,
} from '@ant-design/icons';
import type { UploadFile } from 'antd';
import { useNavigate, useParams } from 'react-router-dom';
import { useDigitalHumanStore } from '../../store/digitalHumanStore';

const { Title, Paragraph } = Typography;
const { TextArea } = Input;

type InputType = 'text' | 'audio';

export const GenerateVideoPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const {
    currentDigitalHuman,
    loading,
    error,
    fetchDigitalHuman,
    generateVideo,
    clearError,
  } = useDigitalHumanStore();

  const [form] = Form.useForm();
  const [inputType, setInputType] = useState<InputType>('text');
  const [audioFile, setAudioFile] = useState<File | null>(null);
  const [audioFileList, setAudioFileList] = useState<UploadFile[]>([]);
  const [generatedVideoPath, setGeneratedVideoPath] = useState<string | null>(null);

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

  const handleAudioUploadChange = (info: any) => {
    setAudioFileList(info.fileList);
    if (info.file.originFileObj) {
      setAudioFile(info.file.originFileObj);
    }
  };

  const beforeAudioUpload = (file: File) => {
    const isAudio = file.type.startsWith('audio/');
    if (!isAudio) {
      message.error('You can only upload audio files!');
      return false;
    }
    const isLt10M = file.size / 1024 / 1024 < 10;
    if (!isLt10M) {
      message.error('Audio must be smaller than 10MB!');
      return false;
    }
    return false; // Prevent auto upload
  };

  const handleSubmit = async (values: any) => {
    if (!currentDigitalHuman) return;

    try {
      const videoPath = await generateVideo({
        digital_human_id: currentDigitalHuman.id,
        text: inputType === 'text' ? values.text : undefined,
        audio: inputType === 'audio' ? audioFile || undefined : undefined,
        mode: values.mode,
        speaker_wav: values.speaker_wav,
      });
      setGeneratedVideoPath(videoPath);
      message.success('Video generated successfully!');
    } catch (error) {
      // Error handled by store
    }
  };

  if (loading && !currentDigitalHuman) {
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
        onClick={() => navigate(`/digital-humans/${currentDigitalHuman.id}`)}
        style={{ marginBottom: 16 }}
      >
        Back to Detail
      </Button>

      <Title level={2}>Generate Video - {currentDigitalHuman.name}</Title>

      <Card style={{ maxWidth: 800, margin: '0 auto' }}>
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
          initialValues={{
            mode: 'enhanced_talking_head',
          }}
        >
          <Form.Item label="Input Type">
            <Radio.Group
              value={inputType}
              onChange={(e) => setInputType(e.target.value)}
            >
              <Radio.Button value="text">Text</Radio.Button>
              <Radio.Button value="audio">Audio File</Radio.Button>
            </Radio.Group>
          </Form.Item>

          {inputType === 'text' ? (
            <Form.Item
              label="Text"
              name="text"
              rules={[
                { required: true, message: 'Please enter text' },
                { max: 1000, message: 'Text must be less than 1000 characters' },
              ]}
            >
              <TextArea
                placeholder="Enter the text you want the digital human to speak"
                rows={6}
                showCount
                maxLength={1000}
              />
            </Form.Item>
          ) : (
            <Form.Item
              label="Audio File"
              required
              help="Upload an audio file for the digital human to lip-sync to"
            >
              <Upload
                fileList={audioFileList}
                onChange={handleAudioUploadChange}
                beforeUpload={beforeAudioUpload}
                maxCount={1}
                accept="audio/*"
              >
                <Button icon={<UploadOutlined />}>Upload Audio</Button>
              </Upload>
              <Paragraph type="secondary" style={{ marginTop: 8 }}>
                Supported formats: MP3, WAV, OGG. Max size: 10MB
              </Paragraph>
            </Form.Item>
          )}

          <Form.Item
            label="Generation Mode"
            name="mode"
            rules={[{ required: true, message: 'Please select a mode' }]}
          >
            <Select>
              <Select.Option value="lipsync">
                Lip Sync (Wav2Lip)
              </Select.Option>
              <Select.Option value="talking_head">
                Talking Head (SadTalker)
              </Select.Option>
              <Select.Option value="enhanced_lipsync">
                Enhanced Lip Sync (Wav2Lip + GFPGAN)
              </Select.Option>
              <Select.Option value="enhanced_talking_head">
                Enhanced Talking Head (SadTalker + GFPGAN)
              </Select.Option>
            </Select>
          </Form.Item>

          <Form.Item>
            <Space>
              <Button
                type="primary"
                htmlType="submit"
                icon={<PlayCircleOutlined />}
                loading={loading}
              >
                Generate Video
              </Button>
              <Button onClick={() => navigate(`/digital-humans/${currentDigitalHuman.id}`)}>
                Cancel
              </Button>
            </Space>
          </Form.Item>
        </Form>

        {generatedVideoPath && (
          <Card title="Generated Video" style={{ marginTop: 24 }}>
            <video
              controls
              style={{ width: '100%', maxHeight: 500 }}
              src={generatedVideoPath}
            >
              Your browser does not support the video tag.
            </video>
            <Paragraph style={{ marginTop: 16 }}>
              <strong>Video Path:</strong> {generatedVideoPath}
            </Paragraph>
          </Card>
        )}
      </Card>
    </div>
  );
};