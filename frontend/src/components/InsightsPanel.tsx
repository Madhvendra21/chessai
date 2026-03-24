import styled from 'styled-components'
import { AlertCircle, Lightbulb, Target } from 'lucide-react'

const Panel = styled.div`
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 1rem;
  max-height: 400px;
  overflow-y: auto;
`

const Title = styled.h3`
  margin: 0 0 1rem 0;
  color: #fff;
  font-size: 1.1rem;
`

const InsightItem = styled.div<{ type: string }>`
  display: flex;
  gap: 0.75rem;
  padding: 0.75rem;
  margin-bottom: 0.5rem;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 8px;
  border-left: 3px solid ${props => {
    switch (props.type) {
      case 'blunder': return '#ff6b6b'
      case 'mistake': return '#ffd93d'
      case 'opening': return '#6bcf7f'
      case 'endgame': return '#4d96ff'
      default: return '#7ee8fa'
    }
  }};
`

const IconWrapper = styled.div`
  flex-shrink: 0;
  margin-top: 2px;
`

const Content = styled.div`
  flex: 1;
`

const MoveNumber = styled.div`
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.5);
  margin-bottom: 0.25rem;
`

const Description = styled.div`
  color: rgba(255, 255, 255, 0.9);
  font-size: 0.9rem;
  line-height: 1.4;
`

const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
  margin-bottom: 1rem;
`

const StatBox = styled.div`
  background: rgba(255, 255, 255, 0.05);
  padding: 0.75rem;
  border-radius: 8px;
  text-align: center;
`

const StatValue = styled.div`
  font-size: 1.5rem;
  font-weight: bold;
  color: #7ee8fa;
`

const StatLabel = styled.div`
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.6);
  margin-top: 0.25rem;
`

interface Insight {
  move_number: number
  type: string
  description: string
}

interface InsightsPanelProps {
  insights: Insight[]
  accuracyWhite?: number
  accuracyBlack?: number
}

export default function InsightsPanel({ 
  insights, 
  accuracyWhite = 0, 
  accuracyBlack = 0 
}: InsightsPanelProps) {
  const getIcon = (type: string) => {
    switch (type) {
      case 'blunder':
        return <AlertCircle size={18} color="#ff6b6b" />
      case 'mistake':
        return <AlertCircle size={18} color="#ffd93d" />
      case 'opening':
      case 'endgame':
        return <Lightbulb size={18} color="#6bcf7f" />
      default:
        return <Target size={18} color="#7ee8fa" />
    }
  }
  
  return (
    <Panel>
      <Title>Analysis</Title>
      
      <StatsGrid>
        <StatBox>
          <StatValue>{accuracyWhite}%</StatValue>
          <StatLabel>White Accuracy</StatLabel>
        </StatBox>
        <StatBox>
          <StatValue>{accuracyBlack}%</StatValue>
          <StatLabel>Black Accuracy</StatLabel>
        </StatBox>
      </StatsGrid>
      
      {insights.map((insight, idx) => (
        <InsightItem key={idx} type={insight.type}>
          <IconWrapper>
            {getIcon(insight.type)}
          </IconWrapper>
          <Content>
            <MoveNumber>Move {insight.move_number}</MoveNumber>
            <Description>{insight.description}</Description>
          </Content>
        </InsightItem>
      ))}
    </Panel>
  )
}