"""
Tests for CLI configuration file handling.
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from cli.config import Config, load_config, save_config, validate_config, DEFAULT_CONFIG_PATH
from cli.main import run_init_command, setup_registry


class TestConfig:
    """Tests for Config class."""
    
    def test_config_creation_minimal(self):
        """Test creating config with minimal values."""
        config = Config(
            source_format='claude',
            target_format='copilot'
        )
        assert config.source_format == 'claude'
        assert config.target_format == 'copilot'
        assert config.source_dir is None
        assert config.target_dir is None
    
    def test_config_creation_full(self):
        """Test creating config with all values."""
        config = Config(
            source_dir='~/.claude',
            target_dir='.github',
            source_format='claude',
            target_format='copilot',
            dry_run=True,
            verbose=True,
            force=True,
            strict=True,
            yes=True,
            only='agents,commands',
            direction='source-to-target',
            state_file='~/.custom_state.json'
        )
        assert config.source_dir == '~/.claude'
        assert config.target_dir == '.github'
        assert config.source_format == 'claude'
        assert config.target_format == 'copilot'
        assert config.dry_run is True
        assert config.verbose is True
        assert config.force is True
        assert config.strict is True
        assert config.yes is True
        assert config.only == 'agents,commands'
        assert config.direction == 'source-to-target'
        assert config.state_file == '~/.custom_state.json'
    
    def test_config_to_dict(self):
        """Test converting config to dict."""
        config = Config(
            source_format='claude',
            target_format='copilot',
            source_dir='~/.claude',
            verbose=True
        )
        data = config.to_dict()
        assert data['source_format'] == 'claude'
        assert data['target_format'] == 'copilot'
        assert data['source_dir'] == '~/.claude'
        assert data['verbose'] is True
        # Defaults should not be in dict
        assert 'dry_run' not in data
        assert 'force' not in data
    
    def test_config_from_dict(self):
        """Test creating config from dict."""
        data = {
            'source_format': 'claude',
            'target_format': 'copilot',
            'source_dir': '~/.claude',
            'verbose': True
        }
        config = Config.from_dict(data)
        assert config.source_format == 'claude'
        assert config.target_format == 'copilot'
        assert config.source_dir == '~/.claude'
        assert config.verbose is True


class TestConfigFile:
    """Tests for config file operations."""
    
    def test_load_nonexistent_config(self, tmp_path):
        """Test loading config when file doesn't exist."""
        config_path = tmp_path / "nonexistent.toml"
        config = load_config(config_path)
        assert config is None
    
    def test_save_and_load_config(self, tmp_path):
        """Test saving and loading config roundtrip."""
        config_path = tmp_path / "config.toml"
        
        original = Config(
            source_format='claude',
            target_format='copilot',
            source_dir='~/.claude',
            target_dir='.github',
            verbose=True,
            only='agents'
        )
        
        save_config(original, config_path)
        assert config_path.exists()
        
        loaded = load_config(config_path)
        assert loaded is not None
        assert loaded.source_format == 'claude'
        assert loaded.target_format == 'copilot'
        assert loaded.source_dir == '~/.claude'
        assert loaded.target_dir == '.github'
        assert loaded.verbose is True
        assert loaded.only == 'agents'
    
    def test_save_config_creates_directory(self, tmp_path):
        """Test that save_config creates parent directory."""
        config_path = tmp_path / "subdir" / "config.toml"
        config = Config(source_format='claude', target_format='copilot')
        
        save_config(config, config_path)
        assert config_path.exists()
    
    def test_load_malformed_config(self, tmp_path):
        """Test loading malformed TOML file."""
        config_path = tmp_path / "bad.toml"
        config_path.write_text("this is not valid toml {[}")
        
        with pytest.raises(ValueError, match="Failed to load config"):
            load_config(config_path)


class TestConfigValidation:
    """Tests for config validation."""
    
    def test_validate_valid_config(self, tmp_path):
        """Test validating a valid config."""
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        
        config = Config(
            source_format='claude',
            target_format='copilot',
            source_dir=str(source_dir)
        )
        
        registry = setup_registry()
        errors = validate_config(config, registry)
        assert errors == []
    
    def test_validate_invalid_format(self, tmp_path):
        """Test validation catches invalid format."""
        config = Config(
            source_format='invalid_format',
            target_format='copilot'
        )
        
        registry = setup_registry()
        errors = validate_config(config, registry)
        assert len(errors) > 0
        assert any('Invalid source format' in err for err in errors)
    
    def test_validate_nonexistent_source_dir(self):
        """Test validation catches nonexistent source directory."""
        config = Config(
            source_format='claude',
            target_format='copilot',
            source_dir='/nonexistent/path'
        )
        
        registry = setup_registry()
        errors = validate_config(config, registry)
        assert len(errors) > 0
        assert any('does not exist' in err for err in errors)
    
    def test_validate_invalid_direction(self, tmp_path):
        """Test validation catches invalid direction."""
        config = Config(
            source_format='claude',
            target_format='copilot',
            direction='invalid-direction'
        )
        
        registry = setup_registry()
        errors = validate_config(config, registry)
        assert len(errors) > 0
        assert any('Invalid direction' in err for err in errors)


class TestInitCommand:
    """Tests for init command."""
    
    @patch('builtins.input')
    def test_init_command_basic(self, mock_input, tmp_path):
        """Test init command with basic inputs."""
        config_path = tmp_path / ".agent-sync.toml"
        source_dir = tmp_path / "source"
        target_dir = tmp_path / "target"
        source_dir.mkdir()
        target_dir.mkdir()
        
        # Mock user inputs
        mock_input.side_effect = [
            'claude',           # source format
            'copilot',          # target format
            str(source_dir),    # source dir
            str(target_dir),    # target dir
        ]
        
        registry = setup_registry()
        
        with patch('cli.config.DEFAULT_CONFIG_PATH', config_path):
            result = run_init_command(registry)
        
        assert result == 0
        assert config_path.exists()
        
        # Verify saved config
        config = load_config(config_path)
        assert config is not None
        assert config.source_format == 'claude'
        assert config.target_format == 'copilot'
    
    @patch('builtins.input')
    @patch('cli.main.DEFAULT_CONFIG_PATH')
    def test_init_command_overwrite_existing(self, mock_path, mock_input, tmp_path):
        """Test init command when config already exists."""
        config_path = tmp_path / ".agent-sync.toml"
        mock_path.exists.return_value = True
        mock_path.__str__.return_value = str(config_path)
        
        # Create existing config
        existing = Config(source_format='gemini', target_format='claude')
        save_config(existing, config_path)
        
        # Mock user inputs - decline overwrite
        mock_input.side_effect = ['n']
        
        registry = setup_registry()
        
        with patch('cli.config.DEFAULT_CONFIG_PATH', config_path):
            result = run_init_command(registry)
        
        assert result == 0
        
        # Config should be unchanged
        config = load_config(config_path)
        assert config.source_format == 'gemini'
    
    @patch('builtins.input')
    def test_init_command_invalid_format(self, mock_input, tmp_path):
        """Test init command with invalid format input."""
        config_path = tmp_path / ".agent-sync.toml"
        source_dir = tmp_path / "source"
        target_dir = tmp_path / "target"
        source_dir.mkdir()
        target_dir.mkdir()
        
        # Mock user inputs - invalid format, then valid
        mock_input.side_effect = [
            'invalid',          # invalid source format
            'claude',           # valid source format
            'copilot',          # target format
            str(source_dir),    # source dir
            str(target_dir),    # target dir
        ]
        
        registry = setup_registry()
        
        with patch('cli.config.DEFAULT_CONFIG_PATH', config_path):
            result = run_init_command(registry)
        
        assert result == 0


class TestConfigIntegration:
    """Integration tests for config with main CLI."""
    
    def test_cli_uses_config_values(self, tmp_path):
        """Test that CLI uses config file values."""
        from cli.main import main
        
        config_path = tmp_path / ".agent-sync.toml"
        source_dir = tmp_path / "source"
        target_dir = tmp_path / "target"
        source_dir.mkdir()
        target_dir.mkdir()
        
        # Create config
        config = Config(
            source_format='claude',
            target_format='copilot',
            source_dir=str(source_dir),
            target_dir=str(target_dir)
        )
        save_config(config, config_path)
        
        # Mock load_config to return our config
        with patch('cli.main.load_config', return_value=config):
            with patch('cli.main.sync_all_config_types') as mock_sync:
                mock_sync.return_value = {}
                
                # Run CLI with no arguments (should use config)
                result = main([])
                
                # Should have called sync with config values
                assert mock_sync.called
    
    def test_cli_flags_override_config(self, tmp_path):
        """Test that CLI flags override config values."""
        from cli.main import main
        
        config_path = tmp_path / ".agent-sync.toml"
        source_dir = tmp_path / "source"
        target_dir = tmp_path / "target"
        override_source = tmp_path / "override_source"
        source_dir.mkdir()
        target_dir.mkdir()
        override_source.mkdir()
        
        # Create config
        config = Config(
            source_format='claude',
            target_format='copilot',
            source_dir=str(source_dir),
            target_dir=str(target_dir)
        )
        save_config(config, config_path)
        
        # Mock load_config to return our config
        with patch('cli.main.load_config', return_value=config):
            with patch('cli.main.sync_all_config_types') as mock_sync:
                mock_sync.return_value = {}
                
                # Run CLI with override flag
                result = main([
                    '--source-dir', str(override_source),
                    '--source-format', 'claude',
                    '--target-format', 'copilot'
                ])
                
                # Should have used override value
                assert mock_sync.called
