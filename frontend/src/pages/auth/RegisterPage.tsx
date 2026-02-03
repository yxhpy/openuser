import { Form, Input, Button, Card, Typography, message } from 'antd';
import { UserOutlined, LockOutlined, MailOutlined } from '@ant-design/icons';
import { useNavigate, Link } from 'react-router-dom';
import { useAuthStore } from '@/store/authStore';
import { ROUTES } from '@/utils/constants';
import type { RegisterRequest } from '@/types/auth';

const { Title, Text } = Typography;

export const RegisterPage: React.FC = () => {
  const navigate = useNavigate();
  const { register, isLoading } = useAuthStore();

  const onFinish = async (values: RegisterRequest) => {
    try {
      await register(values);
      message.success('Registration successful!');
      navigate(ROUTES.DASHBOARD);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Registration failed. Please try again.';
      message.error(errorMessage);
    }
  };

  const validatePassword = (_: unknown, value: string) => {
    if (!value) {
      return Promise.reject(new Error('Please input your password!'));
    }
    if (value.length < 8) {
      return Promise.reject(new Error('Password must be at least 8 characters!'));
    }
    if (!/[A-Z]/.test(value)) {
      return Promise.reject(new Error('Password must contain at least one uppercase letter!'));
    }
    if (!/[a-z]/.test(value)) {
      return Promise.reject(new Error('Password must contain at least one lowercase letter!'));
    }
    if (!/\d/.test(value)) {
      return Promise.reject(new Error('Password must contain at least one digit!'));
    }
    return Promise.resolve();
  };

  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh', background: '#f0f2f5' }}>
      <Card style={{ width: 400 }}>
        <div style={{ textAlign: 'center', marginBottom: 24 }}>
          <Title level={2}>OpenUser</Title>
          <Text type="secondary">Create your account</Text>
        </div>
        <Form
          name="register"
          onFinish={onFinish}
          autoComplete="off"
          layout="vertical"
        >
          <Form.Item
            name="username"
            rules={[
              { required: true, message: 'Please input your username!' },
              { min: 3, message: 'Username must be at least 3 characters!' },
            ]}
          >
            <Input
              prefix={<UserOutlined />}
              placeholder="Username"
              size="large"
            />
          </Form.Item>

          <Form.Item
            name="email"
            rules={[
              { required: true, message: 'Please input your email!' },
              { type: 'email', message: 'Please enter a valid email!' },
            ]}
          >
            <Input
              prefix={<MailOutlined />}
              placeholder="Email"
              size="large"
            />
          </Form.Item>

          <Form.Item
            name="password"
            rules={[{ validator: validatePassword }]}
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder="Password"
              size="large"
            />
          </Form.Item>

          <Form.Item
            name="confirmPassword"
            dependencies={['password']}
            rules={[
              { required: true, message: 'Please confirm your password!' },
              ({ getFieldValue }) => ({
                validator(_, value) {
                  if (!value || getFieldValue('password') === value) {
                    return Promise.resolve();
                  }
                  return Promise.reject(new Error('Passwords do not match!'));
                },
              }),
            ]}
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder="Confirm Password"
              size="large"
            />
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit" loading={isLoading} block size="large">
              Sign Up
            </Button>
          </Form.Item>

          <div style={{ textAlign: 'center' }}>
            <Text>Already have an account? </Text>
            <Link to={ROUTES.LOGIN}>Sign in</Link>
          </div>
        </Form>
      </Card>
    </div>
  );
};
