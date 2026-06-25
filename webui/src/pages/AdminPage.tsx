import React from 'react'
import AdminPanel from '@components/AdminPanel'
import { Link } from 'react-router-dom'
import '../styles/AdminPage.css'

export default function AdminPage() {
  return (
    <div className="page-container">
      <header className="page-header">
        <div className="header-content">
          <h1>🌍 Summary Buddy - Admin Panel</h1>
          <nav className="nav-links">
            <Link to="/game-master-chatbot" className="nav-link">
              Chat
            </Link>
            <Link to="/admin" className="nav-link active">
              Admin
            </Link>
          </nav>
        </div>
      </header>

      <main className="page-content">
        <AdminPanel />
      </main>

      <footer className="page-footer">
        <p>&copy; 2025 Summary Buddy Chatbot. All rights reserved.</p>
      </footer>
    </div>
  )
}
