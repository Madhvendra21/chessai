import { Link } from 'react-router-dom'
import styled from 'styled-components'
import { Upload, Home, List, PlayCircle } from 'lucide-react'

const Nav = styled.nav`
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding: 1rem 2rem;
`

const NavContent = styled.div`
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
`

const Logo = styled(Link)`
  font-size: 1.5rem;
  font-weight: bold;
  color: #fff;
  text-decoration: none;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  
  &:hover {
    color: #7ee8fa;
  }
`

const NavLinks = styled.div`
  display: flex;
  gap: 2rem;
`

const NavLink = styled(Link)`
  color: rgba(255, 255, 255, 0.7);
  text-decoration: none;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: color 0.2s;
  
  &:hover {
    color: #fff;
  }
`

export default function Navbar() {
  return (
    <Nav>
      <NavContent>
        <Logo to="/">
          <PlayCircle size={24} />
          ChessVision AI
        </Logo>
        <NavLinks>
          <NavLink to="/">
            <Home size={18} />
            Home
          </NavLink>
          <NavLink to="/upload">
            <Upload size={18} />
            Upload
          </NavLink>
          <NavLink to="/jobs">
            <List size={18} />
            Jobs
          </NavLink>
        </NavLinks>
      </NavContent>
    </Nav>
  )
}