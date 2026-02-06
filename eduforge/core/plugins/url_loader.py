"""
Dynamic URL loader for modules.
Discovers and loads module URLs at runtime.
"""
from django.urls import path, include
from pathlib import Path
from importlib import import_module
import os


class ModuleURLLoader:
    """
    Dynamically loads URLs from installed modules.
    """
    
    def __init__(self):
        self.modules_dir = Path(__file__).resolve().parent.parent.parent / 'modules'
        self.discovered_urls = []
    
    def discover_module_urls(self):
        """
        Scan modules directory for urls.py files.
        Returns a list of URL patterns to include.
        """
        patterns = []
        
        if not self.modules_dir.exists():
            return patterns
        
        # Iterate through module directories
        for module_path in self.modules_dir.iterdir():
            if not module_path.is_dir():
                continue
            
            # Skip special directories
            if module_path.name.startswith('_'):
                continue
            
            # Check if urls.py exists
            urls_file = module_path / 'urls.py'
            if urls_file.exists():
                module_name = module_path.name
                try:
                    # Import the module's urls
                    urls_module = import_module(f'modules.{module_name}.urls')
                    
                    # Add to patterns with namespace
                    patterns.append(
                        path(f'{module_name}/', include((urls_module, module_name)))
                    )
                    print(f"Loaded URLs for module: {module_name}")
                except Exception as e:
                    print(f"Error loading URLs for {module_name}: {e}")
        
        return patterns
    
    def get_module_urls(self):
        """
        Get all module URL patterns.
        """
        return self.discover_module_urls()


# Global instance
url_loader = ModuleURLLoader()
