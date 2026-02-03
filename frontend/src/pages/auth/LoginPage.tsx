import { Form, Input, Button, Card, Typography, message } from 'antd';
import { UserOutlined, LockOutlined } from '@ant-design/icons';
import { useNavigate, Link } from 'react-router-dom';
import { useAuthStore } from '@/store/authStore';
import { ROUTES } from '@/utils/constants';
import type { LoginRequest } from '@/types/auth';

const { Title, Text } = Typography;

export const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const { login, isLoading } = useAuthStore();

  const onFinish = async (values: LoginRequest) => {
    try {
      await login(values);
      message.success('Login successful!');
      navigate(ROUTES.DASHBOARD);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Login failed. Please check your credentials.';
      message.error(errorMessage);
    }
  };

  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh', background: '#f0f2f5' }}>
      <Card style={{ width: 400 }}>
        <div style={{ textAlign: 'center', marginBottom: 24 }}>
          <Title level={2}>OpenUser</Title>
          <Text type="secondary">Sign in to your account</Text>
        </div>
        <Form
          name="login"
          onFinish={onFinish}
          autoComplete="off"
          layout="vertical"
        >
          <Form.Item
            name="username"
            rules={[{ required: true, message: 'Please input your username!' }]}
          >
            <Input
              prefix={<UserOutlined />}
              placeholder="Username"
              size="large"
            />
          </Form.Item>

          <Form.Item
            name="password"
            rules={[{ required: true, message: 'Please input your password!' }]}
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder="Password"
              size="large"
            />
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit" loading={isLoading} block size="large">
              Sign In
            </Button>
          </Form.Item>

          <div style={{ textAlign: 'center' }}>
            <Text>Don't have an account? </Text>
            <Link to={ROUTES.REGISTER}>Sign up</Link>
          </div>
        </Form>
      </Card>
    </div>
  );
};
