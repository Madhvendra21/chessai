import { useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { useDropzone } from 'react-dropzone'
import styled from 'styled-components'
import toast from 'react-hot-toast'
import { Upload as UploadIcon, Link, Loader2 } from 'lucide-react'
import api from '../api/client'

const UploadContainer = styled.div`
  max-width: 800px;
  margin: 0 auto;
`

const Title = styled.h1`
  color: #fff;
  margin-bottom: 2rem;
  text-align: center;
`

const Tabs = styled.div`
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
  justify-content: center;
`

const Tab = styled.button<{ active: boolean }>`
  padding: 0.75rem 1.5rem;
  background: ${props => props.active ? 'rgba(126, 232, 250, 0.2)' : 'rgba(255, 255, 255, 0.05)'};
  border: 1px solid ${props => props.active ? '#7ee8fa' : 'rgba(255, 255, 255, 0.1)'};
  border-radius: 8px;
  color: ${props => props.active ? '#7ee8fa' : 'rgba(255, 255, 255, 0.7)'};
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  
  &:hover {
    background: rgba(126, 232, 250, 0.1);
  }
`

const Dropzone = styled.div`
  border: 2px dashed rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  padding: 3rem;
  text-align: center;
  background: rgba(255, 255, 255, 0.02);
  transition: all 0.2s;
  cursor: pointer;
  
  &:hover {
    border-color: #7ee8fa;
    background: rgba(126, 232, 250, 0.05);
  }
`

const DropzoneText = styled.p`
  color: rgba(255, 255, 255, 0.6);
  margin-top: 1rem;
`

const UrlInput = styled.div`
  display: flex;
  gap: 1rem;
`

const Input = styled.input`
  flex: 1;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  color: #fff;
  font-size: 1rem;
  
  &:focus {
    outline: none;
    border-color: #7ee8fa;
  }
  
  &::placeholder {
    color: rgba(255, 255, 255, 0.4);
  }
`

const SubmitButton = styled.button`
  padding: 1rem 2rem;
  background: linear-gradient(135deg, #7ee8fa 0%, #4d96ff 100%);
  border: none;
  border-radius: 8px;
  color: #1a1a2e;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s;
  
  &:hover:not(:disabled) {
    transform: translateY(-2px);
  }
  
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
`

const ProgressContainer = styled.div`
  margin-top: 2rem;
  padding: 2rem;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  text-align: center;
`

const ProgressBar = styled.div`
  width: 100%;
  height: 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  overflow: hidden;
  margin: 1rem 0;
`

const ProgressFill = styled.div<{ progress: number }>`
  width: ${props => props.progress}%;
  height: 100%;
  background: linear-gradient(90deg, #7ee8fa, #4d96ff);
  transition: width 0.3s;
`

export default function Upload() {
  const [activeTab, setActiveTab] = useState<'file' | 'url'>('file')
  const [url, setUrl] = useState('')
  const [uploading, setUploading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [status, setStatus] = useState('')
  const navigate = useNavigate()
  
  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0]
    if (!file) return
    
    setUploading(true)
    setStatus('Uploading video...')
    
    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('title', file.name)
      
      const response = await api.post('/jobs/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      
      toast.success('Video uploaded successfully!')
      navigate(`/jobs`)
    } catch (error) {
      toast.error('Upload failed. Please try again.')
      console.error(error)
    } finally {
      setUploading(false)
    }
  }, [navigate])
  
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'video/*': ['.mp4', '.avi', '.mov']
    },
    maxFiles: 1,
    disabled: uploading
  })
  
  const handleUrlSubmit = async () => {
    if (!url.trim()) {
      toast.error('Please enter a URL')
      return
    }
    
    setUploading(true)
    setStatus('Starting download...')
    
    try {
      const response = await api.post('/jobs/from-url', {
        url: url.trim(),
        source: url.includes('youtube') ? 'youtube' : 'url'
      })
      
      toast.success('Job created successfully!')
      navigate('/jobs')
    } catch (error) {
      toast.error('Failed to create job. Please check the URL.')
      console.error(error)
    } finally {
      setUploading(false)
    }
  }
  
  return (
    <UploadContainer>
      <Title>Upload Chess Video</Title>
      
      <Tabs>
        <Tab 
          active={activeTab === 'file'} 
          onClick={() => setActiveTab('file')}
        >
          <UploadIcon size={18} />
          Upload File
        </Tab>
        <Tab 
          active={activeTab === 'url'} 
          onClick={() => setActiveTab('url')}
        >
          <Link size={18} />
          From URL
        </Tab>
      </Tabs>
      
      {activeTab === 'file' ? (
        <Dropzone {...getRootProps()}>
          <input {...getInputProps()} />
          <UploadIcon size={48} color="#7ee8fa" />
          {isDragActive ? (
            <DropzoneText>Drop the video here...</DropzoneText>
          ) : (
            <DropzoneText>
              Drag and drop a video file here, or click to select<br />
              <small>Supports MP4, AVI, MOV</small>
            </DropzoneText>
          )}
        </Dropzone>
      ) : (
        <UrlInput>
          <Input
            type="text"
            placeholder="Enter YouTube URL or direct video link..."
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            disabled={uploading}
          />
          <SubmitButton onClick={handleUrlSubmit} disabled={uploading}>
            {uploading ? <Loader2 className="animate-spin" /> : 'Process'}
          </SubmitButton>
        </UrlInput>
      )}
      
      {uploading && (
        <ProgressContainer>
          <Loader2 className="animate-spin" size={32} color="#7ee8fa" />
          <p style={{ color: '#fff', marginTop: '1rem' }}>{status}</p>
          <ProgressBar>
            <ProgressFill progress={progress} />
          </ProgressBar>
        </ProgressContainer>
      )}
    </UploadContainer>
  )
}