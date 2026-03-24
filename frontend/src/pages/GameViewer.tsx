import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import styled from 'styled-components'
import { Loader2 } from 'lucide-react'
import api from '../api/client'
import ChessBoard from '../components/ChessBoard'
import MoveList from '../components/MoveList'
import EvaluationGraph from '../components/EvaluationGraph'
import InsightsPanel from '../components/InsightsPanel'

const ViewerContainer = styled.div`
  display: grid;
  grid-template-columns: 1fr 320px 320px;
  gap: 2rem;
  
  @media (max-width: 1200px) {
    grid-template-columns: 1fr 320px;
  }
  
  @media (max-width: 900px) {
    grid-template-columns: 1fr;
  }
`

const MainColumn = styled.div`
  display: flex;
  flex-direction: column;
  gap: 2rem;
`

const BoardSection = styled.div`
  display: flex;
  justify-content: center;
`

const SidePanel = styled.div`
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
`

const LoadingContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
  color: rgba(255, 255, 255, 0.7);
`

interface Move {
  move_number: number
  san: string
  uci: string
  fen: string
  evaluation?: number
  is_blunder?: boolean
  is_mistake?: boolean
  time_in_video?: number
}

interface GameData {
  id: string
  pgn: string
  moves: Move[]
  final_fen: string
  result: string
  white_player?: string
  black_player?: string
  total_moves: number
  analysis_complete: boolean
}

interface Insight {
  move_number: number
  type: string
  description: string
}

interface AnalysisData {
  insights: Insight[]
  accuracy_white: number
  accuracy_black: number
}

export default function GameViewer() {
  const { gameId } = useParams<{ gameId: string }>()
  const [game, setGame] = useState<GameData | null>(null)
  const [analysis, setAnalysis] = useState<AnalysisData | null>(null)
  const [currentMove, setCurrentMove] = useState(0)
  const [loading, setLoading] = useState(true)
  
  useEffect(() => {
    fetchGame()
  }, [gameId])
  
  const fetchGame = async () => {
    try {
      const [gameRes, analysisRes] = await Promise.all([
        api.get(`/games/${gameId}`),
        api.get(`/analysis/game/${gameId}`)
      ])
      
      setGame(gameRes.data)
      setAnalysis(analysisRes.data)
    } catch (error) {
      console.error('Failed to fetch game:', error)
    } finally {
      setLoading(false)
    }
  }
  
  const handleMoveClick = (moveIndex: number) => {
    setCurrentMove(moveIndex)
  }
  
  const getCurrentFen = () => {
    if (!game) return undefined
    if (currentMove === 0) return undefined // Starting position
    return game.moves[currentMove - 1]?.fen
  }
  
  if (loading) {
    return (
      <LoadingContainer>
        <Loader2 className="animate-spin" size={48} color="#7ee8fa" />
        <p style={{ marginTop: '1rem' }}>Loading game...</p>
      </LoadingContainer>
    )
  }
  
  if (!game) {
    return (
      <LoadingContainer>
        <p>Game not found</p>
      </LoadingContainer>
    )
  }
  
  return (
    <ViewerContainer>
      <MainColumn>
        <BoardSection>
          <ChessBoard 
            fen={getCurrentFen()} 
            readOnly={true}
          />
        </BoardSection>
        
        {game.moves.some(m => m.evaluation !== undefined) && (
          <EvaluationGraph 
            moves={game.moves} 
            onMoveClick={handleMoveClick}
          />
        )}
      </MainColumn>
      
      <SidePanel>
        <MoveList 
          moves={game.moves}
          currentMove={currentMove}
          onMoveClick={handleMoveClick}
        />
      </SidePanel>
      
      <SidePanel>
        {analysis && (
          <InsightsPanel 
            insights={analysis.insights}
            accuracyWhite={analysis.accuracy_white}
            accuracyBlack={analysis.accuracy_black}
          />
        )}
      </SidePanel>
    </ViewerContainer>
  )
}