from unittest.mock import MagicMock, patch
import pytest
from gui.main import SyncApp
from core.orchestrator import FilePair

@patch('gui.main.ui')
def test_sync_app_init(mock_ui):
    app = SyncApp()
    assert app.log_queue is not None
    assert app.conflict_queue is not None
    app.setup_ui()
    # Check if UI setup was called
    mock_ui.header.assert_called()
    mock_ui.timer.assert_called()

@patch('gui.main.ui')
def test_sync_app_logging(mock_ui):
    app = SyncApp()
    app.setup_ui() # Initialize UI elements
    app.log_area = MagicMock()
    
    app.logger_callback("Test Log")
    assert not app.log_queue.empty()
    assert app.log_queue.get() == "Test Log"
    
    # Process logs
    app.log_queue.put("Process Me")
    app.process_logs()
    app.log_area.push.assert_called_with("Process Me")

@patch('gui.main.ui')
def test_sync_app_conflict(mock_ui):
    app = SyncApp()
    app.setup_ui() # Initialize UI elements
    app.conflict_dialog = MagicMock()
    app.conflict_details = MagicMock()
    
    pair = FilePair('test', None, None, 0, 0)
    
    # Trigger conflict
    app.conflict_queue.put(pair)
    app.process_conflicts()
    
    app.conflict_dialog.open.assert_called()
    
    # Resolve conflict
    app.resolve_conflict('source_to_target')
    app.conflict_dialog.close.assert_called()
    assert not app.response_queue.empty()
    assert app.response_queue.get() == 'source_to_target'
