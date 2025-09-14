import pytest
import os
import uuid
import tempfile
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# Ensure the tools directory is in the Python path
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from tools.gif_video_converter.gif_video_converter_tool import GifVideoConverterTool

# Mock ffmpeg globally for all tests in this module
ffmpeg_mock = MagicMock()

@pytest.fixture(autouse=True)
def mock_ffmpeg():
    with patch('tools.gif_video_converter.gif_video_converter_tool.ffmpeg', ffmpeg_mock):
        yield
        ffmpeg_mock.reset_mock() # Reset mock after each test

@pytest.fixture
def converter_tool():
    """Provides an instance of the GifVideoConverterTool for testing."""
    tool = GifVideoConverterTool()
    # Ensure the instance uses the mocked temp dir path
    tool.temp_dir = '/tmp/test_temp'
    # Clear pending conversions before each test
    tool.pending_conversions.clear()
    return tool

@pytest.fixture
def mock_dependencies(monkeypatch):
    """Mocks external dependencies like os, uuid, datetime."""
    # Mock os.path.getsize to return a small size by default
    monkeypatch.setattr(os.path, 'getsize', lambda x: 10 * 1024 * 1024) # 10MB
    # Mock os.path.exists
    monkeypatch.setattr(os.path, 'exists', lambda x: True)
    # Mock os.remove
    monkeypatch.setattr(os, 'remove', MagicMock())
    # Mock uuid.uuid4 to return a predictable token
    monkeypatch.setattr(uuid, 'uuid4', lambda: uuid.UUID('12345678-1234-5678-1234-567812345678'))
    # Mock tempfile.gettempdir
    monkeypatch.setattr(tempfile, 'gettempdir', lambda: '/tmp/test_temp')
    # Mock datetime.now
    mock_now = datetime(2024, 1, 1, 12, 0, 0)
    monkeypatch.setattr('tools.gif_video_converter.gif_video_converter_tool.datetime', MagicMock(now=lambda: mock_now))


class TestGifVideoConverterTool:

    def test_initialization(self, converter_tool):
        """Test if the tool initializes correctly."""
        assert converter_tool.name == "GIF/Video Konverter"
        assert converter_tool.description == "Konvertiert Videos in GIFs und umgekehrt"
        assert "file" in converter_tool.input_params

    def test_execute_tool_missing_file(self, converter_tool):
        """Test execute_tool when the 'file' parameter is missing."""
        input_params = {}
        result = converter_tool.execute_tool(input_params)
        assert result is False
        assert converter_tool.error_message == "Bitte wählen Sie eine Datei aus."

    def test_execute_tool_file_too_large(self, converter_tool, mock_dependencies, monkeypatch):
        """Test execute_tool with a file size exceeding the limit."""
        # Mock os.path.getsize to return a large size
        monkeypatch.setattr(os.path, 'getsize', lambda x: 2 * 1024 * 1024 * 1024) # 2GB

        input_params = {
            "file": {"file_path": "/fake/path/video.mp4", "filename": "video.mp4"}
        }
        result = converter_tool.execute_tool(input_params)
        assert result is False
        assert converter_tool.error_message == "Die Datei ist zu groß. Maximale Größe ist 1GB."

    def test_execute_tool_video_to_gif_success(self, converter_tool, mock_dependencies):
        """Test successful execution for Video to GIF conversion."""
        input_params = {
            "file": {"file_path": "/fake/path/video.mp4", "filename": "video.mp4"},
            "quality": "high",
            "fps": "15",
            "resize": "medium"
        }
        expected_token = "12345678-1234-5678-1234-567812345678"

        result = converter_tool.execute_tool(input_params)

        assert result is True
        assert converter_tool.error_message == ""
        assert expected_token in converter_tool.output # Check if token is in the download link
        assert "Video zu GIF Konvertierung wurde erfolgreich gestartet" in converter_tool.output
        assert expected_token in converter_tool.pending_conversions
        conversion_data = converter_tool.pending_conversions[expected_token]
        assert conversion_data["file_path"] == "/fake/path/video.mp4"
        assert conversion_data["is_gif"] is False
        assert conversion_data["filename"] == "video.mp4"
        assert conversion_data["quality"] == "high"
        assert conversion_data["fps"] == "15"
        assert conversion_data["resize"] == "medium"
        assert conversion_data["format"] is None
        assert conversion_data["loop"] == "0"  # Default loop value
        assert conversion_data["downloaded"] is False

    def test_execute_tool_video_to_gif_with_custom_loop(self, converter_tool, mock_dependencies):
        """Test successful execution for Video to GIF conversion with custom loop count."""
        input_params = {
            "file": {"file_path": "/fake/path/video.mp4", "filename": "video.mp4"},
            "quality": "medium",
            "fps": "10",
            "resize": "small",
            "loop": "3"
        }
        expected_token = "12345678-1234-5678-1234-567812345678"

        result = converter_tool.execute_tool(input_params)

        assert result is True
        assert converter_tool.error_message == ""
        assert expected_token in converter_tool.pending_conversions
        conversion_data = converter_tool.pending_conversions[expected_token]
        assert conversion_data["loop"] == "3"
        assert conversion_data["quality"] == "medium"
        assert conversion_data["fps"] == "10"
        assert conversion_data["resize"] == "small"

    def test_execute_tool_gif_to_video_success(self, converter_tool, mock_dependencies):
        """Test successful execution for GIF to Video conversion."""
        input_params = {
            "file": {"file_path": "/fake/path/animation.gif", "filename": "animation.gif"},
            "quality": "low",
            "format": "webm"
        }
        expected_token = "12345678-1234-5678-1234-567812345678"

        result = converter_tool.execute_tool(input_params)

        assert result is True
        assert converter_tool.error_message == ""
        assert expected_token in converter_tool.output # Check if token is in the download link
        assert "GIF zu Video Konvertierung wurde erfolgreich gestartet" in converter_tool.output
        assert expected_token in converter_tool.pending_conversions
        conversion_data = converter_tool.pending_conversions[expected_token]
        assert conversion_data["file_path"] == "/fake/path/animation.gif"
        assert conversion_data["is_gif"] is True
        assert conversion_data["filename"] == "animation.gif"
        assert conversion_data["quality"] == "low"
        assert conversion_data["fps"] == "10" # Default FPS
        assert conversion_data["resize"] is None
        assert conversion_data["format"] == "webm"
        assert conversion_data["loop"] is None  # No loop for GIF to video
        assert conversion_data["downloaded"] is False

    def test_convert_and_save_video_to_gif(self, converter_tool, mock_dependencies):
        """Test the convert_and_save method for Video to GIF."""
        # First, execute the tool to set up the conversion
        input_params = {
            "file": {"file_path": "/fake/path/video.mp4", "filename": "video.mp4"},
            "quality": "medium",
            "fps": "12",
            "resize": "small"
        }
        token = "12345678-1234-5678-1234-567812345678"
        converter_tool.execute_tool(input_params) # Sets up pending_conversions

        # Mock ffmpeg calls specifically for this conversion type
        ffmpeg_mock.input.return_value = ffmpeg_mock
        ffmpeg_mock.output.return_value = ffmpeg_mock

        expected_output_path = f"/tmp/test_temp/converted_{token}.gif"
        output_path = converter_tool.convert_and_save(token)

        assert output_path == expected_output_path
        ffmpeg_mock.input.assert_called_once_with("/fake/path/video.mp4")
        ffmpeg_mock.output.assert_called_once_with(
            ffmpeg_mock, # The stream object from input()
            expected_output_path,
            vf="fps=12,scale=320:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=256:stats_mode=diff[p];[s1][p]paletteuse=dither=2",
            loop=0  # Default loop value
        )
        ffmpeg_mock.run.assert_called_once_with(ffmpeg_mock, overwrite_output=True, quiet=True)

    def test_convert_and_save_video_to_gif_with_custom_loop(self, converter_tool, mock_dependencies):
        """Test the convert_and_save method for Video to GIF with custom loop count."""
        # First, execute the tool to set up the conversion with custom loop
        input_params = {
            "file": {"file_path": "/fake/path/video.mp4", "filename": "video.mp4"},
            "quality": "high",
            "fps": "15",
            "resize": "large",
            "loop": "5"
        }
        token = "12345678-1234-5678-1234-567812345678"
        converter_tool.execute_tool(input_params) # Sets up pending_conversions

        # Mock ffmpeg calls specifically for this conversion type
        ffmpeg_mock.input.return_value = ffmpeg_mock
        ffmpeg_mock.output.return_value = ffmpeg_mock

        expected_output_path = f"/tmp/test_temp/converted_{token}.gif"
        output_path = converter_tool.convert_and_save(token)

        assert output_path == expected_output_path
        ffmpeg_mock.input.assert_called_once_with("/fake/path/video.mp4")
        ffmpeg_mock.output.assert_called_once_with(
            ffmpeg_mock, # The stream object from input()
            expected_output_path,
            vf="fps=15,scale=640:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=256:stats_mode=diff[p];[s1][p]paletteuse=dither=4",
            loop=5  # Custom loop value
        )
        ffmpeg_mock.run.assert_called_once_with(ffmpeg_mock, overwrite_output=True, quiet=True)

    def test_convert_and_save_gif_to_video(self, converter_tool, mock_dependencies):
        """Test the convert_and_save method for GIF to Video."""
        # First, execute the tool to set up the conversion
        input_params = {
            "file": {"file_path": "/fake/path/animation.gif", "filename": "animation.gif"},
            "quality": "high",
            "format": "mp4"
        }
        token = "12345678-1234-5678-1234-567812345678"
        converter_tool.execute_tool(input_params) # Sets up pending_conversions

        # Mock ffmpeg calls specifically for this conversion type
        ffmpeg_mock.input.return_value = ffmpeg_mock
        ffmpeg_mock.output.return_value = ffmpeg_mock

        expected_output_path = f"/tmp/test_temp/converted_{token}.mp4"
        output_path = converter_tool.convert_and_save(token)

        assert output_path == expected_output_path
        ffmpeg_mock.input.assert_called_once_with("/fake/path/animation.gif")
        ffmpeg_mock.output.assert_called_once_with(
            ffmpeg_mock, # The stream object from input()
            expected_output_path,
            vcodec='libx264',
            pix_fmt='yuv420p',
            crf="18",
            preset="slow"
        )
        ffmpeg_mock.run.assert_called_once_with(ffmpeg_mock, overwrite_output=True, quiet=True)

    def test_convert_and_save_invalid_token(self, converter_tool, mock_dependencies):
        """Test convert_and_save with a non-existent token."""
        output_path = converter_tool.convert_and_save("invalid-token")
        assert output_path is None
        ffmpeg_mock.run.assert_not_called()

    def test_convert_and_save_already_downloaded(self, converter_tool, mock_dependencies):
        """Test convert_and_save when the conversion is marked as downloaded."""
        input_params = {
            "file": {"file_path": "/fake/path/video.mp4", "filename": "video.mp4"}
        }
        token = "12345678-1234-5678-1234-567812345678"
        converter_tool.execute_tool(input_params)
        converter_tool.pending_conversions[token]["downloaded"] = True # Mark as downloaded

        output_path = converter_tool.convert_and_save(token)
        assert output_path is None
        ffmpeg_mock.run.assert_not_called()

    def test_cleanup_old_files(self, converter_tool, mock_dependencies, monkeypatch):
        """Test the cleanup_old_files method."""
        # Setup multiple conversions with different timestamps and downloaded states
        token_old = "old-token"
        token_recent = "recent-token"
        token_downloaded = "downloaded-token"

        mock_now = datetime(2024, 1, 1, 12, 0, 0)
        old_time = mock_now - timedelta(hours=2)
        recent_time = mock_now - timedelta(minutes=30)

        converter_tool.pending_conversions = {
            token_old: {
                "file_path": "/fake/path/old.gif", "is_gif": True, "format": "mp4",
                "timestamp": old_time, "downloaded": False
            },
            token_recent: {
                "file_path": "/fake/path/recent.mp4", "is_gif": False,
                "timestamp": recent_time, "downloaded": False
            },
            token_downloaded: {
                "file_path": "/fake/path/downloaded.gif", "is_gif": True, "format": "webm",
                "timestamp": recent_time, "downloaded": True
            }
        }

        # Mock os.remove to track calls
        remove_mock = MagicMock()
        monkeypatch.setattr(os, 'remove', remove_mock)

        # Mock datetime.now for cleanup comparison
        monkeypatch.setattr('tools.gif_video_converter.gif_video_converter_tool.datetime', MagicMock(now=lambda: mock_now))

        converter_tool.cleanup_old_files()

        # Assertions
        assert token_old not in converter_tool.pending_conversions
        assert token_downloaded not in converter_tool.pending_conversions
        assert token_recent in converter_tool.pending_conversions # Should remain

        # Check if correct files were attempted to be removed
        expected_removals = [
            "/fake/path/old.gif",
            f"/tmp/test_temp/converted_{token_old}.mp4",
            "/fake/path/downloaded.gif",
            f"/tmp/test_temp/converted_{token_downloaded}.webm"
        ]
        # Check that remove was called for each expected path
        assert remove_mock.call_count == len(expected_removals)
        called_paths = [call.args[0] for call in remove_mock.call_args_list]
        assert sorted(called_paths) == sorted(expected_removals)

    def test_convert_and_save_ffmpeg_error(self, converter_tool, mock_dependencies):
        """Test convert_and_save when ffmpeg.run raises an exception."""
        input_params = {
            "file": {"file_path": "/fake/path/video.mp4", "filename": "video.mp4"}
        }
        token = "12345678-1234-5678-1234-567812345678"
        converter_tool.execute_tool(input_params)

        # Mock ffmpeg.run to raise an exception
        ffmpeg_mock.run.side_effect = Exception("FFmpeg failed")

        output_path = converter_tool.convert_and_save(token)

        assert output_path is None
        ffmpeg_mock.run.assert_called_once() # Ensure it was called
