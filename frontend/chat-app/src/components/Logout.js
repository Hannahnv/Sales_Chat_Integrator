// Logout.js
import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { logout } from '../services/api';

const Logout = () => {
    const navigate = useNavigate();

    useEffect(() => {
        logout();
        navigate('/login');
    }, [navigate]);

    return (
        <div className="logout-container">
            <h2>You have been logged out.</h2>
            <p>Redirecting to login...</p>
        </div>
    );
};

export default Logout;
