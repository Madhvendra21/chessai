import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import styled from 'styled-components'
import { formatDistanceToNow } from 'date-fns'
import { Loader2, CheckCircle, XCircle, Clock, Trash2 } from 'lucide-react'
import api from '../api/client'

const JobsContainer = styled.div`
  max-width: 1000px;
  margin: 0 auto;
`

const Title = styled.h1`
  color: #fff;
  margin-bottom: 2rem;
`

const JobList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 1rem;
`

const JobCard = styled.div`
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.2s;
  
  &:hover {
    background: rgba(255, 255, 255, 0.08);
    border-color: rgba(126, 232, 250, 0.3);
  }
`

const JobInfo = styled.div`
  flex: 1;
`

const JobTitle = styled.h3`
  color: #fff;
  margin: 0 0 0.5rem 0;
  font-size: 1.1rem;
`

const JobMeta = styled.div`
  display: flex;
  gap: 1rem;
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.85rem;
`

const StatusBadge = styled.span<{ status: string }>`
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.25rem 0.75rem;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
  background: ${props => {
    switch (props.status) {
      case 'completed': return 'rgba(107, 207, 127, 0.2)'
      case 'failed': return 'rgba(255, 107, 107, 0.2)'
      case 'processing': return 'rgba(126, 232, 250, 0.2)'
      default: return 'rgba(255, 255, 255, 0.1)'
    }
  }};
  color: ${props => {
    switch (props.status) {
      case 'completed': return '#6bcf7f'
      case 'failed': return '#ff6b6b'
      case 'processing': return '#7ee8fa'
      default: return 'rgba(255, 255, 255, 0.7)'
    }
  }};
`

const ProgressBar = styled.div`
  width: 100px;
  height: 6px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
  overflow: hidden;
  margin-top: 0.5rem;
`

const ProgressFill = styled.div<{ progress: number }>`
  width: ${props => props.progress}%;
  height: 100%;
  background: #7ee8fa;
  transition: width 0.3s;
`

const ActionButtons = styled.div`
  display: flex;
  gap: 0.75rem;
`

const IconButton = styled.button`
  background: rgba(255, 255, 255, 0.1);
  border: none;
  padding: 0.5rem;
  border-radius: 6px;
  color: rgba(255, 255, 255, 0.7);
  cursor: pointer;
  transition: all 0.2s;
  
  &:hover {
    background: rgba(255, 255, 255, 0.2);
    color: #fff;
  }
`

const ViewButton = styled(Link)`
  background: linear-gradient(135deg, #7ee8fa 0%, #4d96ff 100%);
  color: #1a1a2e;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  text-decoration: none;
  font-weight: 600;
  font-size: 0.9rem;
  transition: transform 0.2s;
  
  &:hover {
    transform: translateY(-1px);
  }
`

interface Job {
  id: string
  title: string
  status: string
  progress: number
  source: string
  created_at: string
  game_id?: string
}

export default function Jobs() {
  const [jobs, setJobs] = useState<Job[]>([])
  const [loading, setLoading] = useState(true)
  
  useEffect(() => {
    fetchJobs()
    const interval = setInterval(fetchJobs, 5000) // Poll every 5 seconds
    return () => clearInterval(interval)
  }, [])
  
  const fetchJobs = async () => {
    try {
      const response = await api.get('/jobs/')
      setJobs(response.data)
    } catch (error) {
      console.error('Failed to fetch jobs:', error)
    } finally {
      setLoading(false)
    }
  }
  
  const deleteJob = async (jobId: string) => {
    try {
      await api.delete(`/jobs/${jobId}`)
      setJobs(jobs.filter(j => j.id !== jobId))
    } catch (error) {
      console.error('Failed to delete job:', error)
    }
  }
  
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <CheckCircle size={14} />
      case 'failed': return <XCircle size={14} />
      case 'processing': return <Loader2 size={14} className="animate-spin" />
      default: return <Clock size={14} />
    }
  }
  
  if (loading) {
    return (
      <JobsContainer>
        <Title>Processing Jobs</Title>
        <div style={{ textAlign: 'center', padding: '3rem' }}>
          <Loader2 className="animate-spin" size={32} color="#7ee8fa" />
        </div>
      </JobsContainer>
    )
  }
  
  return (
    <JobsContainer>
      <Title>Processing Jobs</Title>
      
      <JobList>
        {jobs.map(job => (
          <JobCard key={job.id}>
            <JobInfo>
              <JobTitle>{job.title}</JobTitle>
              <JobMeta>
                <span>{job.source}</span>
                <span>•</span>
                <span>{formatDistanceToNow(new Date(job.created_at))} ago</span>
              </JobMeta>
              {job.status === 'processing' && (
                <ProgressBar>
                  <ProgressFill progress={job.progress} />
                </ProgressBar>
              )}
            </JobInfo>
            
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
              <StatusBadge status={job.status}>
                {getStatusIcon(job.status)}
                {job.status}
              </StatusBadge>
              
              <ActionButtons>
                {job.status === 'completed' && job.game_id && (
                  <ViewButton to={`/game/${job.game_id}`}>
                    View Game
                  </ViewButton>
                )}
                <IconButton onClick={() => deleteJob(job.id)}>
                  <Trash2 size={16} />
                </IconButton>
              </ActionButtons>
            </div>
          </JobCard>
        ))}
      </JobList>
    </JobsContainer>
  )
}