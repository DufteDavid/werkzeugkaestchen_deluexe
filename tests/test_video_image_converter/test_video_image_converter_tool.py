import pytest
import os
import uuid
import tempfile
import zipfile
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock, mock_open

import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from tools.video_image_converter.video_image_converter_tool import VideoImageConverterTool

ffmpeg_mock = MagicMock()
pil_mock = MagicMock()

@pytest.fixture(autouse=True)
def mock_dependencies():
    with patch('tools.video_image_converter.video_image_converter_tool.ffmpeg', ffmpeg_mock), \
         patch('tools.video_image_converter.video_image_converter_tool.Image', pil_mock):
        yield
        ffmpeg_mock.reset_mock()
        pil_mock.reset_mock()

@pytest.fixture
def converter_tool():
    """Provides an instance of the VideoImageConverterTool for testing."""
    tool = VideoImageConverterTool()
    tool.temp_dir = '/tmp/test_temp'
    tool.pending_conversions.clear()
    return tool

@pytest.fixture
def mock_temp_file():
    """Mock temporary file for testing."""
    return '/tmp/test_file.mp4'

class TestVideoImageConverterTool:
    """Test cases for VideoImageConverterTool."""

    def test_tool_initialization(self, converter_tool):
        """Test that the tool initializes correctly."""
        assert converter_tool.name == "Video/Bild Konverter"
        assert converter_tool.identifier == "VideoImageConverterTool"
        assert "file" in converter_tool.input_params
        assert "conversion_type" in converter_tool.input_params

    def test_is_video_file(self, converter_tool):
        """Test video file detection."""
        assert converter_tool._is_video_file("test.mp4") == True
        assert converter_tool._is_video_file("test.avi") == True
        assert converter_tool._is_video_file("test.mkv") == True
        assert converter_tool._is_video_file("test.txt") == False
        assert converter_tool._is_video_file("test.zip") == False

    def test_is_zip_file(self, converter_tool):
        """Test ZIP file detection."""
        assert converter_tool._is_zip_file("test.zip") == True
        assert converter_tool._is_zip_file("test.ZIP") == True
        assert converter_tool._is_zip_file("test.mp4") == False

    def test_is_image_file(self, converter_tool):
        """Test image file detection."""
        assert converter_tool._is_image_file("test.png") == True
        assert converter_tool._is_image_file("test.jpg") == True
        assert converter_tool._is_image_file("test.jpeg") == True
        assert converter_tool._is_image_file("test.gif") == True
        assert converter_tool._is_image_file("test.txt") == False

    @patch('os.path.getsize')
    def test_execute_tool_missing_file(self, mock_getsize, converter_tool):
        """Test execution with missing file parameter."""
        input_params = {}
        result = converter_tool.execute_tool(input_params)
        assert result == False
        assert "Bitte wählen Sie eine Datei aus" in converter_tool.error_message

    @patch('os.path.getsize')
    def test_execute_tool_file_too_large(self, mock_getsize, converter_tool):
        """Test execution with file too large."""
        mock_getsize.return_value = 3 * 1024 * 1024 * 1024  # 3GB
        input_params = {
            "file": {"file_path": "/test.mp4", "filename": "test.mp4"},
            "conversion_type": "video_to_images"
        }
        result = converter_tool.execute_tool(input_params)
        assert result == False
        assert "zu groß" in converter_tool.error_message

    @patch('os.path.getsize')
    def test_execute_tool_video_to_images_success(self, mock_getsize, converter_tool):
        """Test successful video to images conversion setup."""
        mock_getsize.return_value = 100 * 1024 * 1024  # 100MB
        input_params = {
            "file": {"file_path": "/test.mp4", "filename": "test.mp4"},
            "conversion_type": "video_to_images",
            "fps": "10",
            "image_format": "png"
        }
        result = converter_tool.execute_tool(input_params)
        assert result == True
        assert len(converter_tool.pending_conversions) == 1
        assert "Konvertierung gestartet" in converter_tool.output

    @patch('os.path.getsize')
    def test_execute_tool_images_to_video_success(self, mock_getsize, converter_tool):
        """Test successful images to video conversion setup."""
        mock_getsize.return_value = 100 * 1024 * 1024  # 100MB
        input_params = {
            "file": {"file_path": "/test.zip", "filename": "test.zip"},
            "conversion_type": "images_to_video",
            "fps": "24",
            "video_format": "mp4",
            "quality": "high"
        }
        result = converter_tool.execute_tool(input_params)
        assert result == True
        assert len(converter_tool.pending_conversions) == 1

    @patch('os.path.getsize')
    def test_execute_tool_invalid_video_file(self, mock_getsize, converter_tool):
        """Test execution with invalid video file for video_to_images."""
        mock_getsize.return_value = 100 * 1024 * 1024
        input_params = {
            "file": {"file_path": "/test.txt", "filename": "test.txt"},
            "conversion_type": "video_to_images"
        }
        result = converter_tool.execute_tool(input_params)
        assert result == False
        assert "Bitte wählen Sie eine Videodatei aus" in converter_tool.error_message

    @patch('os.path.getsize')
    def test_execute_tool_invalid_zip_file(self, mock_getsize, converter_tool):
        """Test execution with invalid ZIP file for images_to_video."""
        mock_getsize.return_value = 100 * 1024 * 1024
        input_params = {
            "file": {"file_path": "/test.mp4", "filename": "test.mp4"},
            "conversion_type": "images_to_video"
        }
        result = converter_tool.execute_tool(input_params)
        assert result == False
        assert "Bitte wählen Sie eine ZIP-Datei mit Bildern aus" in converter_tool.error_message

    def test_convert_and_save_invalid_token(self, converter_tool):
        """Test convert_and_save with invalid token."""
        result = converter_tool.convert_and_save("invalid_token")
        assert result is None

    def test_convert_and_save_already_downloaded(self, converter_tool):
        """Test convert_and_save with already downloaded conversion."""
        token = "test_token"
        converter_tool.pending_conversions[token] = {"downloaded": True}
        result = converter_tool.convert_and_save(token)
        assert result is None

    @patch('os.makedirs')
    @patch('os.listdir')
    @patch('os.remove')
    @patch('os.rmdir')
    @patch('zipfile.ZipFile')
    def test_video_to_images_conversion(self, mock_zipfile, mock_rmdir, mock_remove, 
                                       mock_listdir, mock_makedirs, converter_tool):
        """Test video to images conversion process."""
        token = "test_token"
        conversion = {
            "file_path": "/test.mp4",
            "conversion_type": "video_to_images",
            "fps": "10",
            "image_format": "png",
            "downloaded": False
        }
        converter_tool.pending_conversions[token] = conversion
        
        mock_listdir.return_value = ["frame_0001.png", "frame_0002.png"]
        mock_zipfile_instance = MagicMock()
        mock_zipfile.return_value.__enter__.return_value = mock_zipfile_instance
        
        result = converter_tool._video_to_images(token, conversion)
        
        assert result == f"/tmp/test_temp/images_{token}.zip"
        ffmpeg_mock.input.assert_called_once()
        ffmpeg_mock.output.assert_called_once()
        ffmpeg_mock.run.assert_called_once()
        mock_zipfile_instance.write.assert_called()

    @patch('os.makedirs')
    @patch('os.listdir')
    @patch('os.remove')
    @patch('os.rmdir')
    @patch('zipfile.ZipFile')
    def test_images_to_video_conversion(self, mock_zipfile, mock_rmdir, mock_remove,
                                       mock_listdir, mock_makedirs, converter_tool):
        """Test images to video conversion process."""
        token = "test_token"
        conversion = {
            "file_path": "/test.zip",
            "conversion_type": "images_to_video",
            "fps": "24",
            "video_format": "mp4",
            "quality": "medium",
            "downloaded": False
        }
        converter_tool.pending_conversions[token] = conversion
        
        # Mock ZIP file contents
        mock_file_info = MagicMock()
        mock_file_info.filename = "image1.png"
        mock_zipfile_instance = MagicMock()
        mock_zipfile_instance.filelist = [mock_file_info]
        mock_zipfile.return_value.__enter__.return_value = mock_zipfile_instance
        
        # Mock image processing
        mock_listdir.return_value = ["image1.png"]
        pil_mock.open.return_value.__enter__.return_value.size = (1920, 1080)
        pil_mock.open.return_value.__enter__.return_value.resize.return_value = MagicMock()
        pil_mock.open.return_value.__enter__.return_value.convert.return_value = MagicMock()
        
        result = converter_tool._images_to_video(token, conversion)
        
        assert result == f"/tmp/test_temp/video_{token}.mp4"
        ffmpeg_mock.input.assert_called()
        ffmpeg_mock.output.assert_called()
        ffmpeg_mock.run.assert_called()

    @patch('zipfile.ZipFile')
    def test_images_to_video_no_images_in_zip(self, mock_zipfile, converter_tool):
        """Test images to video conversion with no images in ZIP."""
        token = "test_token"
        conversion = {
            "file_path": "/test.zip",
            "conversion_type": "images_to_video",
            "downloaded": False
        }
        converter_tool.pending_conversions[token] = conversion
        
        # Mock empty ZIP file
        mock_zipfile_instance = MagicMock()
        mock_zipfile_instance.filelist = []
        mock_zipfile.return_value.__enter__.return_value = mock_zipfile_instance
        
        with pytest.raises(Exception, match="Keine Bilddateien in der ZIP-Datei gefunden"):
            converter_tool._images_to_video(token, conversion)

    @patch('os.path.exists')
    @patch('os.remove')
    def test_cleanup_old_files(self, mock_remove, mock_exists, converter_tool):
        """Test cleanup of old files."""
        mock_exists.return_value = True
        
        # Add old conversion
        old_token = "old_token"
        converter_tool.pending_conversions[old_token] = {
            "file_path": "/old_file.mp4",
            "conversion_type": "video_to_images",
            "timestamp": datetime.now() - timedelta(hours=2),
            "downloaded": False
        }
        
        # Add recent conversion
        recent_token = "recent_token"
        converter_tool.pending_conversions[recent_token] = {
            "file_path": "/recent_file.mp4",
            "conversion_type": "video_to_images", 
            "timestamp": datetime.now(),
            "downloaded": False
        }
        
        converter_tool.cleanup_old_files()
        
        # Old conversion should be removed
        assert old_token not in converter_tool.pending_conversions
        # Recent conversion should remain
        assert recent_token in converter_tool.pending_conversions
        
        mock_remove.assert_called()

    def test_cleanup_downloaded_files(self, converter_tool):
        """Test cleanup of downloaded files."""
        token = "downloaded_token"
        converter_tool.pending_conversions[token] = {
            "file_path": "/downloaded_file.mp4",
            "timestamp": datetime.now(),
            "downloaded": True
        }
        
        converter_tool.cleanup_old_files()
        
        # Downloaded conversion should be removed
        assert token not in converter_tool.pending_conversions