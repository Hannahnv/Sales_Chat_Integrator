import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import './Chat.css';

const Chat = () => {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [username, setUsername] = useState(localStorage.getItem('username') || '');
    const navigate = useNavigate();
    const chatSocket = useRef(null);

    useEffect(() => {
        const token = localStorage.getItem('token');
        if (!token) {
            navigate('/login');
        } else {
            setUsername(localStorage.getItem('username'));
            chatSocket.current = new WebSocket(`ws://localhost:8000/ws/chat/?token=${token}`);

            chatSocket.current.onmessage = function(e) {
                const data = JSON.parse(e.data);
                setMessages((prevMessages) => [...prevMessages, data]);
            };

            chatSocket.current.onclose = function(e) {
                console.error('Chat socket closed unexpectedly');
            };

            return () => {
                chatSocket.current.close();
            };
        }
    }, [navigate]);

    const sendMessage = () => {
        if (input.trim() !== '' && username) {
            chatSocket.current.send(JSON.stringify({
                'message': input.trim(),
                'username': username,
            }));
            setInput('');
        } else {
            console.error('Username is missing.');
        }
    };

    return (
        <div className="chat-container">
            <div className="chat-messages" id="chatMessages">
                {messages.map((msg, index) => (
                    <div
                        key={index}
                        className={`message-group ${msg.username === username ? 'user' : 'system'}`}
                    >
                        <div className="chat-username">{msg.username}</div>
                        <div className={`chat-message ${msg.username === username ? 'user' : 'system'}`}>
                            {msg.message}
                        </div>
                    </div>
                ))}
            </div>
            <div className="chat-input">
                <input
                    type="text"
                    id="chatInput"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Type your message..."
                    onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                />
                <button onClick={sendMessage}>Send</button>
            </div>
        </div>
    );
};

export default Chat;
