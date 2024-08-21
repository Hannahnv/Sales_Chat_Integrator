// App.js
import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
import Chat from './components/Chat';
import Login from './components/Login';
import Logout from './components/Logout';
import Navbar from './components/Navbar';

import './App.css';

function App() {
    const [isLoggedIn, setIsLoggedIn] = useState(false);

    useEffect(() => {
        const token = localStorage.getItem('token');
        setIsLoggedIn(!!token);
    }, []);

    return (
        <Router>
            <div className="App">
                <Navbar isLoggedIn={isLoggedIn} />
                <Routes>
                    <Route path="/login" element={<Login setIsLoggedIn={setIsLoggedIn} />} />
                    <Route path="/logout" element={<Logout setIsLoggedIn={setIsLoggedIn} />} />
                    <Route path="/chat" element={isLoggedIn ? <Chat /> : <Navigate to="/login" />} />
                    <Route path="*" element={<Navigate to={isLoggedIn ? "/chat" : "/login"} />} />
                </Routes>
            </div>
        </Router>
    );
}

export default App;