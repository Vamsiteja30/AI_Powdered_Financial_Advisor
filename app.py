import streamlit as st
import yfinance as yf
import time
import re
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv
import google.generativeai as genai
from datetime import datetime, timedelta
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import io
import os
import matplotlib.pyplot as plt
from fpdf import FPDF
import hashlib
import json
from pathlib import Path

# ==================== AUTHENTICATION SYSTEM ====================
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    if make_hashes(password) == hashed_text:
        return hashed_text
    return False

class Authenticator:
    def __init__(self):
        self.users_file = Path("users.json")
        self.users = self._load_users()

    def _load_users(self):
        if self.users_file.exists():
            with open(self.users_file, 'r') as f:
                return json.load(f)
        return {}

    def _save_users(self):
        with open(self.users_file, 'w') as f:
            json.dump(self.users, f)

    def sign_up(self, username, password):
        if username in self.users:
            return False, "Username already exists"
        if len(password) < 6:
            return False, "Password must be at least 6 characters"
        self.users[username] = make_hashes(password)
        self._save_users()
        return True, "Sign up successful"

    def login(self, username, password):
        if username not in self.users:
            return False, "Username not found"
        if check_hashes(password, self.users[username]):
            return True, "Login successful"
        return False, "Wrong password"

# Initialize authenticator
auth = Authenticator()

# ==================== AUTHENTICATION PAGE ====================
def auth_page():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');

        * {
            font-family: 'Poppins', sans-serif;
        }

        .auth-container {
            max-width: 650px;
            margin: 3 auto;
            padding: 60px;
            border-radius: 25px;
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            box-shadow: 0 12px 24px rgba(0, 0, 0, 0.15);
            border: 3px solid rgba(255, 255, 255, 0.3);
            animation: fadeIn 0.6s ease forwards;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .auth-title {
            text-align: center;
            background: linear-gradient(135deg, #2563EB 0%, #1E40AF 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 35px;
            font-size: 32px;
            font-weight: 700;
        }

        .auth-button {
            width: 100%;
            margin-top: 25px;
            padding: 15px !important;
            font-size: 16px !important;
            background: linear-gradient(135deg, #2563EB 0%, #1E40AF 100%);
            border: none !important;
            border-radius: 12px !important;
            transition: all 0.3s ease !important;
        }

        .auth-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(37, 99, 235, 0.3);
        }

        .logo-container {
            text-align: center;
            margin-bottom: 40px;
            position: relative;
        }

        .logo-text {
            font-size: 42px;
            font-weight: 800;
            background: linear-gradient(45deg, #2563EB, #1d4edd);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            position: relative;
            animation: write 1s ease-in-out forwards;
            overflow: hidden;
            white-space: nowrap;
        }

        @keyframes write {
            from { width: 0; }
            to { width: 100%; }
        }

        .pen-effect {
            position: absolute;
            right: -30px;
            bottom: 0;
            animation: float 3s ease-in-out infinite;
        }

        @keyframes float {
            0% { transform: translateY(0px); }
            50% { transform: translateY(-10px); }
            100% { transform: translateY(0px); }
        }

        .form-row {
            display: flex;
            gap: 15px;
            margin-bottom: 15px;
        }
    </style>
    """, unsafe_allow_html=True)

    # Center the auth container
    col1, col2, col3 = st.columns([0.5, 4, 0.5])
    with col2:
        st.markdown("""
        <div class="logo-container">
            <div class="logo-text">AI Finance Advisor
                <div class="pen-effect">✍</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["🔐 Secure Login", "🚀 New Account"])

        with tab1:
            with st.form("login_form"):
                st.markdown("<h3 class='auth-title'>Welcome Back</h3>", unsafe_allow_html=True)
                username = st.text_input("Username", key="login_username", placeholder="Enter your username")
                password = st.text_input("Password", type="password", key="login_password", placeholder="••••••••")
                submit = st.form_submit_button("Access Dashboard →", type="primary", use_container_width=True)

                if submit:
                    if not username or not password:
                        st.error("Please fill in all fields")
                    else:
                        success, message = auth.login(username, password)
                        if success:
                            st.session_state["authenticated"] = True
                            st.session_state["username"] = username
                            st.session_state["user_profile"] = {
                                'name': username,
                                'age': 35,
                                'income': 100000,
                                'savings': 65000,
                                'debt': 25000,
                                'expenses': 10000,
                                'risk_pref': "Conservative",
                                'risk_percentage': 0,
                                'debt_to_income': 0,
                                'savings_ratio': 0,
                                'expenses_ratio': 0
                            }

                            # Show success message and balloons
                            success_placeholder = st.empty()
                            success_placeholder.success(
                                f"Welcome {username}! You've successfully logged in. Redirecting to dashboard...")
                            st.balloons()

                            # Wait for 2 seconds
                            time.sleep(2)

                            # Clear the success message and redirect
                            success_placeholder.empty()
                            st.rerun()
                        else:
                            st.error(message)

        with tab2:
            with st.form("signup_form"):
                st.markdown("<h3 class='auth-title'>Start Your Journey</h3>", unsafe_allow_html=True)

                # Split name fields
                col1, col2 = st.columns(2)
                with col1:
                    first_name = st.text_input("First Name", key="signup_fname", placeholder="John")
                with col2:
                    last_name = st.text_input("Last Name", key="signup_lname", placeholder="Doe")

                email = st.text_input("Email Address", key="signup_email", placeholder="john@example.com")
                new_username = st.text_input("Username", key="signup_username", placeholder="john_doe123")

                # Split password fields
                col3, col4 = st.columns(2)
                with col3:
                    new_password = st.text_input("Password", type="password", key="signup_password",
                                                 placeholder="••••••••")
                with col4:
                    confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm",
                                                     placeholder="••••••••")

                submit = st.form_submit_button("Create Account 🚀", type="primary", use_container_width=True)

                if submit:
                    if not all([first_name, last_name, email, new_username, new_password, confirm_password]):
                        st.error("Please fill in all fields")
                    elif new_password != confirm_password:
                        st.error("Passwords do not match")
                    else:
                        success, message = auth.sign_up(new_username, new_password)
                        if success:
                            st.balloons()
                            st.success(f"{message} Please login now.")
                        else:
                            st.error(message)

# ==================== LANDING PAGE ====================
def landing_page():
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@700&family=Roboto:wght@400;700&display=swap');
            /* Custom Scrollbar */
            ::-webkit-scrollbar {
                width: 5px;
            }
            ::-webkit-scrollbar-track {
                background: #f1f1f1;
                border-radius: 10px;
            }
            ::-webkit-scrollbar-thumb {
                background: #ff5722;
                border-radius: 10px;
            }
            ::-webkit-scrollbar-thumb:hover {
                background: #ff9800;
            }

            /* Navbar Styles */
            .navbar {
                background: rgba(255, 255, 255, 0.95);
                display: flex;
                align-items: center;
                justify-content: left;
                width: 100%;
                padding: 1rem 2rem;
                font-family: 'Poppins', sans-serif;
                position: fixed;
                top: 45px;
                left: 0;
                z-index: 1000;
                backdrop-filter: blur(10px);
                border-bottom: 1px solid rgba(0, 0, 0, 0.1);
                box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.1);
            }
            .navbar-logo {
                font-size: 1.8rem;
                font-weight: bold;
                color: #1a237e;
                letter-spacing: 5px;
            }
            @keyframes glow {
                0% { text-shadow: 0 0 10px rgba(26, 35, 126, 0.4); }
                100% { text-shadow: 0 0 20px rgba(26, 35, 126, 0.8); }
            }
            .navbar-links {
                list-style: none;
                display: flex;
                gap: 2rem;
                margin: 0;
                padding: 0;
                position: absolute;
                left: 50%;
                transform: translateX(-50%);
            }
            .navbar-links a {
                text-decoration: none;
                color: #5F6368;
                font-family: 'Roboto', sans-serif;
                font-size: 1.2rem;
                font-weight: 500;
                padding: 0.5rem 1rem;
                border-radius: 25px;
                background: linear-gradient(45deg, #ff6b6b, #ff5722);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                transition: all 0.3s ease;
                position: relative;
                overflow: hidden;
            }
            .navbar-links a::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: linear-gradient(45deg, #ff6b6b, #ff5722);
                z-index: -1;
                border-radius: 25px;
                transform: scaleX(0);
                transform-origin: right;
                transition: transform 0.3s ease;
            }
            .navbar-links a:hover::before {
                transform: scaleX(1);
                transform-origin: left;
            }
            .navbar-links a:hover {
                color: white;
                -webkit-text-fill-color: white;
            }

            /* Responsive Design */
            @media (max-width: 768px) {
                .navbar {
                    padding: 1rem;
                    flex-wrap: nowrap;
                }
                .navbar-logo {
                    font-size: 1.5rem;
                }
                .navbar-links {
                    gap: 1rem;
                }
                .navbar-links a {
                    font-size: 1rem;
                    padding: 0.5rem;
                }
            }
            @media (max-width: 480px) {
                .navbar {
                    padding: 0.5rem;
                }
                .navbar-logo {
                    font-size: 1.2rem;
                }
                .navbar-links {
                    gap: 0.5rem;
                }
                .navbar-links a {
                    font-size: 0.8rem;
                    padding: 0.3rem;
                }
            }

            /* Hero Section */
            .hero-section {
                text-align: center;
                font-family: 'Poppins', sans-serif;
                margin: 8rem auto 3rem;
                max-width: 900px;
                padding: 2rem;
                animation: fadeIn 1s ease-in-out;
            }
            .greeting-message {
                font-size: 2.5rem;
                font-weight: bold;
                color: #1a237e;
                animation: fadeIn 1.2s ease-in-out;
            }
            .main-headline {
                font-size: 4.5rem;
                font-weight: bold;
                background: linear-gradient(45deg, #ff9800, #ff5722);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                animation: float 3s ease-in-out infinite;
            }
            .sub-headline {
                font-size: 1.8rem;
                color: #333;
                margin-bottom: 2rem;
                animation: fadeIn 1.5s ease-in-out;
            }

            /* CTA Button */
            div[data-testid="stButton"] > button {
                background: linear-gradient(45deg, #ff6b6b, #ff5722) !important;
                color: white !important;
                font-family: 'Poppins', sans-serif !important;
                font-size: 1.5rem !important;
                padding: 1.5rem 3rem !important;
                border: none !important;
                border-radius: 50px !important;
                cursor: pointer !important;
                transition: all 0.3s ease !important;
                animation: pulse 2s infinite, glow 1.5s infinite alternate !important;
                position: relative !important;
                overflow: hidden !important;
                box-shadow: 0 8px 24px rgba(255, 87, 34, 0.3) !important;
                width: 100% !important;
                max-width: 400px !important;
                margin: 2rem auto !important;
                display: block !important;
            }
            div[data-testid="stButton"] > button:hover {
                transform: scale(1.05) !important;
                box-shadow: 0 12px 32px rgba(255, 87, 34, 0.5) !important;
            }
            @keyframes pulse {
                0% { transform: scale(1); }
                50% { transform: scale(1.02); }
                100% { transform: scale(1); }
            }
            @keyframes glow {
                0% { box-shadow: 0 0 15px rgba(255, 87, 34, 0.4); }
                100% { box-shadow: 0 0 25px rgba(255, 87, 34, 0.6); }
            }

            /* Background Animation */
            .interactive-background {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                z-index: -1;
                background: linear-gradient(135deg, #f8fafc, #f0f4ff);
                animation: backgroundShift 10s infinite alternate;
            }
            @keyframes backgroundShift {
                0% { background-position: 0% 50%; }
                100% { background-position: 100% 50%; }
            }

            /* Floating Particles */
            .particles {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                overflow: hidden;
            }
            .particles span {
                position: absolute;
                display: block;
                width: 20px;
                height: 20px;
                background: rgba(255, 152, 0, 0.5);
                border-radius: 50%;
                animation: floatParticle 5s infinite;
            }
            @keyframes floatParticle {
                0% { transform: translateY(0) translateX(0); }
                50% { transform: translateY(-100px) translateX(100px); }
                100% { transform: translateY(0) translateX(0); }
            }

            /* Interactive Card */
            .interactive-card {
                background: rgba(255, 255, 255, 0.9);
                border-radius: 20px;
                padding: 2rem;
                margin: 2rem auto;
                max-width: 800px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.2);
                animation: slideIn 1s ease-in-out;
            }
            @keyframes slideIn {
                0% { transform: translateY(50px); opacity: 0; }
                100% { transform: translateY(0); opacity: 1; }
            }

            /* Feature Cards */
            .feature-card {
                background: rgba(255, 255, 255, 0.9);
                border-radius: 15px;
                padding: 1.5rem;
                margin: 1rem;
                box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
                transition: all 0.3s ease;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            .feature-card:hover {
                transform: translateY(-10px);
                box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
            }

            /* Feature Icons */
            .feature-icon {
                font-size: 2.5rem;
                margin-bottom: 1rem;
                color: #ff5722;
            }

            /* Feature Grid */
            .feature-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 1.5rem;
                margin: 2rem 0;
            }

            /* Footer */
            .footer {
                text-align: center;
                padding: 2rem;
                margin-top: 3rem;
                color: #666;
                font-size: 0.9rem;
            }

            /* Custom Cursor */
            .custom-cursor {
                position: fixed;
                width: 20px;
                height: 20px;
                background: #ff5722;
                border-radius: 50%;
                pointer-events: none;
                transform: translate(-50%, -50%);
                z-index: 1000;
                mix-blend-mode: difference;
                transition: transform 0.1s ease-out;
            }
        </style>

        <!-- Navbar -->
        <div class="navbar">
            <div class="navbar-logo">
                FinAI
            </div>
            <div class="navbar-links">
                <a href="#home">Home</a>
                <a href="#about">About</a>
                <a href="#features">Features</a>
                <a href="#contact">Contact</a>
            </div>
        </div>

        <div class="interactive-background"></div>
        <div class="particles">
            <span style="top: 10%; left: 20%; animation-delay: 0s;"></span>
            <span style="top: 20%; left: 50%; animation-delay: 1s;"></span>
            <span style="top: 30%; left: 70%; animation-delay: 2s;"></span>
            <span style="top: 40%; left: 10%; animation-delay: 3s;"></span>
            <span style="top: 50%; left: 90%; animation-delay: 4s;"></span>
        </div>

        <!-- Home Section -->
        <div id="home" class="hero-section">
            <div class="greeting-message">🚀 Welcome to Your Financial Future</div>
            <h1 class="main-headline">AI-Powered Financial Intelligence</h1>
            <p class="sub-headline">
                Transform your financial decision-making with real-time insights and <br>
                predictive analytics powered by machine learning.
            </p>
            <div class="cta-text">Start your journey to financial success today!</div>
        </div>

        <!-- About Section -->
        <div id="about" class="interactive-card">
            <h2>About Us – Shaping the Future of Financial Intelligence</h2>
            <p>
                At <strong>AI-Powered Finance Advisor</strong>, we believe financial freedom should be accessible to everyone. 
                Whether you're a student, a working professional, or a seasoned investor, our AI-driven platform is designed 
                to help you make smarter financial decisions.
            </p>
            <h3>🌟 Why We're Different?</h3>
            <ul>
                <li><strong>Real-Time AI Analytics:</strong> Never miss an investment opportunity or financial trend.</li>
                <li><strong>Automated Savings Plans:</strong> AI suggests optimal saving strategies based on your income and goals.</li>
                <li><strong>Debt-Free Faster:</strong> AI provides smart repayment & refinancing options tailored to your situation.</li>
                <li><strong>24/7 AI Financial Assistant:</strong> Get expert financial insights anytime, anywhere.</li>
            </ul>
        </div>

        <!-- Features Section -->
        <div id="features" class="feature-grid">
            <div class="feature-card card-3d">
                <div class="feature-icon">📈</div>
                <h3>Real-Time Stock Insights</h3>
                <p>Get up-to-date stock data, trends, and predictions to make informed investment decisions.</p>
            </div>
            <div class="feature-card card-3d">
                <div class="feature-icon">💼</div>
                <h3>Personalized Financial Advice</h3>
                <p>Receive tailored financial advice based on your unique profile and goals.</p>
            </div>
            <div class="feature-card card-3d">
                <div class="feature-icon">🤖</div>
                <h3>AI-Powered Chatbot</h3>
                <p>Ask questions and get instant answers from our AI-powered financial assistant.</p>
            </div>
            <div class="feature-card card-3d">
                <div class="feature-icon">📊</div>
                <h3>Portfolio Management</h3>
                <p>Track and manage your investments with advanced portfolio analytics.</p>
            </div>
        </div>

        <!-- Contact Section -->
        <div id="contact" class="interactive-card">
            <h2>Contact Us – Your Financial Success Starts Here!</h2>
            <p>
                Have questions? Need financial guidance? Let's connect!<br>
                📧 <strong>Email:</strong> support@aifinanceadvisor.com<br>
                🌐 <strong>Website:</strong> <a href="http://www.aifinanceadvisor.com">www.aifinanceadvisor.com</a><br>
                📲 <strong>Follow Us:</strong> 
                <a href="https://instagram.com/AIFinanceAdvisor">Instagram</a>, 
                <a href="https://facebook.com/AIFinanceCommunity">Facebook</a>, 
                <a href="https://twitter.com/AI_Finance">Twitter</a>
            </p>
        </div>

        <!-- Custom Cursor -->
        <div class="custom-cursor"></div>

        <script>
            // Custom Cursor Script
            const cursor = document.querySelector('.custom-cursor');
            document.addEventListener('mousemove', (e) => {
                cursor.style.left = e.pageX + 'px';
                cursor.style.top = e.pageY + 'px';
            });

            // Smooth Scroll Script
            document.querySelectorAll('.navbar-links a').forEach(anchor => {
                anchor.addEventListener('click', function (e) {
                    e.preventDefault();
                    document.querySelector(this.getAttribute('href')).scrollIntoView({
                        behavior: 'smooth'
                    });
                });
            });
        </script>
    """, unsafe_allow_html=True)

    # Single Get Started Button
    if st.button("🚀 Get Started", key="get_started_button"):
        st.session_state.landing_viewed = True
        st.rerun()

    st.markdown(""" 
    <div class="footer">
            © 2025 AI Finance & Stock Advisor. All rights reserved.
        </div>
    """, unsafe_allow_html=True)

# ==================== MAIN APP ====================
def main_app():
    # Page configuration
    st.set_page_config(page_title="AI Finance & Stock Advisor", page_icon="💼", layout="wide")

    # Load environment variables
    load_dotenv()
    api_key = "AIzaSyD3L43HYFM6m-JcCv0kX0w378u4X3kwOUs"  # Replace with your actual API key
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')

    # Main title with professional styling
    st.markdown("""
    <style>
        .main-title {
            text-align: center;
            font-size: 2.8rem;
            font-weight: 700;
            color: #2563EB;
            text-transform: uppercase;
            letter-spacing: 2px;
            margin: 1.5rem 0;
            padding: 1rem;
            background: linear-gradient(45deg, #2563EB, #1d4edd);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 2px 2px 4px rgba(37, 99, 235, 0.2);
            position: relative;
            animation: titleEntrance 1s ease-out;
        }

        .main-title::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 50%;
            transform: translateX(-50%);
            width: 120px;
            height: 4px;
            background: #2563EB;
            border-radius: 2px;
        }

        @keyframes titleEntrance {
            0% {
                opacity: 0;
                transform: translateY(-20px);
            }
            100% {
                opacity: 1;
                transform: translateY(0);
            }
        }
    </style>
    """, unsafe_allow_html=True)



    # Main title with professional styling
    st.markdown("""
    <style>
        .hero-section {
            background: linear-gradient(135deg, #2563EB 0%, #1d4edd 100%);
            border-radius: 20px;
            padding: 2rem;
            margin: 1rem 0;
            color: white;
            text-align: center;
            position: relative;
            overflow: hidden;
            box-shadow: 0 10px 30px rgba(37, 99, 235, 0.3);
        }
        .hero-title {
            font-size: 3.5rem;
            font-weight: 800;
            margin-bottom: 1rem;
            text-shadow: 2px 2px 8px rgba(0,0,0,0.2);
            animation: fadeInDown 1s ease;
        }
        .hero-subtitle {
            font-size: 1.5rem;
            opacity: 0.9;
            margin-bottom: 1.5rem;
            animation: fadeIn 1.5s ease;
        }
        @keyframes fadeInDown {
            0% { opacity: 0; transform: translateY(-30px); }
            100% { opacity: 1; transform: translateY(0); }
        }
        @keyframes fadeIn {
            0% { opacity: 0; }
            100% { opacity: 1; }
        }
        @keyframes ticker {
            0% { transform: translateX(100%); }
            100% { transform: translateX(-100%); }
        }
    </style>

    <div class="hero-section">
        <div class="hero-content">
            <div class="hero-title">AI-Powered Financial Intelligence</div>
            <div class="hero-subtitle">Your personalized roadmap to financial success</div>
        </div>
    </div>
    """, unsafe_allow_html=True)





    # Global styles for the entire app
    st.markdown("""
    <style>
        /* ====== General Styles ====== */
        @import url('https://fonts.googleapis.com/css2?family=Roboto+Slab:wght@400;700&family=Source+Sans+Pro:wght@400;600&family=Exo+2:wght@500&family=Merriweather:wght@700&display=swap');

        .main {
            background: linear-gradient(135deg, #f8fafc, #f0f4ff);
            animation: backgroundShift 10s infinite alternate;
        }

        @keyframes backgroundShift {
            0% { background-position: 0% 50%; }
            100% { background-position: 100% 50%; }
        }

        body {
            color: #1f2937 !important;
            font-family: 'Poppins', sans-serif !important;
        }

        /* ====== Sidebar (Luxury Glassmorphism) ====== */
        [data-testid="stSidebar"] {
            background: #2563EB !important;
            color: white !important;
            backdrop-filter: blur(18px);
            border-radius: 35px !important;
            padding: 32px !important;
            box-shadow: 10px 10px 35px rgba(0, 0, 0, 0.2);
            transition: all 0.5s ease-in-out;
            border: 2px solid rgba(255,255,255,0.2) !important;
        }

        [data-testid="stSidebar"]:hover {
            background: rgba(37,99,235,0.9) !important;
            box-shadow: 12px 12px 40px rgba(0, 0, 0, 0.3);
        }

        .stSidebar > h1, .stSidebar > h2 {
            color: white !important;
            font-weight: bold !important;
            text-shadow: 1px 1px 10px rgba(0, 0, 0, 0.3);
        }

        /* Sidebar text elements */
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] ul,
        [data-testid="stSidebar"] li {
            color: white !important;
        }

        [data-testid="stSidebar"] .st-emotion-cache-1v7f65g {
            color: rgba(255,255,255,0.8) !important;
        }
        .stSidebar > h1, .stSidebar > h2 {
            color: #2563EB !important;
            font-weight: bold !important;
            text-shadow: 1px 1px 10px rgba(0, 0, 0, 0.2);
        }

        /* ====== Tabs (Premium Minimalist Design) ====== */
        [data-baseweb="tab-list"] {
            display: flex !important;
            gap: 30px !important;
            justify-content: center !important;
            margin-bottom: 30px !important;
        }

        [data-baseweb="tab"] {
            background: rgba(255, 255, 255, 0.75) !important;
            backdrop-filter: blur(20px);
            border-radius: 22px !important;
            padding: 22px 38px !important;
            margin: 12px !important;
            transition: all 0.5s ease-in-out !important;
            font-weight: bold !important;
            font-size: 19px !important;
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.18);
        }

        [data-baseweb="tab"]:hover {
            background: rgba(255, 255, 255, 0.95) !important;
            transform: scale(1.05);
        }

        [aria-selected="true"] {
            background: linear-gradient(90deg, #2563EB 0%, #1d4edd 100%) !important;
            color: white !important;
            font-weight: bold !important;
            box-shadow: 0 10px 22px rgba(37, 99, 235, 0.5);
        }

        /* ====== Tab-Specific Styles ====== */
        /* All tabs now use professional blue theme */
        div[data-baseweb~="tab-panel"] {
            border-radius: 30px !important;
            padding: 40px !important;
            box-shadow: 0 12px 24px rgba(0,0,0,0.08) !important;
            border: 3px solid #2563EB !important;
            margin-top: 20px !important;
        }

        div[data-baseweb~="tab-panel"] h3 {
            color: #2563EB !important;
            border-bottom: 3px solid #2563EB !important;
            padding-bottom: 10px !important;
            text-shadow: 2px 2px 4px rgba(37, 99, 235, 0.15);
        }

        /* Tab 1: Financial Advice */
        div[data-baseweb~="tab-panel"]:nth-child(1) {
            background: linear-gradient(135deg, #f8f9fa 0%, #e8f0ff 100%) !important;
        }

        /* Tab 2: Stock Insights */
        div[data-baseweb~="tab-panel"]:nth-child(2) {
            background: linear-gradient(135deg, #f0f7ff 0%, #e0edff 100%) !important;
        }

        /* Tab 3: AI Chatbot */
        div[data-baseweb~="tab-panel"]:nth-child(3) {
            background: linear-gradient(135deg, #e8f0ff 0%, #d8e8ff 100%) !important;
        }

        /* Tab 4: Portfolio Management */
        div[data-baseweb~="tab-panel"]:nth-child(4) {
            background: linear-gradient(135deg, #e0e8ff 0%, #d0dcff 100%) !important;
        }

        /* ====== Input Fields ====== */
        .stTextInput, .stNumberInput, .stSelectbox {
            border: 2px solid !important;
            border-image: linear-gradient(30deg, #2563EB, #1d4edd) 1 !important;
            background: rgba(255,255,255,0.9) !important;
            backdrop-filter: blur(10px);
            margin-bottom: 10px !important;
        }

        .stTextInput:focus, .stNumberInput:focus, .stSelectbox:focus {
            border:3px solid #2563EB !important;
            box-shadow: 0 0 16px rgba(37, 99, 235, 0.6) !important;
        }

        /* ====== Buttons ====== */
        .stButton>button {
            background: linear-gradient(45deg, #2563EB, #1d4edd) !important;
            border: none !important;
            color: white !important;
            border-radius: 22px !important;
            padding: 20px 48px !important;
            font-size: 21px !important;
            font-weight: bold !important;
            transition: all 0.5s ease-in-out !important;
            box-shadow: 0 14px 28px rgba(37, 99, 235, 0.55);
        }

        .stButton>button:hover {
            transform: translateY(-6px);
            box-shadow: 0 16px 34px rgba(37, 99, 235, 0.65) !important;
        }

        /* ====== Scrollbar ====== */
        ::-webkit-scrollbar-thumb {
            background: linear-gradient(135deg, #2563EB, #1d4edd);
        }

        /* ====== Chatbot Bubbles ====== */
        .bot-message {
            background: #e8f0ff !important;
        }

        .user-message {
            background: #d8e8ff !important;
        }

        /* ====== Consistent Professional Colors ====== */
        .fin-metric-box {
            background: rgba(255, 255, 255, 0.95) !important;
        }

        .stPlotlyChart {
            background: rgba(255, 255, 255, 0.98) !important;
        }

        /* ====== Hover Effects ====== */
        .hover-card {
            transition: all 0.3s ease;
            transform: translateY(0);
        }
        .hover-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 30px rgba(0,0,0,0.15) !important;
        }

        /* ====== Loading Animation ====== */
        .custom-spinner {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .spinner {
            width: 50px;
            height: 50px;
            border: 5px solid #f0f0f0;
            border-top: 5px solid #2563EB;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-bottom: 10px;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
    """, unsafe_allow_html=True)

    # Sidebar
    st.sidebar.title(f"Welcome, {st.session_state.username}")
    st.sidebar.markdown(
        "Navigate through the tabs below for real-time stock data, personalized financial advice, and AI-powered insights!"
    )
    st.sidebar.subheader("Features")
    st.sidebar.markdown("1. 📈 Stock Insights - Get real-time stock data.")
    st.sidebar.markdown("2. 💼 Financial Advice - Receive personalized financial advice.")
    st.sidebar.markdown("3. 💬 AI Finance Chatbot - Ask financial questions.")
    st.sidebar.markdown("4. 📊 Portfolio Management - Track and manage your investments.")



    if st.sidebar.button("🚪 Logout"):
        st.session_state.authenticated = False
        st.session_state.landing_viewed = False
        st.rerun()

    # Helper functions
    def get_nifty_110_stocks():
        return [
            'RELIANCE.NS', 'TCS.NS', 'HDFC.NS', 'INFY.NS', 'KOTAKBANK.NS',
            'ICICIBANK.NS', 'ITC.NS', 'HDFCBANK.NS', 'SBIN.NS', 'BAJAJ-AUTO.NS',
            'ASIANPAINT.NS', 'HINDUNILVR.NS', 'LT.NS', 'MARUTI.NS', 'AXISBANK.NS',
            'BHARTIARTL.NS', 'HEROMOTOCO.NS', 'HCLTECH.NS', 'TATAMOTORS.NS', 'TATASTEEL.NS',
            'WIPRO.NS', 'JSWSTEEL.NS', 'DRREDDY.NS', 'SUNPHARMA.NS', 'NESTLEIND.NS',
            'ULTRACEMCO.NS', 'DIVISLAB.NS', 'CIPLA.NS', 'BAJAJFINSV.NS', 'BAJFINANCE.NS',
            'POWERGRID.NS', 'NTPC.NS', 'ONGC.NS', 'GAIL.NS', 'GRASIM.NS',
            'HINDALCO.NS', 'HINDZINC.NS', 'ADANIPORTS.NS', 'ADANIGREEN.NS', 'ADANITRANS.NS',
            'ADANIENT.NS', 'SHREECEM.NS', 'LUPIN.NS', 'PIDILITIND.NS', 'GODREJCP.NS',
            'VEDL.NS', 'VOLTAS.NS', 'TECHM.NS', 'INDUSINDBK.NS', 'SBILIFE.NS',
            'HDFCLIFE.NS', 'JSWENERGY.NS', 'MOTHERSUMI.NS', 'SHRIRAMFIN.NS', 'TORNTPHARM.NS',
            'UPL.NS', 'TITAN.NS', 'CHOLAFIN.NS', 'COALINDIA.NS', 'RBLBANK.NS',
            'BAJAJHLDNG.NS', 'DMART.NS', 'M&M.NS', 'APOLLOHOSP.NS', 'BRITANNIA.NS',
            'DABUR.NS', 'EICHERMOT.NS', 'GICHOUSING.NS', 'ICICILOMBARD.NS', 'MRF.NS',
            'PAGEIND.NS', 'PNB.NS', 'REC.NS', 'SBICARD.NS', 'TATACONSUM.NS',
            'TATACHEM.NS', 'TATAPOWER.NS', 'WHIRLPOOL.NS', 'CADILAHC.NS', 'CONCOR.NS',
            'DLF.NS', 'ESCORTS.NS', 'GODREJPROP.NS', 'HINDPETRO.NS', 'LICHSGFIN.NS',
            'MFSL.NS', 'NHPC.NS', 'SRF.NS', 'TATAELXSI.NS', 'VGUARD.NS',
            'VSTIND.NS', 'ZENSARTECH.NS', 'CUMMINSIND.NS', 'CHEMFIN.NS', 'FINCABLE.NS',
            'PEL.NS', 'ARVIND.NS', 'VEDANTA.NS', 'HDFCERGO.NS', 'KIRLOSIND.NS',
            'ORIENTFIN.NS', 'PVR.NS', 'SRTRANSFIN.NS', 'ACC.NS', 'BHARATFORG.NS',
            'COLPAL.NS', 'DIXON.NS', 'CASTROLIND.NS', 'TATAMTRDVR.NS', 'MINDTREE.NS'
        ]

    def replace_unsupported_chars(text):
        replacements = {
            "\u20B9": "INR",  # Replace ₹ with INR
            "\u2019": "'",  # Right single quote
            "\u2018": "'",  # Left single quote
            "\u201C": '"',  # Left double quote
            "\u201D": '"',  # Right double quote
            "\u2013": "-",  # En dash
            "\u2014": "-"  # Em dash
        }
        for char, replacement in replacements.items():
            text = text.replace(char, replacement)
        return text

    def create_financial_chart(income, savings, debt, expenses):
        labels = ["Income", "Savings", "Debt", "Expenses"]
        values = [income, savings, debt, expenses]

        fig, ax = plt.subplots()
        ax.pie(values, labels=labels, autopct="%1.1f%%",
               colors=["#4CAF50", "#2196F3", "#F44336", "#FFC107"])
        ax.set_title("Financial Distribution")

        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format="png", dpi=300, bbox_inches='tight')
        plt.close(fig)
        img_buffer.seek(0)
        return img_buffer

    def generate_pdf_report(income, savings, debt, expenses, advice):
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        # Add header with border
        pdf.set_fill_color(240, 240, 240)
        pdf.rect(5, 5, 200, 25, style='F')
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(200, 10, "AI FINANCE ADVISOR REPORT", ln=True, align='C')
        pdf.set_font("Arial", 'I', 10)
        pdf.cell(200, 5, f"Date: {datetime.now().strftime('%B %d, %Y %I:%M %p')}", ln=True, align='C')
        pdf.ln(15)

        # Financial Details section
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(200, 10, "Financial Summary", ln=True)
        pdf.set_font("Arial", size=12)

        # Add financial details with better formatting
        col_width = 95
        row_height = 10

        # Header row
        pdf.set_fill_color(220, 220, 220)
        pdf.cell(col_width, row_height, "Category", border=1, fill=True)
        pdf.cell(col_width, row_height, "Amount (INR)", border=1, fill=True, ln=True)

        # Data rows
        pdf.cell(col_width, row_height, "Income", border=1)
        pdf.cell(col_width, row_height, f"{income:,.2f}", border=1, ln=True)
        pdf.cell(col_width, row_height, "Savings", border=1)
        pdf.cell(col_width, row_height, f"{savings:,.2f}", border=1, ln=True)
        pdf.cell(col_width, row_height, "Debt", border=1)
        pdf.cell(col_width, row_height, f"{debt:,.2f}", border=1, ln=True)
        pdf.cell(col_width, row_height, "Expenses", border=1)
        pdf.cell(col_width, row_height, f"{expenses:,.2f}", border=1, ln=True)

        pdf.ln(15)

        # Add Financial Chart
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(200, 10, "Financial Distribution", ln=True)
        chart_image = create_financial_chart(income, savings, debt, expenses)

        # Temporary file handling
        temp_chart_path = "temp_chart.png"
        with open(temp_chart_path, "wb") as f:
            f.write(chart_image.getbuffer())

        pdf.image(temp_chart_path, x=30, w=150)
        pdf.ln(80)

        # Add AI Advice with better formatting
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(200, 10, "AI-Generated Financial Advice", ln=True)
        pdf.set_font("Arial", size=12)

        # Add light gray background for advice section
        pdf.set_fill_color(245, 245, 245)
        pdf.rect(10, pdf.get_y(), 190, 60, style='F')
        pdf.multi_cell(0, 8, replace_unsupported_chars(advice))

        # Add footer
        pdf.set_y(-15)
        pdf.set_font("Arial", 'I', 8)
        pdf.cell(0, 10, f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", 0, 0, 'C')

        # Finalize PDF
        pdf_output = pdf.output(dest="S").encode("latin1", "replace")
        pdf_buffer = io.BytesIO(pdf_output)

        # Cleanup temporary file
        import os
        if os.path.exists(temp_chart_path):
            os.remove(temp_chart_path)

        return pdf_buffer
    def fetch_stock_data(symbol):
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            hist = stock.history(period="2y")
            return {
                "company": info.get("longName", "N/A"),
                "sector": info.get("sector", "N/A"),
                "current_price": info.get("currentPrice", "N/A"),
                "market_cap": info.get("marketCap", "N/A"),
                "pe_ratio": info.get("trailingPE", "N/A"),
                "dividend_yield": info.get("dividendYield", "N/A"),
                "profit_loss": info.get("regularMarketChange", "N/A"),
                "profit_loss_percent": info.get("regularMarketChangePercent", "N/A"),
                "history": hist
            }
        except Exception as e:
            return {"error": str(e)}

    def predict_stock_price(symbol):
        stock = yf.Ticker(symbol)
        hist = stock.history(period="5y")
        hist['Date'] = hist.index
        hist['Days'] = (hist['Date'] - hist['Date'].min()).dt.days
        X = hist[['Days']]
        y = hist['Close']
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        model = LinearRegression()
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        future_days = np.array([X['Days'].max() + i for i in range(1, 31)]).reshape(-1, 1)
        future_prices = model.predict(future_days)
        return future_prices, mse

    # Create Tabs
    tab1, tab2, tab3, tab4 = st.tabs(
        ["💼 Financial Advice", "📈 Stock Insights", "💬 AI Finance Chatbot", "📊 Portfolio Management"])

    # ------------------- Tab 1: Financial Advice -------------------
    with tab1:
        # Add chatbot pop-up icon
        st.markdown(
            """
            <style>
                .chatbot-icon {
                    position: fixed;
                    bottom: 20px;
                    right: 20px;
                    z-index: 1000;
                    cursor: pointer;
                    background-color: #2196F3;
                    color: white;
                    border-radius: 50%;
                    width: 70px;
                    height: 70px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                    transition: transform 0.2s, box-shadow 0.2s;
                    font-size: 32px;
                    animation: pulse 2s infinite;
                }
                .chatbot-icon:hover {
                    transform: scale(1.1);
                    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.2);
                    animation: none;
                }
                @keyframes pulse {
                    0% { transform: scale(1); }
                    50% { transform: scale(1.1); }
                    100% { transform: scale(1); }
                }
                .chatbot-icon::after {
                    content: "Chat with AI";
                    position: absolute;
                    top: -30px;
                    right: 0;
                    background-color: #2196F3;
                    color: white;
                    padding: 5px 10px;
                    border-radius: 5px;
                    font-size: 14px;
                    opacity: 0;
                    transition: opacity 0.3s;
                    pointer-events: none;
                }
                .chatbot-icon:hover::after {
                    opacity: 1;
                }
            </style>
            <div class="chatbot-icon" onclick="window.location.href='#tab3';">
                🤖
            </div>
            """,
            unsafe_allow_html=True
        )

        if st.session_state.get("redirect_to_tab3", False):
            st.session_state.selected_tab = "💬 AI Finance Chatbot"
            st.session_state.redirect_to_tab3 = False

        st.subheader("💼 Personalized Financial Advice")

        # Initialize session state for user inputs and advice
        if "user_profile" not in st.session_state:
            st.session_state.user_profile = {
                'name': st.session_state.username,
                'age': 35,
                'income': 100000,
                'savings': 65000,
                'debt': 25000,
                'expenses': 10000,
                'risk_pref': "Conservative",
                'risk_percentage': 0,
                'debt_to_income': 0,
                'savings_ratio': 0,
                'expenses_ratio': 0
            }
        if "advice" not in st.session_state:
            st.session_state.advice = ""

        # Display personalized welcome message
        if st.session_state.user_profile['name']:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #2563EB, #1d4edd); color: white; border-radius: 15px; padding: 25px; margin-bottom: 30px; box-shadow: 0 10px 20px rgba(37,99,235,0.3);">
                <h2 style="margin-top: 0;">Welcome, {st.session_state.user_profile['name']}!</h2>
                <p style="font-size: 1.1rem;">We've prepared personalized insights based on your financial profile:</p>
            </div>
            """, unsafe_allow_html=True)

        # Pre-fill inputs using session state
        col1, col2 = st.columns(2)
        with col1:
            age = st.number_input("📅 Age:", min_value=18, max_value=100, step=1,
                                  value=st.session_state.user_profile['age'],
                                  help="Enter your current age for personalized planning")
            income = st.number_input("💵 Monthly Income (₹):", min_value=0, step=1000,
                                     value=st.session_state.user_profile['income'],
                                     format="%d", help="Gross monthly income before taxes")
            savings = st.number_input("🏦 Current Savings (₹):", min_value=0, step=1000,
                                      value=st.session_state.user_profile['savings'],
                                      format="%d", help="Total liquid assets and investments")
        with col2:
            debt = st.number_input("💳 Current Debt (₹):", min_value=0, step=1000,
                                   value=st.session_state.user_profile['debt'],
                                   format="%d", help="Total outstanding debt including loans")
            expenses = st.number_input("🛒 Monthly Expenses (₹):", min_value=0, step=1000,
                                       value=st.session_state.user_profile['expenses'],
                                       format="%d", help="Average monthly spending")
            risk_pref = st.selectbox("📈 Risk Preference Category:", ["Conservative", "Moderate", "Aggressive"],
                                     index=["Conservative", "Moderate", "Aggressive"].index(
                                         st.session_state.user_profile['risk_pref']),
                                     help="Your investment risk tolerance level")

            # Risk percentage number input
            risk_percentage = st.number_input("📊 Risk Percentage Allocation (0-100%):",
                                              min_value=0,
                                              max_value=100,
                                              value=st.session_state.user_profile['risk_percentage'],
                                              step=1,
                                              help="What percentage of your portfolio are you willing to allocate to higher-risk investments? (Enter a number between 0-100)")

        if st.button("Generate Smart Advice", key="generate_advice"):
            with st.spinner("🔍 Analyzing your financial profile..."):
                time.sleep(2)

                # Calculate financial ratios
                debt_to_income = round((debt / income) * 100, 2) if income > 0 else 0
                savings_ratio = round((savings / income) * 100, 2) if income > 0 else 0
                expenses_ratio = round((expenses / income) * 100, 2) if income > 0 else 0

                # Update session state with user inputs
                st.session_state.user_profile = {
                    'name': st.session_state.user_profile['name'],
                    'age': age,
                    'income': income,
                    'savings': savings,
                    'debt': debt,
                    'expenses': expenses,
                    'risk_pref': risk_pref,
                    'risk_percentage': risk_percentage,
                    'debt_to_income': debt_to_income,
                    'savings_ratio': savings_ratio,
                    'expenses_ratio': expenses_ratio
                }

                # Generate advice using the model with enhanced prompt
                prompt = (
                    f"Provide detailed, personalized financial advice for {st.session_state.user_profile['name']}, a {age}-year-old with the following profile:\n"
                    f"- Monthly Income: ₹{income:,}\n"
                    f"- Current Savings: ₹{savings:,}\n"
                    f"- Current Debt: ₹{debt:,}\n"
                    f"- Monthly Expenses: ₹{expenses:,}\n"
                    f"- Risk Preference: {risk_pref} (with {risk_percentage}% allocated to higher-risk investments)\n"
                    f"- Debt-to-Income Ratio: {debt_to_income}%\n"
                    f"- Savings Ratio: {savings_ratio}%\n\n"
                    f"Provide comprehensive advice that:\n"
                    f"1. Starts with a personalized greeting addressing {st.session_state.user_profile['name']} by name\n"
                    f"2. Clearly explains what their risk percentage means for their investment strategy\n"
                    f"3. Provides specific recommendations for debt management if applicable\n"
                    f"4. Suggests concrete savings and investment strategies based on their risk percentage\n"
                    f"5. Includes actionable steps they can take immediately\n"
                    f"6. Ends with motivational encouragement\n"
                    f"Make the advice relatable, practical, and tailored to their exact numbers."
                )
                advice = model.generate_content(prompt)
                st.session_state.advice = advice.text.strip()

        if st.session_state.advice:
            # Remove asterisks from the advice text
            advice_text = st.session_state.advice.replace("*", "")

            # Display Financial Health Metrics
            st.markdown("### 📊 Financial Health Metrics")
            m1, m2, m3, m4 = st.columns(4)
            with m1:
                st.markdown(f"""
                <div class="fin-metric-box hover-card" style="border-color: #e74c3c;">
                    <div class="metric-icon">📉</div>
                    <h4>Debt/Income</h4>
                    <h2 style="color: #e74c3c;">{st.session_state.user_profile['debt_to_income']}%</h2>
                </div>
                """, unsafe_allow_html=True)
            with m2:
                st.markdown(f"""
                <div class="fin-metric-box hover-card" style="border-color: #27ae60;">
                    <div class="metric-icon">💰</div>
                    <h4>Savings Ratio</h4>
                    <h2 style="color: #27ae60;">{st.session_state.user_profile['savings_ratio']}%</h2>
                </div>
                """, unsafe_allow_html=True)
            with m3:
                st.markdown(f"""
                <div class="fin-metric-box hover-card" style="border-color: #f39c12;">
                    <div class="metric-icon">💸</div>
                    <h4>Expenses Ratio</h4>
                    <h2 style="color: #f39c12;">{st.session_state.user_profile['expenses_ratio']}%</h2>
                </div>
                """, unsafe_allow_html=True)
            with m4:
                st.markdown(f"""
                <div class="fin-metric-box hover-card" style="border-color: #3498db;">
                    <div class="metric-icon">⚖</div>
                    <h4>Risk Allocation</h4>
                    <h2 style="color: #3498db;">{st.session_state.user_profile['risk_percentage']}%</h2>
                </div>
                """, unsafe_allow_html=True)

            # ------------------- Financial Distribution -------------------
            st.markdown("### 🥧 Financial Distribution")
            financial_data = {
                "Category": ["Savings", "Debt", "Expenses"],
                "Amount (₹)": [savings, debt, expenses]
            }
            df = pd.DataFrame(financial_data)

            # Create the pie chart only for Savings, Debt, and Expenses
            fig = px.pie(df, values="Amount (₹)", names="Category",
                         title="Financial Distribution (Excluding Income)",
                         color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig, use_container_width=True)


            # ------------------- Debt Repayment Plan -------------------
            st.markdown("### 🗓 Debt Repayment Plan")
            if debt > 0:
                total_debt_payment = st.number_input("Enter total debt payment (₹):", min_value=0, step=1000,
                                                     value=debt)
                monthly_payment = st.number_input("Enter monthly debt repayment (₹):", min_value=0, step=1000,
                                                  value=5000)
                interest_rate = st.number_input("Enter interest rate per annum (%):", min_value=0.0, step=0.1,
                                                value=10.0)

                if monthly_payment > 0:
                    # Calculate months to repay debt with interest
                    monthly_interest_rate = (interest_rate / 100) / 12
                    months_to_repay = 0
                    remaining_debt = total_debt_payment
                    total_interest_paid = 0

                    while remaining_debt > 0:
                        interest = remaining_debt * monthly_interest_rate
                        principal = monthly_payment - interest
                        if principal > remaining_debt:
                            principal = remaining_debt
                        remaining_debt -= principal
                        total_interest_paid += interest
                        months_to_repay += 1

                    # Display Debt Repayment Metrics
                    st.markdown(f"""
                    <div class="fin-metric-box hover-card" style="border-color: #e74c3c;">
                        <div class="metric-icon">⏳</div>
                        <h4>Months to Repay Debt</h4>
                        <h2 style="color: #e74c3c;">{months_to_repay:.1f} months</h2>
                    </div>
                    """, unsafe_allow_html=True)

                    # Display Monthly Loan EMI, Principal Amount, Interest Amount, and Total Amount Payable
                    st.markdown("#### 📊 Detailed Repayment Breakdown")
                    st.write(f"- Monthly Loan EMI: ₹{monthly_payment:,.0f}")
                    st.write(f"- Principal Amount: ₹{total_debt_payment:,.0f}")
                    st.write(f"- Interest Amount: ₹{total_interest_paid:,.0f}")
                    st.write(f"- Total Amount Payable: ₹{total_debt_payment + total_interest_paid:,.0f}")
                else:
                    st.warning("Please enter a valid monthly payment amount.")
            else:
                st.success("🎉 You have no debt to repay!")



            # ------------------- Ultra-Realistic CIBIL Score Simulator 2.0 -----------------
            # Custom CSS for enhanced styling
            st.markdown("""
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');

                * {
                    font-family: 'Inter', sans-serif;
                }

                .credit-header {
                    background: linear-gradient(135deg, #1a237e 0%, #283593 100%);
                    padding: 2rem;
                    border-radius: 15px;
                    color: white;
                    box-shadow: 0 8px 24px rgba(0,97,255,0.1);
                    margin-bottom: 2rem;
                    border: 1px solid rgba(255,255,255,0.1);
                }

                .metric-card {
                    background: rgba(255,255,255,0.95);
                    border-radius: 12px;
                    padding: 1.5rem;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
                    border-left: 5px solid #1a237e;
                    margin-bottom: 1.5rem;
                    transition: transform 0.2s;
                }

                .metric-card:hover {
                    transform: translateY(-3px);
                }

                .factor-card {
                    background: rgba(248,249,250,0.95);
                    border-radius: 10px;
                    padding: 1.25rem;
                    margin: 0.75rem 0;
                    border-left: 4px solid #6c757d;
                    box-shadow: 0 2px 6px rgba(0,0,0,0.03);
                }

                .positive-factor {
                    border-left: 4px solid #4CAF50;
                    background: linear-gradient(90deg, rgba(76,175,80,0.05) 0%, rgba(255,255,255,1) 100%);
                }

                .negative-factor {
                    border-left: 4px solid #F44336;
                    background: linear-gradient(90deg, rgba(244,67,54,0.05) 0%, rgba(255,255,255,1) 100%);
                }

                .improvement-tips {
                    background: linear-gradient(135deg, #fff3e0 0%, #ffffff 100%);
                    padding: 2rem;
                    border-radius: 12px;
                    margin-top: 2rem;
                    border-left: 4px solid #FF9800;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
                }

                .stButton>button {
                    background: linear-gradient(135deg, #1a237e 0%, #283593 100%);
                    color: white!important;
                    border: none;
                    padding: 20px 48px;
                    border-radius: 8px;
                    font-weight: 600;
                    transition: all 0.3s;
                }

                .stButton>button:hover {
                    transform: scale(1.05);
                    box-shadow: 0 8px 16px rgba(26,35,126,0.2);
                }

                .score-change-reason {
                    padding: 1rem;
                    border-radius: 8px;
                    margin: 1rem 0;
                    background: rgba(0,0,0,0.02);
                    border-left: 4px solid #9E9E9E;
                }

                .score-increase {
                    border-left: 4px solid #4CAF50;
                    background: rgba(76,175,80,0.05);
                }

                .score-decrease {
                    border-left: 4px solid #F44336;
                    background: rgba(244,67,54,0.05);
                }

                .timeline-marker {
                    position: absolute;
                    width: 100%;
                    height: 2px;
                    background: rgba(0,0,0,0.1);
                    top: 50%;
                    left: 0;
                }

                .timeline-container {
                    position: relative;
                    padding: 1rem 0;
                    margin: 2rem 0;
                }

                .timeline-event {
                    position: relative;
                    padding-left: 2rem;
                    margin-bottom: 1.5rem;
                }

                .timeline-dot {
                    position: absolute;
                    left: 0;
                    top: 0;
                    width: 20px;
                    height: 20px;
                    border-radius: 50%;
                    background: #1a237e;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: white;
                    font-size: 0.8rem;
                }
                }
            </style>
            """, unsafe_allow_html=True)

            # Header Section with Animated Gradient
            st.markdown("""
            <div class="credit-header">
                <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 1rem;">
                    <div style="background: rgba(255,255,255,0.1); padding: 10px; border-radius: 10px;">
                        📈
                    </div>
                    <div>
                        <h1 style="color:white; margin:0; font-size: 2rem;">CIBIL Score Master</h1>
                        <p style="color:rgba(255,255,255,0.9); margin:0;">Advanced AI-Powered Credit Health Analysis</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # User Inputs Section with Improved Layout
            with st.expander("📝 Enter Your Credit Profile", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    current_credit_score = st.slider(
                        "Current CIBIL Score", 300, 900, 750,
                        help="CIBIL scores range from 300-900 in India"
                    )

                    credit_utilization = st.slider(
                        "Credit Utilization Ratio (%)", 0, 100, 35,
                        help="Maintain below 30% for optimal scoring"
                    )

                    payment_history = st.selectbox(
                        "Payment History (Last 24 months)",
                        ["Perfect (0 late payments)",
                         "Good (1-2 late payments)",
                         "Fair (3-5 late payments)",
                         "Poor (6+ late payments)"]
                    )

                with col2:
                    credit_age = st.slider(
                        "Average Credit Age (Years)", 0, 30, 4,
                        help="Average age of all credit accounts"
                    )

                    credit_mix = st.selectbox(
                        "Credit Mix Diversity",
                        ["Excellent (3+ types)",
                         "Good (2 types)",
                         "Fair (1 type)",
                         "Poor (No active credit)"]
                    )

                    recent_inquiries = st.slider(
                        "Recent Credit Inquiries", 0, 10, 2,
                        help="Hard inquiries in last 6 months"
                    )

            # Advanced Financial Details
            with st.expander("🔍 Advanced Financial Parameters"):
                col3, col4 = st.columns(2)
                with col3:
                    total_debt = st.number_input(
                        "Total Outstanding Debt (₹)",
                        min_value=0, value=350000, step=5000
                    )

                    derogatory_marks = st.number_input(
                        "Derogatory Marks (7 years)", 0, 10, 0,
                        help="Defaults, bankruptcies, settlements"
                    )

                with col4:
                    credit_limit = st.number_input(
                        "Total Credit Limit (₹)",
                        min_value=0, value=800000, step=10000
                    )

                    overdue_amount = st.number_input(
                        "Current Overdue Amount (₹)",
                        min_value=0, value=0, step=1000
                    )

            # Realistic Simulation Logic
            if st.button("🚀 Generate Comprehensive Analysis", use_container_width=True):
                with st.spinner("Analyzing 58+ credit factors using AI..."):
                    # Enhanced Scoring Algorithm
                    score_components = {
                        'payment_history': {'weight': 0.35, 'impact': 0, 'reason': ''},
                        'credit_utilization': {'weight': 0.30, 'impact': 0, 'reason': ''},
                        'credit_age': {'weight': 0.15, 'impact': 0, 'reason': ''},
                        'credit_mix': {'weight': 0.10, 'impact': 0, 'reason': ''},
                        'new_credit': {'weight': 0.10, 'impact': 0, 'reason': ''}
                    }

                    # 1. Payment History Analysis
                    if "Perfect" in payment_history:
                        score_components['payment_history']['impact'] = 0
                        score_components['payment_history'][
                            'reason'] = "Perfect payment history (no late payments) maintains your score"
                    elif "Good" in payment_history:
                        penalty = -15 * (1 + 0.05 * current_credit_score / 100)
                        score_components['payment_history']['impact'] = penalty
                        score_components['payment_history'][
                            'reason'] = f"1-2 late payments in last 24 months reduces score by {abs(int(penalty))} points"
                    elif "Fair" in payment_history:
                        penalty = -40 * (1 + 0.08 * current_credit_score / 100)
                        score_components['payment_history']['impact'] = penalty
                        score_components['payment_history'][
                            'reason'] = f"3-5 late payments in last 24 months reduces score by {abs(int(penalty))} points"
                    else:
                        penalty = -80 * (1 + 0.1 * current_credit_score / 100)
                        score_components['payment_history']['impact'] = penalty
                        score_components['payment_history'][
                            'reason'] = f"6+ late payments significantly reduces score by {abs(int(penalty))} points"

                    # 2. Credit Utilization Impact Curve
                    util_curve = [
                        (0, -10, "Very low utilization doesn't demonstrate active credit usage"),
                        (10, 15, "Optimal utilization (10-30%) shows responsible credit usage"),
                        (30, 0, "At threshold (30%) - no positive or negative impact"),
                        (50, -25, "High utilization (30-50%) begins to negatively impact score"),
                        (75, -50, "Very high utilization (50-75%) significantly hurts score"),
                        (100, -75, "Maxed out credit (75-100%) severely impacts score")
                    ]

                    for threshold, impact, reason in util_curve:
                        if credit_utilization <= threshold:
                            adjusted_impact = impact * (current_credit_score / 800)
                            score_components['credit_utilization']['impact'] = adjusted_impact
                            if impact >= 0:
                                score_components['credit_utilization'][
                                    'reason'] = f"Utilization at {credit_utilization}% increases score by {int(adjusted_impact)} points ({reason})"
                            else:
                                score_components['credit_utilization'][
                                    'reason'] = f"Utilization at {credit_utilization}% decreases score by {abs(int(adjusted_impact))} points ({reason})"
                            break

                    # 3. Credit Age Calculation
                    age_multiplier = 1 + (credit_age ** 1.5) / 100
                    age_impact = 15 * np.log1p(credit_age) * age_multiplier
                    score_components['credit_age']['impact'] = age_impact
                    if credit_age < 3:
                        score_components['credit_age'][
                            'reason'] = f"Short credit history ({credit_age} years) limits score potential by {abs(int(age_impact))} points"
                    elif credit_age < 7:
                        score_components['credit_age'][
                            'reason'] = f"Moderate credit age ({credit_age} years) contributes {int(age_impact)} points"
                    else:
                        score_components['credit_age'][
                            'reason'] = f"Long credit history ({credit_age} years) boosts score by {int(age_impact)} points"

                    # 4. Credit Mix Evaluation
                    mix_map = {
                        "Excellent": (25, "Diverse credit mix (3+ types) demonstrates responsible management"),
                        "Good": (10, "Good credit mix (2 types) has minor positive impact"),
                        "Fair": (-5, "Limited credit mix (1 type) slightly reduces potential"),
                        "Poor": (-30, "No active credit accounts significantly limits score")
                    }
                    impact, reason = mix_map[credit_mix.split()[0]]
                    score_components['credit_mix']['impact'] = impact
                    score_components['credit_mix']['reason'] = f"{reason} ({'+' if impact >= 0 else ''}{impact} points)"

                    # 5. New Credit Impact
                    inquiry_penalty = -4 * recent_inquiries ** 1.2
                    score_components['new_credit']['impact'] = inquiry_penalty
                    if recent_inquiries == 0:
                        score_components['new_credit']['reason'] = "No recent inquiries - no impact"
                    elif recent_inquiries <= 2:
                        score_components['new_credit'][
                            'reason'] = f"{recent_inquiries} recent inquiries reduce score by {abs(int(inquiry_penalty))} points"
                    else:
                        score_components['new_credit'][
                            'reason'] = f"{recent_inquiries} recent inquiries significantly reduce score by {abs(int(inquiry_penalty))} points (appears credit hungry)"

                    # Calculate Composite Score
                    base_score = current_credit_score
                    weighted_impact = sum(comp['impact'] * comp['weight'] for comp in score_components.values())

                    # Additional Penalties
                    derogatory_penalty = -2 * derogatory_marks ** 1.5
                    overdue_penalty = -0.0005 * overdue_amount
                    penalties = derogatory_penalty + overdue_penalty

                    final_score = base_score + weighted_impact + penalties
                    final_score = max(300, min(900, int(final_score)))

                    # Generate Projection Curve with realistic fluctuations
                    months = 12
                    x = np.arange(months + 1)

                    # Create realistic trajectory based on user behavior
                    if final_score > current_credit_score:
                        # Improving score curve
                        y = current_credit_score + (final_score - current_credit_score) * (1 - np.exp(-x / 6))
                    else:
                        # Declining score curve
                        y = current_credit_score + (final_score - current_credit_score) * (1 - np.exp(-x / 3))

                    # Add realistic noise and plateaus
                    y += np.random.normal(0, 3, len(x))  # Small random fluctuations
                    for i in range(3, len(x), 3):
                        y[i:i + 2] = y[i - 1]  # Simulate plateaus where score doesn't change
                    y = np.clip(y, 300, 900).astype(int)

                    # Display Results with Enhanced Visuals
                    st.markdown(f"""
                    <div style='display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin: 2rem 0;'>
                        <div class="metric-card">
                            <div style="display: flex; align-items: center; gap: 10px;">
                                <div style="background: #e3f2fd; padding: 8px; border-radius: 8px;">📅</div>
                                <div>
                                    <h3 style='margin: 0; font-size: 0.9rem; color: #616161;'>Current Score</h3>
                                    <h2 style='margin: 0; color: #1a237e; font-size: 2rem;'>{current_credit_score}</h2>
                                </div>
                            </div>
                        </div>
                        <div class="metric-card">
                            <div style="display: flex; align-items: center; gap: 10px;">
                                <div style="background: #e8f5e9; padding: 8px; border-radius: 8px;">📈</div>
                                <div>
                                    <h3 style='margin: 0; font-size: 0.9rem; color: #616161;'>Projected Score</h3>
                                    <h2 style='margin: 0; color: {'#4CAF50' if final_score >= current_credit_score else '#F44336'}; font-size: 2rem;'>
                                        {final_score}{'▲' if final_score > current_credit_score else '▼' if final_score < current_credit_score else ''}
                                    </h2>
                                </div>
                            </div>
                        </div>
                        <div class="metric-card">
                            <div style="display: flex; align-items: center; gap: 10px;">
                                <div style="background: #fff3e0; padding: 8px; border-radius: 8px;">📉</div>
                                <div>
                                    <h3 style='margin: 0; font-size: 0.9rem; color: #616161;'>Score Change</h3>
                                    <h2 style='margin: 0; color: {'#4CAF50' if (final_score - current_credit_score) >= 0 else '#F44336'}; font-size: 2rem;'>
                                        {final_score - current_credit_score:+}
                                    </h2>
                                </div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    # Score Change Reasons
                    st.markdown("### 📊 Score Change Breakdown")

                    for factor, data in score_components.items():
                        if data['impact'] != 0:
                            reason_class = "score-increase" if data['impact'] > 0 else "score-decrease"
                            st.markdown(f"""
                            <div class="score-change-reason {reason_class}">
                                <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                                    <strong>{' '.join(factor.split('_')).title()}</strong>
                                    <span style="color: {'#4CAF50' if data['impact'] > 0 else '#F44336'}">
                                        {'+' if data['impact'] > 0 else ''}{int(data['impact'])}
                                    </span>
                                </div>
                                <div style="font-size: 0.9rem; color: #424242;">{data['reason']}</div>
                            </div>
                            """, unsafe_allow_html=True)

                    # Additional penalties
                    if derogatory_penalty < 0:
                        st.markdown(f"""
                        <div class="score-change-reason score-decrease">
                            <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                                <strong>Derogatory Marks</strong>
                                <span style="color: #F44336">{int(derogatory_penalty)}</span>
                            </div>
                            <div style="font-size: 0.9rem; color: #424242;">
                                {derogatory_marks} derogatory mark(s) on your credit report (defaults, bankruptcies, etc.)
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                    if overdue_penalty < 0:
                        st.markdown(f"""
                        <div class="score-change-reason score-decrease">
                            <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                                <strong>Overdue Amount</strong>
                                <span style="color: #F44336">{int(overdue_penalty)}</span>
                            </div>
                            <div style="font-size: 0.9rem; color: #424242;">
                                ₹{overdue_amount:,} in overdue payments negatively impacts your score
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                    # Interactive Projection Chart with Key Events
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=[datetime.now() + timedelta(days=30 * i) for i in range(13)],
                        y=y,
                        mode='lines+markers',
                        line=dict(color='#1a237e', width=4, shape='spline'),
                        marker=dict(size=8, color='#1a237e'),
                        name='CIBIL Trajectory',
                        hovertemplate="<b>%{x|%b %Y}</b><br>Score: %{y}<extra></extra>"
                    ))

                    # Add key events to the timeline
                    key_events = []

                    # Credit utilization improvement opportunity
                    if credit_utilization > 30:
                        improvement_month = min(3, months)
                        improvement_amount = int((credit_utilization - 30) / 100 * credit_limit)
                        key_events.append({
                            'month': improvement_month,
                            'text': f"Credit utilization improves to 30% (₹{improvement_amount:,} payment)",
                            'impact': 15
                        })

                    # Payment history impact
                    if "Perfect" not in payment_history:
                        key_events.append({
                            'month': 6,
                            'text': "6 months of on-time payments improves payment history",
                            'impact': 10
                        })

                    # Credit age milestone
                    if credit_age < 5:
                        key_events.append({
                            'month': 12,
                            'text': f"Credit age reaches {credit_age + 1} years",
                            'impact': 5
                        })

                    # Add event markers
                    for event in key_events:
                        fig.add_annotation(
                            x=datetime.now() + timedelta(days=30 * event['month']),
                            y=y[event['month']] + 15,
                            text=event['text'],
                            showarrow=True,
                            arrowhead=1,
                            ax=0,
                            ay=-40,
                            bgcolor="#FFFFFF",
                            bordercolor="#1a237e",
                            borderwidth=1,
                            font=dict(size=10)
                        )

                    fig.update_layout(
                        title="12-Month AI-Projected Credit Health with Key Events",
                        template="plotly_white",
                        height=500,
                        hoverlabel=dict(bgcolor="white", font_size=14),
                        xaxis=dict(title="Timeline", gridcolor="#f0f0f0"),
                        yaxis=dict(title="CIBIL Score", range=[max(300, min(y) - 50), min(900, max(y) + 50)],
                                   gridcolor="#f0f0f0"),
                        margin=dict(l=50, r=50, t=80, b=50)
                    )
                    st.plotly_chart(fig, use_container_width=True)

                    # Timeline of Key Factors
                    st.markdown("### ⏳ Credit Health Timeline")
                    st.markdown("<div class='timeline-container'><div class='timeline-marker'></div>",
                                unsafe_allow_html=True)

                    # Current situation
                    st.markdown("""
                    <div class="timeline-event">
                        <div class="timeline-dot">Now</div>
                        <div style="background: #F5F5F5; padding: 1rem; border-radius: 8px;">
                            <h4 style="margin-top: 0;">Current Credit Profile</h4>
                            <p style="margin-bottom: 0;">Score: {current_credit_score} | Utilization: {credit_utilization}% | Credit Age: {credit_age} yrs</p>
                        </div>
                    </div>
                    """.format(current_credit_score=current_credit_score, credit_utilization=credit_utilization,
                               credit_age=credit_age), unsafe_allow_html=True)

                    # Future milestones
                    milestones = [
                        (1, "1 month of on-time payments", "Payment history begins to improve"),
                        (3, "Credit utilization optimization", "Pay down balances to <30% for maximum impact"),
                        (6, "Credit age milestone", "Older accounts improve your average credit age"),
                        (12, "12-month review", "Derogatory marks age and have less impact")
                    ]

                    for month, title, description in milestones:
                        st.markdown(f"""
                        <div class="timeline-event">
                            <div class="timeline-dot">{month}M</div>
                            <div style="background: #F5F5F5; padding: 1rem; border-radius: 8px;">
                                <h4 style="margin-top: 0;">{title}</h4>
                                <p style="margin-bottom: 0;">{description}</p>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                    st.markdown("</div>", unsafe_allow_html=True)

                    # Dynamic Improvement Recommendations
                    st.markdown("""
                    <div class="improvement-tips">
                        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 1.5rem;">
                            <div style="background: #FF9800; padding: 8px; border-radius: 8px;">💡</div>
                            <h3 style="margin:0; color: #FF9800;">AI-Powered Credit Optimization Strategy</h3>
                        </div>
                        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem;">
                    """, unsafe_allow_html=True)

                    # Generate Recommendations Based on Profile
                    recommendations = []

                    if credit_utilization > 30:
                        target_util = max(30, credit_utilization * 0.7)
                        payment_needed = int((credit_utilization - target_util) / 100 * credit_limit)
                        rec = f"""
                        <div class="factor-card positive-factor">
                            <div style="display: flex; gap: 10px; align-items: start;">
                                <div style="color: #4CAF50;">✔️</div>
                                <div>
                                    <h4 style="margin:0;">Reduce Credit Utilization</h4>
                                    <p style="margin:0.3rem 0; font-size: 0.9rem;">Current: {credit_utilization}% → Target: {target_util}%</p>
                                    <div style="background: rgba(0,0,0,0.05); padding: 0.5rem; border-radius: 6px; margin-top: 0.5rem;">
                                        <p style="margin:0; font-size:0.85em; color: #666;">
                                        <strong>Action:</strong> Pay down ₹{payment_needed:,} across your cards<br>
                                        <strong>Impact:</strong> +{min(40, int((credit_utilization - 30) * 0.8))} points potential
                                        </p>
                                    </div>
                                </div>
                            </div>
                        </div>
                        """
                        recommendations.append(rec)

                    if "Perfect" not in payment_history:
                        rec = f"""
                        <div class="factor-card positive-factor">
                            <div style="display: flex; gap: 10px; align-items: start;">
                                <div style="color: #4CAF50;">⏰</div>
                                <div>
                                    <h4 style="margin:0;">Payment Automation</h4>
                                    <p style="margin:0.3rem 0; font-size: 0.9rem;">Setup auto-pay for minimum payments</p>
                                    <div style="background: rgba(0,0,0,0.05); padding: 0.5rem; border-radius: 6px; margin-top: 0.5rem;">
                                        <p style="margin:0; font-size:0.85em; color: #666;">
                                        <strong>Action:</strong> Enable auto-pay through your bank<br>
                                        <strong>Impact:</strong> Prevents future late payments (35% weighting)
                                        </p>
                                    </div>
                                </div>
                            </div>
                        </div>
                        """
                        recommendations.append(rec)

                    if credit_age < 5:
                        rec = f"""
                        <div class="factor-card positive-factor">
                            <div style="display: flex; gap: 10px; align-items: start;">
                                <div style="color: #4CAF50;">🕰️</div>
                                <div>
                                    <h4 style="margin:0;">Increase Credit Age</h4>
                                    <p style="margin:0.3rem 0; font-size: 0.9rem;">Current average: {credit_age} years</p>
                                    <div style="background: rgba(0,0,0,0.05); padding: 0.5rem; border-radius: 6px; margin-top: 0.5rem;">
                                        <p style="margin:0; font-size:0.85em; color: #666;">
                                        <strong>Action:</strong> Keep oldest accounts open<br>
                                        <strong>Impact:</strong> +3-5 points per year of additional history
                                        </p>
                                    </div>
                                </div>
                            </div>
                        </div>
                        """
                        recommendations.append(rec)

                    if recent_inquiries > 2:
                        rec = f"""
                        <div class="factor-card positive-factor">
                            <div style="display: flex; gap: 10px; align-items: start;">
                                <div style="color: #4CAF50;">🛑</div>
                                <div>
                                    <h4 style="margin:0;">Limit New Credit Applications</h4>
                                    <p style="margin:0.3rem 0; font-size: 0.9rem;">Recent inquiries: {recent_inquiries}</p>
                                    <div style="background: rgba(0,0,0,0.05); padding: 0.5rem; border-radius: 6px; margin-top: 0.5rem;">
                                        <p style="margin:0; font-size:0.85em; color: #666;">
                                        <strong>Action:</strong> Avoid new applications for 6 months<br>
                                        <strong>Impact:</strong> Inquiries stop affecting score after 12 months
                                        </p>
                                    </div>
                                </div>
                            </div>
                        </div>
                        """
                        recommendations.append(rec)

                    if derogatory_marks > 0:
                        rec = f"""
                        <div class="factor-card positive-factor">
                            <div style="display: flex; gap: 10px; align-items: start;">
                                <div style="color: #4CAF50;">🔍</div>
                                <div>
                                    <h4 style="margin:0;">Address Derogatory Marks</h4>
                                    <p style="margin:0.3rem 0; font-size: 0.9rem;">Negative items: {derogatory_marks}</p>
                                    <div style="background: rgba(0,0,0,0.05); padding: 0.5rem; border-radius: 6px; margin-top: 0.5rem;">
                                        <p style="margin:0; font-size:0.85em; color: #666;">
                                        <strong>Action:</strong> Dispute inaccuracies or negotiate pay-for-delete<br>
                                        <strong>Impact:</strong> Removal can boost score by 20-50 points
                                        </p>
                                    </div>
                                </div>
                            </div>
                        </div>
                        """
                        recommendations.append(rec)

                    st.markdown("\n".join(recommendations[:4]), unsafe_allow_html=True)
                    st.markdown("</div></div>", unsafe_allow_html=True)

            from streamlit_extras.metric_cards import style_metric_cards
            from streamlit_extras.grid import grid

            # ------------------- Custom Styles -------------------
            st.markdown("""
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');

                :root {
                    --primary: #6366f1;
                    --secondary: #a855f7;
                    --success: #10b981;
                    --background: #f8fafc;
                }

                * {
                    font-family: 'Inter', sans-serif;
                }

                .glass-card {
                    background: rgba(255, 255, 255, 0.9);
                    backdrop-filter: blur(12px);
                    border-radius: 20px;
                    border: 1px solid rgba(255,255,255,0.3);
                    box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.15);
                    padding: 1.5rem;
                    margin: 1rem 0;
                    transition: all 0.3s ease;
                }

                .glass-card:hover {
                    transform: translateY(-5px);
                    box-shadow: 0 12px 40px 0 rgba(31, 38, 135, 0.25);
                }

                .progress-bar {
                    height: 8px;
                    background: #e5e7eb;
                    border-radius: 4px;
                    overflow: hidden;
                }

                .progress-fill {
                    height: 100%;
                    background: linear-gradient(90deg, var(--primary) 0%, var(--secondary) 100%);
                    transition: width 0.5s ease;
                }

                .savings-tip {
                    position: relative;
                    background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
                    border-radius: 16px;
                    padding: 1.5rem;
                    margin: 1rem 0;
                    box-shadow: 0 4px 24px rgba(99,102,241,0.1);
                    border: 1px solid rgba(99,102,241,0.1);
                }

                .pulse-indicator {
                    width: 12px;
                    height: 12px;
                    background: var(--success);
                    border-radius: 50%;
                    position: absolute;
                    right: 1rem;
                    top: 1rem;
                    animation: pulse 1.5s infinite;
                }

                @keyframes pulse {
                    0% { box-shadow: 0 0 0 0 rgba(16,185,129,0.4); }
                    70% { box-shadow: 0 0 0 10px rgba(16,185,129,0); }
                    100% { box-shadow: 0 0 0 0 rgba(16,185,129,0); }
                }
            </style>
            """, unsafe_allow_html=True)

            # ------------------- Header Section -------------------
            header = grid([2, 5], vertical_align="center")
            with header.container():
                header.markdown("""
                <div style="display: flex; align-items: center; gap: 1.5rem; padding: 2rem 0;">
                    <div style="font-size: 3.5rem;">💸</div>
                    <div>
                        <h1 style="margin: 0; color: #1f2937; font-size: 2.5rem;">Smart Expense Tracker</h1>
                        <p style="margin: 0; color: #6b7280; font-size: 1.1rem;">AI-Powered Financial Insights & Optimization</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # ------------------- Initialize Session State -------------------
            if 'expenses' not in st.session_state:
                st.session_state.expenses = []
            if 'budgets' not in st.session_state:
                st.session_state.budgets = {
                    'Rent/Mortgage': 15000,
                    'Groceries': 8000,
                    'Dining Out': 5000,
                    'Transportation': 3000,
                    'Entertainment': 4000,
                    'Subscriptions': 2000,
                    'Shopping': 6000,
                    'Utilities': 4500,
                    'Healthcare': 3000,
                    'Other': 2500
                }

            # ------------------- Expense Input Form -------------------
            with st.expander("📥 Add New Expense", expanded=True):
                with st.form("expense_form", clear_on_submit=True):
                    cols = st.columns([1, 1, 2, 1])
                    with cols[0]:
                        amount = st.number_input("Amount (₹)", min_value=0, step=100)
                    with cols[1]:
                        date = st.date_input("Date", datetime.today())
                    with cols[2]:
                        category = st.selectbox("Category", options=[
                            ("🏠 Rent/Mortgage", "Rent/Mortgage"),
                            ("🛒 Groceries", "Groceries"),
                            ("🍽️ Dining Out", "Dining Out"),
                            ("🚗 Transportation", "Transportation"),
                            ("🎉 Entertainment", "Entertainment"),
                            ("📱 Subscriptions", "Subscriptions"),
                            ("🛍️ Shopping", "Shopping"),
                            ("💡 Utilities", "Utilities"),
                            ("🏥 Healthcare", "Healthcare"),
                            ("📦 Other", "Other")
                        ], format_func=lambda x: x[0])
                    with cols[3]:
                        description = st.text_input("Description")

                    if st.form_submit_button("✨ Add Expense", use_container_width=True):
                        st.session_state.expenses.append({
                            "amount": amount,
                            "date": date,
                            "category": category[1],
                            "description": description
                        })
                        st.success("✅ Expense added successfully!")

            # ------------------- Budget Configuration -------------------
            with st.expander("🎯 Set Monthly Budgets"):
                budget_grid = grid(2, 4, 2, 2, vertical_align="center")
                for idx, (cat, budget) in enumerate(st.session_state.budgets.items()):
                    with budget_grid.container():
                        st.session_state.budgets[cat] = st.slider(
                            f"**{cat}** Budget",
                            min_value=0,
                            max_value=50000,
                            value=budget,
                            step=500,
                            key=f"budget_{cat}"
                        )

            # ------------------- Data Analysis & Visualization -------------------
            if st.session_state.expenses:
                df = pd.DataFrame(st.session_state.expenses)
                df['date'] = pd.to_datetime(df['date'])
                current_month = datetime.now().strftime("%B")

                # ------------------- Key Metrics -------------------
                total_spent = df['amount'].sum()
                total_budget = sum(st.session_state.budgets.values())
                budget_utilization = (total_spent / total_budget) * 100 if total_budget else 0

                metric_grid = grid(3, 3, 3, 3, gap="medium")
                with metric_grid.container():
                    st.metric("Total Spent", f"₹{total_spent:,.0f}", f"{current_month}")
                with metric_grid.container():
                    st.metric("Monthly Budget", f"₹{total_budget:,.0f}",
                              "Remaining: ₹{total_budget - total_spent:,.0f}")
                with metric_grid.container():
                    st.metric("Budget Utilization", f"{budget_utilization:.1f}%")
                style_metric_cards(border_left_color="#6366f1", box_shadow=True)

                # ------------------- Main Visualizations -------------------
                col1, col2 = st.columns([2, 1])

                with col1:
                    # ------------------- Spending Timeline -------------------
                    with st.container():
                        st.markdown("### 📆 Spending Timeline")
                        timeline_df = df.groupby(df['date'].dt.date)['amount'].sum().reset_index()
                        fig = px.area(timeline_df, x='date', y='amount',
                                      labels={'amount': 'Daily Spending (₹)'},
                                      color_discrete_sequence=['#6366f1'])
                        fig.update_layout(
                            height=300,
                            margin=dict(t=30, b=20),
                            xaxis_title=None,
                            yaxis_title=None,
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)'
                        )
                        st.plotly_chart(fig, use_container_width=True)

                with col2:
                    # ------------------- Budget Progress -------------------
                    with st.container():
                        st.markdown("### 🎯 Budget Progress")
                        for category, budget in st.session_state.budgets.items():
                            spent = df[df['category'] == category]['amount'].sum()
                            utilization = (spent / budget) * 100 if budget else 0
                            color = "#ef4444" if utilization > 100 else "#10b981"

                            st.markdown(f"""
                            <div style="margin: 0.5rem 0;">
                                <div style="display: flex; justify-content: space-between; margin-bottom: 0.25rem;">
                                    <span>{category}</span>
                                    <span style="color: {color}; font-weight: 500;">{utilization:.1f}%</span>
                                </div>
                                <div class="progress-bar">
                                    <div class="progress-fill" style="width: {min(utilization, 100)}%; background: {color};"></div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)

                # ------------------- Advanced Analytics -------------------
                st.markdown("---")
                analytics_col1, analytics_col2 = st.columns([1, 2])

                with analytics_col1:
                    # ------------------- Category Breakdown -------------------
                    with st.container():
                        st.markdown("### 🎨 Spending Distribution")
                        category_df = df.groupby('category')['amount'].sum().reset_index()
                        fig = px.pie(category_df, values='amount', names='category',
                                     hole=0.6, color_discrete_sequence=px.colors.qualitative.Pastel)
                        fig.update_layout(showlegend=False, height=300, margin=dict(t=30, b=20))
                        st.plotly_chart(fig, use_container_width=True)

                with analytics_col2:
                    # ------------------- AI Recommendations -------------------
                    with st.container():
                        st.markdown("### 💡 Smart Savings Recommendations")

                        # Generate dynamic recommendations
                        category_spending = df.groupby('category')['amount'].sum().to_dict()
                        top_category = max(category_spending, key=category_spending.get)
                        top_spent = category_spending[top_category]
                        budget_diff = st.session_state.budgets[top_category] - top_spent

                        st.markdown(f"""
                        <div class="savings-tip">
                            <div class="pulse-indicator"></div>
                            <h4>🚨 Top Spending Category: {top_category}</h4>
                            <p>You've spent ₹{top_spent:,.0f} this month ({abs(budget_diff):,.0f} ₹{'over' if budget_diff < 0 else 'under'} budget).</p>
                            <ul>
                                {{
                                    'Rent/Mortgage': '<li>🔍 Compare rental prices in nearby areas</li><li>💡 Consider refinancing options</li>',
                                    'Groceries': '<li>📝 Implement meal planning strategy</li><li>🛒 Buy in bulk for staple items</li>',
                                    'Dining Out': '<li>🍳 Try meal prepping 2x/week</li><li>🎟️ Use discount coupons</li>',
                                    'Transportation': '<li>🚲 Carpool 3 days/week</li><li>⛽ Optimize fuel efficiency</li>',
                                    'Entertainment': '<li>🎥 Host movie nights at home</li><li>🎫 Explore free community events</li>',
                                    'Subscriptions': '<li>❌ Audit unused subscriptions</li><li>👥 Share family plans</li>',
                                    'Shopping': '<li>⏳ Implement 48-hour purchase rule</li><li>📉 Track price history</li>',
                                    'Utilities': '<li>💡 Switch to LED lighting</li><li>🌡️ Optimize thermostat settings</li>',
                                    'Healthcare': '<li>🏃 Invest in preventive care</li><li>💊 Compare pharmacy prices</li>',
                                    'Other': '<li>📊 Review weekly expenses</li><li>🎯 Set micro-budgets</li>'
                                }}[top_category]
                            </ul>
                            <div style="background: rgba(16,185,129,0.1); padding: 0.75rem; border-radius: 8px; margin-top: 1rem;">
                                💰 Potential Monthly Savings: <strong>₹{int(top_spent * 0.2):,.0f}+</strong>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                # ------------------- Comparative Analysis -------------------
                st.markdown("---")
                st.markdown("### 📈 Monthly Comparison")
                comparison_col1, comparison_col2, comparison_col3 = st.columns([1, 1, 2])

                with comparison_col1:
                    st.markdown("#### Current Month")
                    st.markdown(f"**Total Spent:** ₹{total_spent:,.0f}")
                    st.markdown(f"**Budget Utilization:** {budget_utilization:.1f}%")

                with comparison_col2:
                    st.markdown("#### Previous Month")
                    # Add your previous month's data logic here
                    st.markdown("**Total Spent:** ₹12,500")
                    st.markdown("**Savings Rate:** 18%")

                with comparison_col3:
                    # Sample comparison chart
                    fig = px.bar(x=['Current', 'Previous'], y=[total_spent, 12500],
                                 labels={'y': 'Amount (₹)'}, color=['#6366f1', '#a855f7'])
                    fig.update_layout(height=200, margin=dict(t=30, b=20), showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)

            else:
                # ------------------- Empty State -------------------
                st.markdown("""
                <div style="text-align: center; padding: 4rem; background: #f8fafc; border-radius: 20px; margin: 2rem 0;">
                    <div style="font-size: 4rem;">📭</div>
                    <h3 style="margin: 1rem 0; color: #1f2937;">No Expenses Recorded Yet</h3>
                    <p style="color: #6b7280;">Add your first expense to unlock financial insights</p>
                </div>
                """, unsafe_allow_html=True)


            # ------------------- Financial Health Score Dashboard -------------------
            st.markdown("### 🏆 Financial Health Score Dashboard")
            financial_health_score = (savings / income) * 40 + (1 - (debt / income)) * 30 + (
                    1 - (expenses / income)) * 30
            financial_health_score = min(max(financial_health_score, 0), 100)

            if financial_health_score >= 70:
                score_color = "#27ae60"
                score_status = "Good"
            elif financial_health_score >= 40:
                score_color = "#f39c12"
                score_status = "Needs Improvement"
            else:
                score_color = "#e74c3c"
                score_status = "High Risk"

            st.markdown(f"""
            <div class="fin-metric-box hover-card" style="border-color: {score_color};">
                <div class="metric-icon">📊</div>
                <h4>Financial Health Score</h4>
                <h2 style="color: {score_color};">{financial_health_score:.0f}/100 ({score_status})</h2>
            </div>
            """, unsafe_allow_html=True)

            # ------------------- Additional Features -------------------
            st.markdown("### ✨ Additional Features")

            # Feature 1: Emergency Fund Calculator
            st.markdown("#### 🚨 Emergency Fund Calculator")
            emergency_fund_months = st.slider("How many months of expenses do you want to cover?", 3, 12, 6)
            emergency_fund = expenses * emergency_fund_months
            st.markdown(f"""
            <div class="fin-metric-box hover-card" style="border-color: #27ae60;">
                <div class="metric-icon">🛡</div>
                <h4>Emergency Fund Required</h4>
                <h2 style="color: #27ae60;">₹{emergency_fund:,.0f}</h2>
            </div>
            """, unsafe_allow_html=True)

            # Display Advice with Enhanced Formatting
            st.markdown("### ✨ Personalized Recommendations")
            st.markdown(f"""
                       <div class="fin-advice-container hover-card" style="
                           background-color: #f8f9fa;
                           border-radius: 10px;
                           padding: 20px;
                           margin-top: 15px;
                           border-left: 5px solid #3498db;
                           box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                       ">
                           <div style="line-height: 1.6; color: #4a5568;">
                               {advice_text.replace('\n', '<br>')}
                           </div>
                       </div>
                       """, unsafe_allow_html=True)

            st.success("✅ Analysis complete! Explore your personalized recommendations above.")

            # ------------------- Add PDF Report Generation -------------------
            # In your Financial Advice tab where you generate the report:
            st.markdown("### 📄 Download Financial Report")
            if st.button("📥 Generate AI Finance Report"):
                pdf_file = generate_pdf_report(
                    income=st.session_state.user_profile['income'],
                    savings=st.session_state.user_profile['savings'],
                    debt=st.session_state.user_profile['debt'],
                    expenses=st.session_state.user_profile['expenses'],
                    advice=st.session_state.advice
                )
                st.download_button(
                    label="📥 Download Financial Report",
                    data=pdf_file,
                    file_name="AI_Finance_Report.pdf",
                    mime="application/pdf"
                )
                st.success("✅ Your financial report is ready! Download it above.")

    # ------------------- Tab 2: Stock Insights -------------------
    with tab2:
        st.markdown(
            """
            <style>
                .chatbot-icon {
                    position: fixed;
                    bottom: 20px;
                    right: 20px;
                    z-index: 1000;
                    cursor: pointer;
                    background-color: #2196F3;
                    color: white;
                    border-radius: 50%;
                    width: 70px;
                    height: 70px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                    transition: transform 0.2s, box-shadow 0.2s;
                    font-size: 32px;
                    animation: pulse 2s infinite;
                }
                .chatbot-icon:hover {
                    transform: scale(1.1);
                    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.2);
                    animation: none;
                }
                @keyframes pulse {
                    0% { transform: scale(1); }
                    50% { transform: scale(1.1); }
                    100% { transform: scale(1); }
                }
                .chatbot-icon::after {
                    content: "Chat with AI";
                    position: absolute;
                    top: -30px;
                    right: 0;
                    background-color: #2196F3;
                    color: white;
                    padding: 5px 10px;
                    border-radius: 5px;
                    font-size: 14px;
                    opacity: 0;
                    transition: opacity 0.3s;
                    pointer-events: none;
                }
                .chatbot-icon:hover::after {
                    opacity: 1;
                }
            </style>
            <div class="chatbot-icon" onclick="window.location.href='#tab3';">
                🤖
            </div>
            """,
            unsafe_allow_html=True
        )

        # Check if Tab 1 is completed
        if "user_profile" not in st.session_state or not st.session_state.user_profile['name']:
            st.warning("⚠ Please complete your financial profile in the Financial Advice tab first.")
            st.stop()

        st.subheader("📈 Real-Time Stock Insights & Analytics")
        selected_stock = st.selectbox("Select a Nifty 110 Stock:", get_nifty_110_stocks())

        if selected_stock:
            with st.spinner("🔍 Fetching stock data and analyzing market trends..."):
                time.sleep(2)
                stock_data = fetch_stock_data(selected_stock)

            if "error" in stock_data:
                st.error(f"Error fetching data: {stock_data['error']}")
            else:
                # Display stock info in columns with advanced styling
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"""
                    <div class="hover-card" style="background: linear-gradient(135deg, #f8f9fa, #e9ecef);
                                padding: 15px;
                                border-radius: 10px;
                                margin-bottom: 20px;
                                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                                transition: transform 0.2s;">
                        <h4 style="color: #2c3e50; margin:0 0 10px 0;">📌 Company Info</h4>
                        <p style="margin:5px 0;"><b>Name:</b> {stock_data['company']}</p>
                        <p style="margin:5px 0;"><b>Sector:</b> {stock_data['sector']}</p>
                    </div>
                    """, unsafe_allow_html=True)

                with col2:
                    st.markdown(f"""
                    <div class="hover-card" style="background: linear-gradient(135deg, #f8f9fa, #e9ecef);
                                padding: 15px;
                                border-radius: 10px;
                                margin-bottom: 20px;
                                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                                transition: transform 0.2s;">
                        <h4 style="color: #2c3e50; margin:0 0 10px 0;">💰 Price Metrics</h4>
                        <p style="margin:5px 0;"><b>Current Price:</b> ₹{stock_data['current_price']}</p>
                        <p style="margin:5px 0;"><b>Market Cap:</b> ₹{stock_data['market_cap']:,.2f}</p>
                    </div>
                    """, unsafe_allow_html=True)

                with col3:
                    profit_loss = round(stock_data['profit_loss'], 3)
                    profit_loss_percent = round(stock_data['profit_loss_percent'], 2)
                    pl_color = "green" if profit_loss >= 0 else "red"
                    arrow = "🔼" if profit_loss >= 0 else "🔽"
                    st.markdown(f"""
                    <div class="hover-card" style="background: linear-gradient(135deg, #f8f9fa, #e9ecef);
                                padding: 15px;
                                border-radius: 10px;
                                margin-bottom: 20px;
                                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                                transition: transform 0.2s;">
                        <h4 style="color: #2c3e50; margin:0 0 10px 0;">📊 Performance</h4>
                        <p style="margin:5px 0; color: {pl_color};">
                            <b>Profit/Loss:</b> {arrow} ₹{profit_loss} ({profit_loss_percent}%)
                        </p>
                    </div>
                    """, unsafe_allow_html=True)

                # Stock charts with advanced interactivity
                price_periods = {"1 Day": "1d", "1 Month": "1mo", "6 Month": "6mo", "1 Year": "1y", "5 Years": "5y",
                                 "ALL": "max"}
                sub_tabs = st.tabs(list(price_periods.keys()))
                ticker = yf.Ticker(selected_stock)

                for i, (label, period) in enumerate(price_periods.items()):
                    with sub_tabs[i]:
                        hist = ticker.history(period=period, interval="1m" if label == "1 Day" else "1d")
                        fig = px.line(hist, x=hist.index, y="Close", title=f"{stock_data['company']} - {label} Trend")
                        fig.update_layout(
                            plot_bgcolor="rgba(240, 242, 244, 1)",
                            paper_bgcolor="rgba(240, 242, 244, 1)",
                            hovermode="x unified",
                            xaxis_title="Date",
                            yaxis_title="Price (₹)",
                            font=dict(size=12, color="#2c3e50"),
                        )
                        st.plotly_chart(fig, use_container_width=True, config={"scrollZoom": True})

                # Stock Recommendation Section
                if st.button("📌 Get Stock Recommendation", key="recommendation_button"):
                    user_profile = st.session_state.user_profile
                    prompt = (
                        f"Provide a detailed stock analysis for {stock_data['company']} based on {user_profile['name']}'s investor profile: "
                        f"Age: {user_profile['age']}, Monthly Income: ₹{user_profile['income']}, "
                        f"Savings: ₹{user_profile['savings']}, Debt: ₹{user_profile['debt']}, "
                        f"Risk Preference: {user_profile['risk_pref']}, Debt-to-Income Ratio: {user_profile['debt_to_income']}%. "
                        f"Include potential profit/loss, risk analysis, and suitability for the investor. Address {user_profile['name']} directly in your response."
                    )
                    with st.spinner("🔮 Analyzing stock and generating recommendation..."):
                        time.sleep(2)
                        recommendation = model.generate_content(prompt)
                        st.session_state.stock_recommendation = recommendation.text.strip()

                    # Styled recommendation box with animations
                    st.markdown(f"""
                    <div class="hover-card" style="background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
                                border-radius: 15px;
                                padding: 25px;
                                margin: 20px 0;
                                border-left: 5px solid #2196F3;
                                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                                animation: fadeIn 1s ease-in-out;">
                        <h3 style="color: #1a237e; margin-top:0;">📈 Stock Recommendation</h3>
                        <div style="font-size: 16px; line-height: 1.6; color: #0d47a1;">
                            {st.session_state.stock_recommendation}
                        </div>
                    </div>
                    <style>
                        @keyframes fadeIn {{
                            0% {{ opacity: 0; transform: translateY(20px); }}
                            100% {{ opacity: 1; transform: translateY(0); }}
                        }}
                    </style>
                    """, unsafe_allow_html=True)

                # Future Stock Price Prediction Section
                if st.button("🔮 Predict Future Prices", key="predict_button"):
                    with st.spinner("🔮 Predicting future stock prices..."):
                        # Fetch historical data for the last 5 years
                        stock = yf.Ticker(selected_stock)
                        hist = stock.history(period="5y")
                        hist['Date'] = hist.index
                        hist['Days'] = (hist['Date'] - hist['Date'].min()).dt.days

                        # Prepare data for Linear Regression
                        X = hist[['Days']]
                        y = hist['Close']

                        # Split data into training and testing sets
                        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

                        # Train the Linear Regression model
                        model_lr = LinearRegression()
                        model_lr.fit(X_train, y_train)

                        # Predict future prices for the next 30 days
                        future_days = np.array([X['Days'].max() + i for i in range(1, 31)]).reshape(-1, 1)
                        future_prices = model_lr.predict(future_days)

                        # Calculate Mean Squared Error (MSE) for model validation
                        y_pred = model_lr.predict(X_test)
                        mse = mean_squared_error(y_test, y_pred)

                        # Display predicted prices in a styled container
                        st.markdown(f"""
                        <div class="hover-card" style="background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
                                    border-radius: 15px;
                                    padding: 25px;
                                    margin: 20px 0;
                                    border-left: 5px solid #2196F3;
                                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                                    animation: fadeIn 1s ease-in-out;">
                            <h3 style="color: #1a237e; margin-top:0;">📈 Predicted Future Prices</h3>
                            <div style="font-size: 16px; line-height: 1.6; color: #0d47a1;">
                                The predicted prices for the next 30 days are:
                                <ul>
                                    {"".join([f"<li>Day {i + 1}: ₹{price:.2f}</li>" for i, price in enumerate(future_prices)])}
                                </ul>
                                <p>Mean Squared Error: {mse:.2f}</p>
                            </div>
                        </div>
                        <style>
                            @keyframes fadeIn {{
                                0% {{ opacity: 0; transform: translateY(20px); }}
                                100% {{ opacity: 1; transform: translateY(0); }}
                            }}
                        </style>
                        """, unsafe_allow_html=True)

    # ------------------- Tab 3: AI Finance Chatbot -------------------
    with tab3:
        st.subheader("💬 AI Finance Chatbot")

        if "user_profile" not in st.session_state or not st.session_state.user_profile['name']:
            st.warning("⚠ Please complete your financial profile in the Financial Advice tab first.")
            st.stop()

        if "messages" not in st.session_state:
            st.session_state.messages = []
            st.session_state.messages.append({
                "role": "bot",
                "text": f"Hi {st.session_state.user_profile['name']}! I'm your AI Finance Assistant. How can I help you today? 😊",
                "time": datetime.now().strftime("%H:%M")
            })

        st.markdown(
            """
            <style>
                .message-container {
                    display: flex;
                    margin-bottom: 10px;
                }
                .bot-message {
                    background-color: #e3f2fd;
                    padding: 10px;
                    border-radius: 10px;
                    max-width: 70%;
                    align-self: flex-start;
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                }
                .user-message {
                    background-color: #bbdefb;
                    padding: 10px;
                    border-radius: 10px;
                    max-width: 70%;
                    align-self: flex-end;
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                }
                .timestamp {
                    font-size: 0.8em;
                    color: #666;
                    margin-top: 5px;
                }
            </style>
            """,
            unsafe_allow_html=True
        )

        for msg in st.session_state.messages:
            if msg["role"] == "bot":
                st.markdown(
                    f"""
                    <div class='message-container'>
                        <div class='bot-message'>
                            {msg['text']}
                            <div class='timestamp'>{msg['time']}</div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f"""
                    <div class='message-container' style='justify-content: flex-end;'>
                        <div class='user-message'>
                            {msg['text']}
                            <div class='timestamp'>{msg['time']}</div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        user_query = st.text_input("Type your message here...", key="user_input", placeholder="Type a message...", value="")
        if st.button("Send"):
            if user_query.strip():
                st.session_state.messages.append(
                    {"role": "user", "text": user_query, "time": datetime.now().strftime("%H:%M")})
                with st.spinner("Thinking..."):
                    user_profile = st.session_state.user_profile
                    prompt = (
                        f"User Profile for {user_profile['name']}: Age: {user_profile['age']}, Monthly Income: ₹{user_profile['income']}, "
                        f"Savings: ₹{user_profile['savings']}, Debt: ₹{user_profile['debt']}, "
                        f"Risk Preference: {user_profile['risk_pref']}, Debt-to-Income Ratio: {user_profile['debt_to_income']}%. "
                        f"User Query: {user_query}\n\n"
                        f"Respond directly to {user_profile['name']} in a friendly, professional manner."
                    )
                    response = model.generate_content(prompt)
                    bot_reply = response.text.strip()
                    st.session_state.messages.append(
                        {"role": "bot", "text": bot_reply, "time": datetime.now().strftime("%H:%M")})

                st.rerun()

    # ------------------- Tab 4: Portfolio Management -------------------
    with tab4:
        st.subheader("📊 Portfolio Management")

        if "user_profile" not in st.session_state or not st.session_state.user_profile['name']:
            st.warning("⚠ Please complete your financial profile in the Financial Advice tab first.")
            st.stop()

        if "portfolio" not in st.session_state:
            st.session_state.portfolio = []

        col1, col2 = st.columns(2)
        with col1:
            stock_symbol = st.text_input("Enter Stock Symbol (e.g., RELIANCE.NS):")
            quantity = st.number_input("Quantity:", min_value=1, step=1, value=1)
            purchase_price = st.number_input("Purchase Price (₹):", min_value=0.0, step=0.01, value=0.0)
        with col2:
            purchase_date = st.date_input("Purchase Date:")
            if st.button("Add to Portfolio"):
                if stock_symbol:
                    stock_data = fetch_stock_data(stock_symbol)
                    if "error" not in stock_data:
                        st.session_state.portfolio.append({
                            "symbol": stock_symbol,
                            "quantity": quantity,
                            "purchase_price": purchase_price,
                            "purchase_date": purchase_date,
                            "current_price": stock_data['current_price'],
                            "profit_loss": stock_data['profit_loss'],
                            "profit_loss_percent": stock_data['profit_loss_percent']
                        })
                        st.success("Stock added to portfolio!")
                    else:
                        st.error(f"Error fetching stock data: {stock_data['error']}")
                else:
                    st.error("Please enter a valid stock symbol.")

        if st.session_state.portfolio:
            st.markdown(f"### 📊 {st.session_state.user_profile['name']}'s Portfolio")
            portfolio_df = pd.DataFrame(st.session_state.portfolio)

            # Calculate portfolio metrics
            portfolio_df['Current Value'] = portfolio_df['quantity'] * portfolio_df['current_price']
            portfolio_df['Investment'] = portfolio_df['quantity'] * portfolio_df['purchase_price']
            portfolio_df['Profit/Loss'] = portfolio_df['quantity'] * portfolio_df['profit_loss']
            portfolio_df['Profit/Loss %'] = portfolio_df['profit_loss_percent']

            # Display the portfolio table
            st.dataframe(portfolio_df)

            # Calculate total portfolio metrics
            total_investment = portfolio_df['Investment'].sum()
            total_current_value = portfolio_df['Current Value'].sum()
            total_profit_loss = portfolio_df['Profit/Loss'].sum()
            total_profit_loss_percent = (total_profit_loss / total_investment) * 100 if total_investment != 0 else 0

            # Display portfolio summary with styled container
            st.markdown(f"""
            <div class="hover-card" style="background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
                        border-radius: 15px;
                        padding: 25px;
                        margin: 20px 0;
                        border-left: 5px solid #2196F3;
                        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                        animation: fadeIn 1s ease-in-out;">
                <h3 style="color: #1a237e; margin-top:0;">📊 Portfolio Summary</h3>
                <div style="font-size: 16px; line-height: 1.6; color: #0d47a1;">
                    <p><b>Total Investment:</b> ₹{total_investment:,.2f}</p>
                    <p><b>Total Current Value:</b> ₹{total_current_value:,.2f}</p>
                    <p><b>Total Profit/Loss:</b> ₹{total_profit_loss:,.2f} ({total_profit_loss_percent:.2f}%)</p>
                </div>
            </div>
            <style>
                @keyframes fadeIn {{
                    0% {{ opacity: 0; transform: translateY(20px); }}
                    100% {{ opacity: 1; transform: translateY(0); }}
                }}
            </style>
            """, unsafe_allow_html=True)

# ==================== APP FLOW CONTROL ====================
def main():
    # Initialize session state
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "landing_viewed" not in st.session_state:
        st.session_state.landing_viewed = False
    if "username" not in st.session_state:
        st.session_state.username = ""

    # Show landing page if not viewed yet
    if not st.session_state.landing_viewed:
        landing_page()
    # Show auth page if not authenticated
    elif not st.session_state.authenticated:
        auth_page()
    # Otherwise show main app
    else:
        main_app()

if __name__ == "__main__":
    main()

