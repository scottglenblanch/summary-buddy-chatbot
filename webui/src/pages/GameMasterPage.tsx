import React from 'react'
import GameMasterChat from '@/components/Chat'
import { Link } from 'react-router-dom'
import '../styles/GameMasterPage.css'

export default function GameMasterPage() {
  return (
    <div className="page-container">
      <header className="page-header">
        <div className="header-content">
          <h1>🌍 Summary Buddy - Game Master Chat</h1>
          <nav className="nav-links">
            <Link to="/game-master-chatbot" className="nav-link active">
              Chat
            </Link>
            <Link to="/admin" className="nav-link">
              Admin
            </Link>
          </nav>
        </div>
      </header>

      <main className="page-content">
        <GameMasterChat />
      </main>

      <footer className="page-footer">
        <p>&copy; 2025 Summary Buddy Chatbot. All rights reserved.</p>
      </footer>
    </div>
  )
}
