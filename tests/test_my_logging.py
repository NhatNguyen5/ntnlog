import os
import tempfile
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
from logging_module.my_logging import Logger
from logging_module.config import GLOBAL_LOGGING_ENABLED, GLOBAL_LOG_TRACING_ENABLED


class TestLogger:
    def setup_method(self):
        """Setup before each test."""
        self.Logger = Logger()

    def test_init(self):
        """Test Logger initialization."""
        assert self.Logger._enable is True
        assert self.Logger._enable_log_tracing is False

    @patch('logging_module.my_logging.datetime')
    @patch('logging_module.my_logging.file_verify_path')
    @patch('builtins.open', new_callable=MagicMock)
    def test_log_basic(self, mock_open, mock_verify_path, mock_datetime):
        """Test basic logging functionality."""
        # Setup mocks
        mock_datetime.now.return_value = datetime(2023, 5, 15, 10, 30, 45)
        mock_verify_path.return_value = "/tmp/logs"
        
        # Create a temporary directory for logs
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('os.path.join', return_value=os.path.join(temp_dir, "logs", "2023-05-15_logging.txt")):
                with patch('os.path.isfile', return_value=False):
                    with patch('os.makedirs'):
                        self.Logger.log("Test message")
                        
                        # Check that open was called for writing
                        assert mock_open.call_count >= 1  # Single open in append mode

    @patch('logging_module.my_logging.datetime')
    @patch('logging_module.my_logging.file_verify_path')
    @patch('builtins.open', new_callable=MagicMock)
    @patch('builtins.print')
    def test_log_with_console_output(self, mock_print, mock_open, mock_verify_path, mock_datetime):
        """Test logging with console output."""
        mock_datetime.now.return_value = datetime(2023, 5, 15, 10, 30, 45)
        mock_verify_path.return_value = "/tmp/logs"
        
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('os.path.join', return_value=os.path.join(temp_dir, "logs", "2023-05-15_logging.txt")):
                with patch('os.path.isfile', return_value=True):
                    self.Logger.log("Test message", print_to_console=True)
                    
                    # Check that print was called
                    mock_print.assert_called_once_with("Test message")

    @patch('logging_module.my_logging.datetime')
    @patch('logging_module.my_logging.file_verify_path')
    @patch('builtins.open', new_callable=MagicMock)
    @patch('builtins.print')
    def test_log_with_custom_console_message(self, mock_print, mock_open, mock_verify_path, mock_datetime):
        """Test logging with custom console message."""
        mock_datetime.now.return_value = datetime(2023, 5, 15, 10, 30, 45)
        mock_verify_path.return_value = "/tmp/logs"
        
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('os.path.join', return_value=os.path.join(temp_dir, "logs", "2023-05-15_logging.txt")):
                with patch('os.path.isfile', return_value=True):
                    self.Logger.log("Test message", print_to_console=True, console_message="Custom message")
                    
                    # Check that print was called with custom message
                    mock_print.assert_called_once_with("Custom message")

    def test_log_disabled_globally(self):
        """Test logging when globally disabled."""
        with patch('logging_module.my_logging.GLOBAL_LOGGING_ENABLED', False):
            with patch('builtins.open') as mock_open:
                self.Logger.log("Test message")
                mock_open.assert_not_called()

    def test_log_disabled_locally(self):
        """Test logging when locally disabled."""
        self.Logger.enable_logging(False)
        with patch('builtins.open') as mock_open:
            self.Logger.log("Test message")
            mock_open.assert_not_called()

    @patch('logging_module.my_logging.getframeinfo')
    @patch('logging_module.my_logging.stack')
    def test_get_caller_info_basic(self, mock_stack, mock_getframeinfo):
        """Test getting basic caller info."""
        mock_frame = MagicMock()
        mock_frame.filename = "/path/to/file.py"
        mock_frame.lineno = 42
        mock_getframeinfo.return_value = mock_frame
        mock_stack.return_value = [None, None, None, mock_frame]  # calldepth = 3
        
        result = self.Logger.get_caller_info()
        assert result == "file.py:42"

    @patch('logging_module.my_logging.getframeinfo')
    @patch('logging_module.my_logging.stack')
    def test_get_caller_info_tracing_disabled(self, mock_stack, mock_getframeinfo):
        """Test caller info when tracing is disabled."""
        self.Logger.enable_log_tracing(False)
        mock_frame = MagicMock()
        mock_frame.filename = "/path/to/file.py"
        mock_frame.lineno = 42
        mock_getframeinfo.return_value = mock_frame
        mock_stack.return_value = [None, None, None, mock_frame]
        
        result = self.Logger.get_caller_info()
        assert result == "file.py:42"

    @patch('logging_module.my_logging.getframeinfo')
    @patch('logging_module.my_logging.stack')
    def test_get_caller_info_tracing_enabled(self, mock_stack, mock_getframeinfo):
        """Test caller info when tracing is enabled."""
        self.Logger.enable_log_tracing(True)
        with patch('logging_module.my_logging.GLOBAL_LOG_TRACING_ENABLED', True):
            mock_frame1 = MagicMock()
            mock_frame1.filename = "/path/to/file1.py"
            mock_frame1.lineno = 10
            mock_frame2 = MagicMock()
            mock_frame2.filename = "/path/to/file2.py"
            mock_frame2.lineno = 20
            mock_getframeinfo.side_effect = [mock_frame1, mock_frame2]
            mock_stack.return_value = [None, None, None, mock_frame1, mock_frame2]
            
            result = self.Logger.get_caller_info()
            assert "file1.py:10>file2.py:20" in result

    def test_enable_logging(self):
        """Test enabling/disabling logging."""
        self.Logger.enable_logging(False)
        assert self.Logger._enable is False
        
        self.Logger.enable_logging(True)
        assert self.Logger._enable is True

    def test_enable_log_tracing(self):
        """Test enabling/disabling log tracing."""
        self.Logger.enable_log_tracing(True)
        assert self.Logger._enable_log_tracing is True
        
        self.Logger.enable_log_tracing(False)
        assert self.Logger._enable_log_tracing is False

    def test_call_method(self):
        """Test using Logger as callable."""
        with patch.object(self.Logger, 'log') as mock_log:
            self.Logger("Test message", print_to_console=True)
            mock_log.assert_called_once_with("Test message", print_to_console=True, console_message="")