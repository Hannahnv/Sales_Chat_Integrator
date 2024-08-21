// Navbar.js
import React from 'react';
import { Link } from 'react-router-dom';
import './Navbar.css';

const Navbar = ({ isLoggedIn }) => {
    return (
        <nav className="navbar">
            <div className="navbar-left">
                <div className="navbar-logo">
                    <Link to="/">Ecommerce Web</Link>
                </div>
                {isLoggedIn && (
                    <div className="navbar-chat">
                        <Link to="/chat">Chat</Link>
                    </div>
                )}
            </div>

            <div className="navbar-links">
                {isLoggedIn ? (
                    <Link to="/logout">Logout</Link>
                ) : (
                    <Link to="/login">Login</Link>
                )}
            </div>
        </nav>
    );
};

export default Navbar;
