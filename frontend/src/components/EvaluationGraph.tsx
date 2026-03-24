import { useMemo } from 'react'
import { LineChart, Line, XAxis, YAxis, ResponsiveContainer, Tooltip } from 'recharts'
import styled from 'styled-components'

const GraphContainer = styled.div`
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 1rem;
  height: 200px;
`

const Title = styled.h3`
  margin: 0 0 1rem 0;
  color: #fff;
  font-size: 1.1rem;
`

interface EvaluationData {
  move_number: number
  evaluation?: number
}

interface EvaluationGraphProps {
  moves: EvaluationData[]
  onMoveClick: (moveIndex: number) => void
}

export default function EvaluationGraph({ moves, onMoveClick }: EvaluationGraphProps) {
  const data = useMemo(() => {
    return moves.map((move, idx) => ({
      move: move.move_number,
      eval: move.evaluation !== undefined ? move.evaluation : 0,
      index: idx
    }))
  }, [moves])
  
  return (
    <GraphContainer>
      <Title>Evaluation</Title>
      <ResponsiveContainer width="100%" height={150}>
        <LineChart data={data} onClick={(e) => {
          if (e && e.activeTooltipIndex !== undefined) {
            onMoveClick(e.activeTooltipIndex)
          }
        }}>
          <XAxis 
            dataKey="move" 
            stroke="rgba(255, 255, 255, 0.3)"
            tick={{ fill: 'rgba(255, 255, 255, 0.5)', fontSize: 12 }}
          />
          <YAxis 
            stroke="rgba(255, 255, 255, 0.3)"
            tick={{ fill: 'rgba(255, 255, 255, 0.5)', fontSize: 12 }}
            domain={[-5, 5]}
            tickFormatter={(value) => `${value > 0 ? '+' : ''}${value}`}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: 'rgba(0, 0, 0, 0.8)',
              border: '1px solid rgba(255, 255, 255, 0.2)',
              borderRadius: '4px'
            }}
            labelStyle={{ color: '#fff' }}
            itemStyle={{ color: '#7ee8fa' }}
            formatter={(value: number) => [`${value > 0 ? '+' : ''}${value.toFixed(2)}`, 'Evaluation']}
          />
          <Line
            type="monotone"
            dataKey="eval"
            stroke="#7ee8fa"
            strokeWidth={2}
            dot={{ fill: '#7ee8fa', strokeWidth: 0, r: 3 }}
            activeDot={{ r: 5, fill: '#fff' }}
          />
        </LineChart>
      </ResponsiveContainer>
    </GraphContainer>
  )
}