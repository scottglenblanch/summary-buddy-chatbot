import React, { useState, useRef, useEffect } from 'react'
import { askGameMaster, ChatResponse } from '@services/api'
import '../styles/GameMasterChat.css'

interface ConversationMessage {
  id: string
  question: string
  answer: string
  sources: string[]
  timestamp: Date
}

export default function GameMasterChat() {
  const [question, setQuestion] = useState('')
  const [answer, setAnswer] = useState('')
  const [sources, setSources] = useState<string[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [conversationId, setConversationId] = useState<string | null>(null)
  const [conversations, setConversations] = useState<ConversationMessage[]>([])
  const [showHistory, setShowHistory] = useState(false)
  const answersEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    answersEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [answer])

  const handleAsk = async () => {
    if (!question.trim()) {
      setError('Please enter a question')
      return
    }

    setLoading(true)
    setError('')
    setAnswer('')
    setSources([])

    try {
      const response: ChatResponse = await askGameMaster(question)
      
      if (response.answer) {
        setAnswer(response.answer)
        setSources(response.sources || [])
        setConversationId(response.conversation_id || null)

        // Add to conversation history
        setConversations([
          ...conversations,
          {
            id: response.conversation_id || `local-${Date.now()}`,
            question: question,
            answer: response.answer,
            sources: response.sources || [],
            timestamp: new Date(),
          },
        ])

        // Clear question after successful response
        setQuestion('')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to get response')
      setAnswer('')
      setSources([])
    } finally {
      setLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && e.ctrlKey) {
      handleAsk()
    }
  }

  const clearConversation = () => {
    setQuestion('')
    setAnswer('')
    setSources([])
    setError('')
    setConversationId(null)
  }

  const clearHistory = () => {
    setConversations([])
  }

  const loadConversation = (conv: ConversationMessage) => {
    setQuestion(conv.question)
    setAnswer(conv.answer)
    setSources(conv.sources)
    setConversationId(conv.id)
    setShowHistory(false)
  }

  const formatTime = (date: Date) => {
    return new Intl.DateTimeFormat('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    }).format(date)
  }

  return (
    <div className="game-master-chat">
      <div className="chat-header">
        <h1>Summary Buddy</h1>
        <p className="subtitle">Ask questions about your uploaded documents</p>
        {conversations.length > 0 && (
          <div className="history-controls">
            <button
              className="history-button"
              onClick={() => setShowHistory(!showHistory)}
            >
              📜 History ({conversations.length})
            </button>
          </div>
        )}
      </div>

      {showHistory && conversations.length > 0 && (
        <div className="conversation-history">
          <div className="history-header">
            <h3>Conversation History</h3>
            <button className="clear-history" onClick={clearHistory}>
              Clear
            </button>
          </div>
          <div className="history-list">
            {conversations.map((conv, idx) => (
              <div key={conv.id} className="history-item">
                <div className="history-item-content">
                  <p className="history-question">{idx + 1}. {conv.question}</p>
                  <p className="history-time">{formatTime(conv.timestamp)}</p>
                </div>
                <button
                  className="load-button"
                  onClick={() => loadConversation(conv)}
                >
                  Load
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="chat-container">
        <div className="question-section">
          <label htmlFor="question-input">Your Question:</label>
          <textarea
            id="question-input"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask the Game Master anything about your documents... (Ctrl+Enter to send)"
            disabled={loading}
            rows={4}
          />
        </div>

        <div className="button-group">
          <button
            onClick={handleAsk}
            disabled={loading}
            className="ask-button"
          >
            {loading ? '⏳ Consulting the Summary Buddy AI...' : '✨ Ask Summary Buddy AI'}
          </button>
          {(question || answer || error) && (
            <button
              onClick={clearConversation}
              disabled={loading}
              className="clear-button"
            >
              Clear
            </button>
          )}
        </div>

        {error && (
          <div className="error-message">
            <span className="error-icon">❌</span>
            <div>
              <strong>Error:</strong> {error}
            </div>
          </div>
        )}

        {loading && !answer && (
          <div className="loading-skeleton">
            <div className="skeleton-line"></div>
            <div className="skeleton-line"></div>
            <div className="skeleton-line short"></div>
          </div>
        )}

        {answer && (
          <div className="answer-section">
            <label>Game Master's Response:</label>
            <div className="answer-box">
              {answer}
            </div>

            {sources && sources.length > 0 && (
              <div className="sources-section">
                <label>📚 Sources:</label>
                <div className="sources-list">
                  {sources.map((source, idx) => (
                    <div key={idx} className="source-item">
                      <span className="source-number">{idx + 1}</span>
                      <span className="source-text">{source}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {conversationId && (
              <p className="conversation-id">
                Conversation ID: <code>{conversationId}</code>
              </p>
            )}
          </div>
        )}

        <div ref={answersEndRef} />
      </div>
    </div>
  )
}
