"""
Module Discovery and Loading System.
Scans the modules/ directory and registers modules automatically.
"""
import os
import importlib.util
from pathlib import Path
from django.conf import settings


class ModuleLoader:
    """
    Scans the filesystem for modules and loads their configuration.
    """
    
    def __init__(self):
        self.modules_dir = Path(settings.BASE_DIR) / 'modules'
        self.discovered_modules = []
    
    def discover_modules(self):
        """
        Scan the modules/ directory for valid modules.
        A valid module has a plugin.py file with required attributes.
        """
        if not self.modules_dir.exists():
            print(f"Modules directory not found: {self.modules_dir}")
            return []
        
        self.discovered_modules = []
        
        # Iterate through subdirectories in modules/
        for module_path in self.modules_dir.iterdir():
            if not module_path.is_dir():
                continue
            
            # Skip __pycache__ and other special directories
            if module_path.name.startswith('_'):
                continue
            
            # Look for plugin.py
            plugin_file = module_path / 'plugin.py'
            if plugin_file.exists():
                module_info = self._load_plugin_config(plugin_file, module_path.name)
                if module_info:
                    self.discovered_modules.append(module_info)
        
        return self.discovered_modules
    
    def _load_plugin_config(self, plugin_file, module_dir_name):
        """
        Load configuration from plugin.py file.
        """
        try:
            # Dynamically import the plugin.py file
            spec = importlib.util.spec_from_file_location(
                f"modules.{module_dir_name}.plugin", 
                plugin_file
            )
            if spec and spec.loader:
                plugin_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(plugin_module)
                
                # Extract required attributes
                plugin_name = getattr(plugin_module, 'PLUGIN_NAME', None)
                slug = getattr(plugin_module, 'SLUG', None)
                description = getattr(plugin_module, 'DESCRIPTION', '')
                version = getattr(plugin_module, 'VERSION', '1.0.0')
                icon = getattr(plugin_module, 'ICON', '')
                color = getattr(plugin_module, 'COLOR', '')
                
                # Validate required fields
                if not plugin_name or not slug:
                    print(f"Warning: Module {module_dir_name} missing required fields (PLUGIN_NAME, SLUG)")
                    return None
                
                return {
                    'name': plugin_name,
                    'slug': slug,
                    'description': description,
                    'version': version,
                    'icon': icon,
                    'color': color,
                    'directory': module_dir_name,
                }
        except Exception as e:
            print(f"Error loading plugin from {plugin_file}: {e}")
            return None
    
    def sync_to_database(self):
        """
        Sync discovered modules to the database.
        Creates or updates Module records.
        """
        from core.plugins.models import Module
        
        discovered = self.discover_modules()
        synced_count = 0
        
        for module_info in discovered:
            module, created = Module.objects.update_or_create(
                slug=module_info['slug'],
                defaults={
                    'name': module_info['name'],
                    'description': module_info['description'],
                    'version': module_info['version'],
                    'icon': module_info['icon'],
                    'color': module_info['color'],
                    'is_active': True,
                }
            )
            synced_count += 1
            status = "Created" if created else "Updated"
            print(f"{status}: {module.name} ({module.slug})")
        
        return synced_count


# Global instance
module_loader = ModuleLoader()
