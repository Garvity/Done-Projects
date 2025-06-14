import React, { useState } from 'react';
import { useLocation } from 'react-router-dom';
import Card from 'react-bootstrap/Card';
import Form from 'react-bootstrap/Form';
import Button from 'react-bootstrap/Button';
import ListGroup from 'react-bootstrap/ListGroup';
import Badge from 'react-bootstrap/Badge';

interface Message {
  id: number;
  user: string;
  text: string;
  time: string;
}

interface Participant {
  name: string;
  online: boolean;
}

interface LocationState {
  username?: string;
  canisterId?: string;
}

export function ChatApp() {
  const location = useLocation();
  const { username = 'You', canisterId = '' } = (location.state as LocationState) || {};

  const [messages, setMessages] = useState<Message[]>([]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [showParticipants, setShowParticipants] = useState(false);

  const participants: Participant[] = [
    { name: username, online: true },
    { name: 'Alice', online: false },
    { name: 'Bob', online: true },
    { name: 'Charlie', online: false },
  ];

  const handleSend = () => {
    if (currentMessage.trim() === '') return;

    const newMessage: Message = {
      id: Date.now(),
      user: username,
      text: currentMessage,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages([...messages, newMessage]);
    setCurrentMessage('');
  };

  const handleDelete = (id: number) => setMessages(messages.filter(msg => msg.id !== id));

  const handleEdit = (id: number) => {
    const msg = messages.find(m => m.id === id);
    if (msg) {
      setCurrentMessage(msg.text);
      setMessages(messages.filter(m => m.id !== id));
    }
  };

  return (
    <div style={{
      display: 'flex', justifyContent: 'center', alignItems: 'center',
      minHeight: '100vh', backgroundColor: '#f8f9fa',
    }}>
      <Card style={{
        width: '30rem', 
        border: '2px solid black', 
        borderRadius: '10px',
        boxShadow: '0 4px 8px rgba(0, 0, 0, 0.3)', 
        padding: '20px',
        minHeight: '80vh',
        margin: '20px 0'
      }}>
        <Card.Body style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <div>
            <Card.Title className="text-center fw-bold mb-3" style={{ fontSize: '1.5rem' }}>Chat App</Card.Title>
            <Card.Subtitle className="text-muted text-center mb-4" style={{ fontSize: '1.1rem' }}>Canister ID: {canisterId}</Card.Subtitle>
          </div>

          <Button
            variant="secondary"
            size="sm"
            className="mb-3"
            onClick={() => setShowParticipants(!showParticipants)}
            style={{ width: 'fit-content', margin: '0 auto' }}
          >
            {showParticipants ? 'Hide Participants' : 'Show Participants'}
          </Button>

          {showParticipants && (
            <ListGroup className="mb-4">
              {participants.map((p, i) => (
                <ListGroup.Item key={i} className="d-flex justify-content-between align-items-center" style={{ padding: '12px 15px' }}>
                  <span style={{ fontSize: '1.1rem' }}>{p.name}</span>
                  <Badge 
                    bg={p.online ? 'success' : 'danger'}
                    style={{
                      backgroundColor: p.online ? '#28a745' : '#dc3545',
                      padding: '6px 12px',
                      borderRadius: '12px',
                      fontWeight: 'bold',
                      fontSize: '0.9rem'
                    }}
                  >
                    {p.online ? 'Online' : 'Offline'}
                  </Badge>
                </ListGroup.Item>
              ))}
            </ListGroup>
          )}

          <ListGroup variant="flush" style={{ 
            maxHeight: '400px', 
            overflowY: 'auto', 
            marginBottom: '20px',
            flex: 1,
            border: '1px solid #dee2e6',
            borderRadius: '10px'
          }}>
            {messages.map(msg => (
              <ListGroup.Item key={msg.id} className="d-flex justify-content-between align-items-start" style={{ padding: '15px' }}>
                <div style={{ flex: 1, marginRight: '15px' }}>
                  <strong style={{ fontSize: '1.1rem' }}>{msg.user}:</strong> 
                  <span style={{ fontSize: '1.1rem', marginLeft: '8px' }}>{msg.text}</span>
                  <div style={{ fontSize: '0.9rem', color: '#6c757d', marginTop: '5px' }}>{msg.time}</div>
                </div>
                <div style={{ display: 'flex', gap: '8px' }}>
                  <Button variant="outline-secondary" size="sm" onClick={() => handleEdit(msg.id)}>Edit</Button>
                  <Button variant="outline-danger" size="sm" onClick={() => handleDelete(msg.id)}>Delete</Button>
                </div>
              </ListGroup.Item>
            ))}
          </ListGroup>

          <Form style={{ marginTop: 'auto' }}>
            <Form.Group>
              <Form.Control
                type="text"
                placeholder="Type your message..."
                value={currentMessage}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => setCurrentMessage(e.target.value)}
                style={{ 
                  height: '50px', 
                  borderRadius: '10px', 
                  marginBottom: '15px', 
                  paddingLeft: '15px',
                  fontSize: '1.1rem'
                }}
              />
            </Form.Group>
            <Button
              onClick={handleSend}
              style={{
                width: '100%', 
                fontWeight: 'bold', 
                backgroundColor: '#007bff',
                border: '2px solid #007bff', 
                borderRadius: '10px',
                height: '50px',
                fontSize: '1.1rem'
              }}
              onMouseEnter={(e: React.MouseEvent<HTMLButtonElement>) => {
                const target = e.target as HTMLButtonElement;
                target.style.backgroundColor = '#66b2ff';
              }}
              onMouseLeave={(e: React.MouseEvent<HTMLButtonElement>) => {
                const target = e.target as HTMLButtonElement;
                target.style.backgroundColor = '#007bff';
              }}
            >
              Send Message
            </Button>
          </Form>
        </Card.Body>
      </Card>
    </div>
  );
}
