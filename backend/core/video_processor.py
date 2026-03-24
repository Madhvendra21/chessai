import cv2
import logging
import yt_dlp
import os
import asyncio
from pathlib import Path
from typing import Optional, List, Dict, Callable
from dataclasses import dataclass
import aiohttp
import aiofiles

logger = logging.getLogger(__name__)


@dataclass
class VideoInfo:
    """Information about a video."""
    title: str
    duration: float
    width: int
    height: int
    fps: float
    path: str


class VideoDownloader:
    """Downloads videos from various sources."""
    
    def __init__(self, output_dir: str = "data/uploads"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    async def download_from_url(self, url: str, job_id: str) -> Optional[str]:
        """Download video from URL (YouTube or direct)."""
        output_path = self.output_dir / f"{job_id}.mp4"
        
        # Check if it's a YouTube URL
        if "youtube.com" in url or "youtu.be" in url:
            return await self._download_youtube(url, output_path)
        else:
            return await self._download_direct(url, output_path)
    
    async def _download_youtube(self, url: str, output_path: Path) -> Optional[str]:
        """Download from YouTube using yt-dlp."""
        try:
            ydl_opts = {
                'format': 'best[height<=720]',  # Limit to 720p for processing speed
                'outtmpl': str(output_path),
                'quiet': True,
                'no_warnings': True,
            }
            
            # Run in thread pool since yt-dlp is synchronous
            loop = asyncio.get_event_loop()
            
            def download():
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
            
            await loop.run_in_executor(None, download)
            
            if output_path.exists():
                logger.info(f"Downloaded YouTube video to {output_path}")
                return str(output_path)
            return None
        except Exception as e:
            logger.error(f"YouTube download failed: {e}")
            return None
    
    async def _download_direct(self, url: str, output_path: Path) -> Optional[str]:
        """Download from direct URL."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=300)) as response:
                    if response.status != 200:
                        logger.error(f"Download failed with status {response.status}")
                        return None
                    
                    async with aiofiles.open(output_path, 'wb') as f:
                        async for chunk in response.content.iter_chunked(8192):
                            await f.write(chunk)
            
            logger.info(f"Downloaded video to {output_path}")
            return str(output_path)
        except Exception as e:
            logger.error(f"Direct download failed: {e}")
            return None
    
    def get_video_info(self, video_path: str) -> Optional[VideoInfo]:
        """Extract video metadata."""
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                return None
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = frame_count / fps if fps > 0 else 0
            
            cap.release()
            
            # Get title from filename
            title = Path(video_path).stem
            
            return VideoInfo(
                title=title,
                duration=duration,
                width=width,
                height=height,
                fps=fps,
                path=video_path
            )
        except Exception as e:
            logger.error(f"Error getting video info: {e}")
            return None


class FrameExtractor:
    """Extracts frames from video for processing."""
    
    def __init__(self, output_dir: str = "data/frames", target_fps: int = 2):
        self.output_dir = Path(output_dir)
        self.target_fps = target_fps
    
    def extract_frames(self, video_path: str, job_id: str,
                      progress_callback: Optional[Callable[[int, int], None]] = None) -> List[str]:
        """
        Extract frames from video at target FPS.
        Returns list of frame file paths.
        """
        frames_dir = self.output_dir / job_id
        frames_dir.mkdir(parents=True, exist_ok=True)
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            logger.error(f"Cannot open video: {video_path}")
            return []
        
        video_fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Calculate frame skip interval
        if self.target_fps >= video_fps:
            frame_interval = 1
        else:
            frame_interval = int(video_fps / self.target_fps)
        
        frame_paths = []
        frame_count = 0
        extracted_count = 0
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_count % frame_interval == 0:
                    frame_path = frames_dir / f"frame_{extracted_count:06d}.jpg"
                    cv2.imwrite(str(frame_path), frame)
                    frame_paths.append(str(frame_path))
                    extracted_count += 1
                    
                    if progress_callback and frame_count % 30 == 0:
                        progress_callback(frame_count, total_frames)
                
                frame_count += 1
        finally:
            cap.release()
        
        logger.info(f"Extracted {len(frame_paths)} frames from {video_path}")
        return frame_paths
    
    def cleanup_frames(self, job_id: str):
        """Remove extracted frames for a job."""
        frames_dir = self.output_dir / job_id
        if frames_dir.exists():
            import shutil
            shutil.rmtree(frames_dir)
            logger.info(f"Cleaned up frames for job {job_id}")
