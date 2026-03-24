import { Routes, Route } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import styled from 'styled-components'
import Navbar from './components/Navbar'
import Home from './pages/Home'
import Upload from './pages/Upload'
import GameViewer from './pages/GameViewer'
import Jobs from './pages/Jobs'

const AppContainer = styled.div`
  min-height: 100vh;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
`

const MainContent = styled.main`
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
`

function App() {
  return (
    <AppContainer>
      <Navbar />
      <MainContent>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/upload" element={<Upload />} />
          <Route path="/game/:gameId" element={<GameViewer />} />
          <Route path="/jobs" element={<Jobs />} />
        </Routes>
      </MainContent>
      <Toaster position="top-right" />
    </AppContainer>
  )
}

export default App