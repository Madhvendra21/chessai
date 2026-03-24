import styled from 'styled-components'

const MoveListContainer = styled.div`
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 1rem;
  max-height: 500px;
  overflow-y: auto;
`

const Title = styled.h3`
  margin: 0 0 1rem 0;
  color: #fff;
  font-size: 1.1rem;
`

const MoveRow = styled.div<{ isCurrent: boolean }>`
  display: flex;
  gap: 0.5rem;
  padding: 0.5rem;
  background: ${props => props.isCurrent ? 'rgba(126, 232, 250, 0.2)' : 'transparent'};
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.2s;
  
  &:hover {
    background: rgba(255, 255, 255, 0.1);
  }
`

const MoveNumber = styled.span`
  color: rgba(255, 255, 255, 0.5);
  min-width: 30px;
`

const MoveText = styled.span<{ isBlunder?: boolean; isMistake?: boolean }>`
  color: ${props => {
    if (props.isBlunder) return '#ff6b6b'
    if (props.isMistake) return '#ffd93d'
    return '#fff'
  }};
  font-weight: ${props => (props.isBlunder || props.isMistake) ? 'bold' : 'normal'};
  flex: 1;
  
  &:hover {
    text-decoration: underline;
  }
`

interface MoveData {
  move_number: number
  san: string
  uci: string
  fen: string
  evaluation?: number
  is_blunder?: boolean
  is_mistake?: boolean
}

interface MoveListProps {
  moves: MoveData[]
  currentMove: number
  onMoveClick: (moveIndex: number) => void
}

export default function MoveList({ moves, currentMove, onMoveClick }: MoveListProps) {
  // Group moves into pairs (white and black)
  const movePairs: { white?: MoveData; black?: MoveData; number: number }[] = []
  
  for (let i = 0; i < moves.length; i += 2) {
    movePairs.push({
      number: Math.floor(i / 2) + 1,
      white: moves[i],
      black: moves[i + 1]
    })
  }
  
  return (
    <MoveListContainer>
      <Title>Moves</Title>
      {movePairs.map((pair, idx) => (
        <MoveRow key={idx} isCurrent={currentMove === idx * 2 || currentMove === idx * 2 + 1}>
          <MoveNumber>{pair.number}.</MoveNumber>
          {pair.white && (
            <MoveText
              isBlunder={pair.white.is_blunder}
              isMistake={pair.white.is_mistake}
              onClick={() => onMoveClick(idx * 2)}
            >
              {pair.white.san}
            </MoveText>
          )}
          {pair.black && (
            <MoveText
              isBlunder={pair.black.is_blunder}
              isMistake={pair.black.is_mistake}
              onClick={() => onMoveClick(idx * 2 + 1)}
            >
              {pair.black.san}
            </MoveText>
          )}
        </MoveRow>
      ))}
    </MoveListContainer>
  )
}