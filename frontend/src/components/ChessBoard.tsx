import { useState, useEffect } from 'react'
   import { Chessboard } from 'react-chessboard'
   import { Chess } from 'chess.js'
   import styled from 'styled-components'
   
   const BoardContainer = styled.div`
     background: rgba(255, 255, 255, 0.05);
     border-radius: 12px;
     padding: 1rem;
     box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
   `
   
   interface ChessBoardProps {
     fen?: string
     onMove?: (move: string) => void
     readOnly?: boolean
   }
   
   export default function ChessBoard({ fen, onMove, readOnly = false }: ChessBoardProps) {
     const [game, setGame] = useState(new Chess())
     
     useEffect(() => {
       if (fen) {
         try {
           const newGame = new Chess()
           newGame.load(fen)
           setGame(newGame)
         } catch (e) {
           console.error('Invalid FEN:', fen)
         }
       }
     }, [fen])
     
     function onDrop(sourceSquare: string, targetSquare: string) {
       if (readOnly) return false
       
       try {
         const move = game.move({
           from: sourceSquare,
           to: targetSquare,
           promotion: 'q'
         })
         
         if (move === null) return false
         
         setGame(new Chess(game.fen()))
         if (onMove) {
           onMove(move.san)
         }
         return true
       } catch (e) {
         return false
       }
     }
     
     return (
       <BoardContainer>
         <Chessboard
           position={game.fen()}
           onPieceDrop={onDrop}
           boardWidth={480}
           customBoardStyle={{
             borderRadius: '8px',
             boxShadow: '0 4px 12px rgba(0,0,0,0.3)'
           }}
           customDarkSquareStyle={{ backgroundColor: '#779952' }}
           customLightSquareStyle={{ backgroundColor: '#edeed1' }}
           isDraggablePiece={() => !readOnly}
         />
       </BoardContainer>
     )
   }