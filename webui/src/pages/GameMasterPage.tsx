import React from 'react'
import GameMasterChat from '@/components/Chat'
import AdminPanel from '@components/AdminPanel'
import '../styles/GameMasterPage.css'

export default function GameMasterPage() {
  return (
    <div className="page-container">
      <header className="page-header">
        <div className="header-content">
          <h1>🌍 Summary Buddy</h1>
        </div>
      </header>

      <main className="page-content">
        <div className="page-split">
          <section className="page-split-pane chat-pane">
            <GameMasterChat />
          </section>
          <section className="page-split-pane admin-pane">
            <AdminPanel />
          </section>
        </div>
      </main>

      <footer className="page-footer">
        <p>&copy; 2025 Summary Buddy Chatbot. All rights reserved.</p>
      </footer>
    </div>
  )
}
