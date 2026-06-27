import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import GameMasterPage from '@pages/GameMasterPage'
import '@styles/App.css'

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/game-master-chatbot" element={<GameMasterPage />} />
        <Route path="/" element={<GameMasterPage />} />
        <Route path="*" element={<Navigate to="/game-master-chatbot" replace />} />
      </Routes>
    </Router>
  )
}

export default App
