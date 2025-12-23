import sys
from unittest.mock import patch, MagicMock
import pytest
from cli.main import main

def test_gui_launch_with_flag():
    with patch('gui.main.start') as mock_start:
        with patch('sys.argv', ['cli.main', '--gui']):
            ret = main()
            mock_start.assert_called_once()
            assert ret == 0

def test_gui_launch_no_args():
    with patch('gui.main.start') as mock_start:
        with patch('sys.argv', ['cli.main']):
            ret = main()
            mock_start.assert_called_once()
            assert ret == 0

def test_cli_launch_with_args():
    # Mock create_parser to avoid actual argument parsing errors for this test
    # or provide valid arguments
    with patch('gui.main.start') as mock_start:
        # Provide minimal valid arguments for CLI to avoid parser error or help exit
        # BUT we just want to ensure GUI NOT called.
        # However, main calls parser.parse_args which might exit.
        # We can patch create_parser to return a mock args object
        with patch('cli.main.create_parser') as mock_create_parser:
            mock_parser = MagicMock()
            mock_create_parser.return_value = mock_parser
            # mock args
            mock_args = MagicMock()
            mock_parser.parse_args.return_value = mock_args
            mock_args.convert_file = None
            mock_args.source_dir = None # This will trigger error in main, but that's after GUI check
            
            # We assume main() will return 1 because of missing args, but mock_start shouldn't be called
            with patch('sys.argv', ['cli.main', '--some-arg']):
                main()
                mock_start.assert_not_called()
