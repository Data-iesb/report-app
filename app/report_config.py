"""
Simplified Report Configuration Manager
Each report has its own TOML configuration file that defines:
- Report metadata (title, description, author)
- Streamlit theme configuration
- Custom styling options
"""

import os
import shutil
import tempfile
import toml
from typing import Dict, Any, Optional

class ReportConfig:
    def __init__(self, config_dir: str = None):
        self.config_dir = config_dir or os.path.join(os.getcwd(), ".streamlit")
        self.current_config = os.path.join(self.config_dir, "config.toml")
        self.backup_config = None
        
    def load_report_config(self, config_content: str) -> Dict[str, Any]:
        """Load and parse TOML configuration content"""
        try:
            return toml.loads(config_content)
        except Exception as e:
            print(f"Error parsing TOML config: {e}")
            return {}
    
    def apply_streamlit_config(self, config_data: Dict[str, Any]) -> bool:
        """Apply Streamlit configuration from TOML data"""
        try:
            # Extract only Streamlit-related configuration
            streamlit_config = {}
            
            # Copy standard Streamlit sections if they exist
            for section in ['theme', 'server', 'browser', 'runner', 'logger', 'client']:
                if section in config_data:
                    streamlit_config[section] = config_data[section]
            
            if not streamlit_config:
                return False
                
            # Backup current config
            if os.path.exists(self.current_config):
                self.backup_config = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.toml')
                shutil.copy2(self.current_config, self.backup_config.name)
            
            # Write new config
            os.makedirs(self.config_dir, exist_ok=True)
            with open(self.current_config, 'w') as f:
                toml.dump(streamlit_config, f)
            
            return True
            
        except Exception as e:
            print(f"Error applying Streamlit config: {e}")
            return False
    
    def restore_config(self):
        """Restore the previous configuration"""
        if self.backup_config and os.path.exists(self.backup_config.name):
            try:
                shutil.copy2(self.backup_config.name, self.current_config)
                os.unlink(self.backup_config.name)
                self.backup_config = None
            except Exception as e:
                print(f"Error restoring config: {e}")
    
    def get_report_metadata(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract report metadata from configuration"""
        report_section = config_data.get('report', {})
        
        return {
            'titulo': report_section.get('title', 'Dashboard'),
            'descricao': report_section.get('description', 'Análise de dados interativa'),
            'autor': report_section.get('author', 'Autor não informado'),
            'created_at': report_section.get('created_at', ''),
            'updated_at': report_section.get('updated_at', ''),
            'enable_header': report_section.get('enable_header', True),
            'enable_footer': report_section.get('enable_footer', True),
            'custom_css': report_section.get('custom_css', '')
        }
