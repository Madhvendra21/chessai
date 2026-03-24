import { Link } from 'react-router-dom'
import styled from 'styled-components'
import { Upload, PlayCircle, BarChart3, Zap } from 'lucide-react'

const Hero = styled.div`
  text-align: center;
  padding: 4rem 2rem;
`

const Title = styled.h1`
  font-size: 3rem;
  font-weight: bold;
  background: linear-gradient(135deg, #7ee8fa 0%, #7ee8fa 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 1rem;
`

const Subtitle = styled.p`
  font-size: 1.25rem;
  color: rgba(255, 255, 255, 0.7);
  max-width: 600px;
  margin: 0 auto 2rem;
  line-height: 1.6;
`

const CTAButton = styled(Link)`
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: linear-gradient(135deg, #7ee8fa 0%, #4d96ff 100%);
  color: #1a1a2e;
  padding: 1rem 2rem;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 600;
  font-size: 1.1rem;
  transition: transform 0.2s, box-shadow 0.2s;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(126, 232, 250, 0.4);
  }
`

const Features = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
  margin-top: 4rem;
`

const FeatureCard = styled.div`
  background: rgba(255, 255, 255, 0.05);
  padding: 2rem;
  border-radius: 12px;
  text-align: center;
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: transform 0.2s;
  
  &:hover {
    transform: translateY(-4px);
    background: rgba(255, 255, 255, 0.08);
  }
`

const FeatureIcon = styled.div`
  width: 60px;
  height: 60px;
  background: rgba(126, 232, 250, 0.1);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1rem;
`

const FeatureTitle = styled.h3`
  color: #fff;
  margin-bottom: 0.5rem;
`

const FeatureDesc = styled.p`
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.9rem;
  line-height: 1.5;
`

export default function Home() {
  return (
    <>
      <Hero>
        <Title>ChessVision AI</Title>
        <Subtitle>
          Transform chess videos into interactive analysis. Upload any chess video, 
          and our AI will extract the moves, analyze the game with Stockfish, 
          and provide insights.
        </Subtitle>
        <CTAButton to="/upload">
          <Upload size={20} />
          Upload Video
        </CTAButton>
      </Hero>
      
      <Features>
        <FeatureCard>
          <FeatureIcon>
            <PlayCircle size={28} color="#7ee8fa" />
          </FeatureIcon>
          <FeatureTitle>Video Processing</FeatureTitle>
          <FeatureDesc>
            Supports YouTube URLs and direct video uploads. Automatically 
            extracts frames and detects board positions.
          </FeatureDesc>
        </FeatureCard>
        
        <FeatureCard>
          <FeatureIcon>
            <BarChart3 size={28} color="#7ee8fa" />
          </FeatureIcon>
          <FeatureTitle>Deep Analysis</FeatureTitle>
          <FeatureDesc>
            Powered by Stockfish engine. Get move-by-move evaluations, 
            identify blunders, and see the best lines.
          </FeatureDesc>
        </FeatureCard>
        
        <FeatureCard>
          <FeatureIcon>
            <Zap size={28} color="#7ee8fa" />
          </FeatureIcon>
          <FeatureTitle>Interactive Viewer</FeatureTitle>
          <FeatureDesc>
            Browse through moves with synchronized board state. 
            Evaluation graphs and insights panel included.
          </FeatureDesc>
        </FeatureCard>
      </Features>
    </>
  )
}