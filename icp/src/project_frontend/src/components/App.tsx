import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Button from 'react-bootstrap/Button';
import Card from 'react-bootstrap/Card';
import Form from 'react-bootstrap/Form';

export function App() {
  const [hover, setHover] = useState(false);
  const [username, setUsername] = useState('');
  const [canisterId, setCanisterId] = useState('');
  const navigate = useNavigate();

  const handleConnect = () => {
    if (username.trim() && canisterId.trim()) {
      navigate('/chat', { state: { username, canisterId } });
    }
  };

  const buttonStyle = {
    backgroundColor: '#007bff',
    color: 'white',
    border: '2px solid #007bff',
    width: '100%',
    fontWeight: 'bold',
    transition: 'background-color 0.3s ease',
    marginTop: '20px',
    borderRadius: '10px',
    padding: '10px 0',
  };

  const buttonHoverStyle = {
    backgroundColor: '#66b2ff',
    borderColor: '#66b2ff',
  };

  const inputStyle = {
    height: '45px',
    borderRadius: '10px',
    fontSize: '1rem',
    paddingLeft: '12px',
    border: '1px solid #ced4da',
  };

  return (
    <div className="App" style={{
      display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', backgroundColor: '#f8f9fa',
    }}>
      <Card style={{
        width: '32rem', border: '2px solid black', boxShadow: '0 4px 8px rgba(0,0,0,0.3)', borderRadius: '10px', padding: '20px',
      }}>
        <Card.Body>
          <Card.Title style={{ textAlign: 'center', marginBottom: '20px' }}>Connect to Canister</Card.Title>

          <Form>
            <Form.Group className="mb-4" controlId="formUsername">
              <Form.Label>Username</Form.Label>
              <Form.Control
                type="text"
                placeholder="Enter username"
                value={username}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => setUsername(e.target.value)}
                style={inputStyle}
              />
            </Form.Group>

            <Form.Group className="mb-4" controlId="formCanisterId">
              <Form.Label>Canister ID</Form.Label>
              <Form.Control
                type="text"
                placeholder="Enter canister ID"
                value={canisterId}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => setCanisterId(e.target.value)}
                style={inputStyle}
              />
            </Form.Group>

            <Button
              style={hover ? { ...buttonStyle, ...buttonHoverStyle } : buttonStyle}
              onMouseEnter={() => setHover(true)}
              onMouseLeave={() => setHover(false)}
              onClick={handleConnect}
            >
              Connect
            </Button>
          </Form>
        </Card.Body>
      </Card>
    </div>
  );
}
