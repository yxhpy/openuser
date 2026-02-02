"""
Plugin Registry

Provides plugin discovery, search, and management capabilities.
"""

import json
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests


@dataclass
class PluginMetadata:
    """Plugin metadata information"""

    name: str
    version: str
    description: str
    author: str = ""
    homepage: str = ""
    repository: str = ""
    license: str = ""
    dependencies: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    install_url: Optional[str] = None
    checksum: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PluginMetadata":
        """Create from dictionary"""
        return cls(**data)


class PluginRegistry:
    """
    Plugin Registry for managing plugin metadata and discovery

    Features:
    - Local plugin registry
    - Plugin search and discovery
    - Remote registry support
    - Plugin metadata management
    """

    def __init__(self, registry_path: str = ".plugin_registry.json"):
        """Initialize the plugin registry.

        Args:
            registry_path: Path to the local registry file
        """
        self.registry_path = Path(registry_path)
        self.plugins: Dict[str, PluginMetadata] = {}
        self._load_registry()

    def _load_registry(self) -> None:
        """Load the registry from disk"""
        if self.registry_path.exists():
            try:
                with open(self.registry_path, "r") as f:
                    data = json.load(f)
                    self.plugins = {
                        name: PluginMetadata.from_dict(meta)
                        for name, meta in data.items()
                    }
            except (json.JSONDecodeError, KeyError, TypeError):
                # If registry is corrupted, start fresh
                self.plugins = {}

    def _save_registry(self) -> None:
        """Save the registry to disk"""
        data = {name: meta.to_dict() for name, meta in self.plugins.items()}
        with open(self.registry_path, "w") as f:
            json.dump(data, f, indent=2)

    def register(self, metadata: PluginMetadata) -> None:
        """Register a plugin in the registry.

        Args:
            metadata: Plugin metadata to register
        """
        self.plugins[metadata.name] = metadata
        self._save_registry()

    def unregister(self, name: str) -> bool:
        """Unregister a plugin from the registry.

        Args:
            name: Plugin name to unregister

        Returns:
            True if plugin was unregistered, False if not found
        """
        if name in self.plugins:
            del self.plugins[name]
            self._save_registry()
            return True
        return False

    def get(self, name: str) -> Optional[PluginMetadata]:
        """Get plugin metadata by name.

        Args:
            name: Plugin name

        Returns:
            Plugin metadata if found, None otherwise
        """
        return self.plugins.get(name)

    def list_all(self) -> List[PluginMetadata]:
        """List all registered plugins.

        Returns:
            List of all plugin metadata
        """
        return list(self.plugins.values())

    def search(
        self,
        query: Optional[str] = None,
        tags: Optional[List[str]] = None,
        author: Optional[str] = None,
    ) -> List[PluginMetadata]:
        """Search for plugins.

        Args:
            query: Search query (matches name or description)
            tags: Filter by tags
            author: Filter by author

        Returns:
            List of matching plugin metadata
        """
        results = list(self.plugins.values())

        # Filter by query
        if query:
            query_lower = query.lower()
            results = [
                p
                for p in results
                if query_lower in p.name.lower() or query_lower in p.description.lower()
            ]

        # Filter by tags
        if tags:
            results = [p for p in results if any(tag in p.tags for tag in tags)]

        # Filter by author
        if author:
            author_lower = author.lower()
            results = [p for p in results if author_lower in p.author.lower()]

        return results

    def sync_from_remote(
        self, remote_url: str, merge: bool = True
    ) -> tuple[bool, str]:
        """Sync registry from a remote source.

        Args:
            remote_url: URL to the remote registry JSON
            merge: If True, merge with local registry; if False, replace

        Returns:
            Tuple of (success, message)
        """
        try:
            response = requests.get(remote_url, timeout=30)
            response.raise_for_status()

            remote_data = response.json()

            if merge:
                # Merge remote plugins with local
                for name, meta_dict in remote_data.items():
                    try:
                        metadata = PluginMetadata.from_dict(meta_dict)
                        # Only update if remote version is newer or plugin doesn't exist
                        if name not in self.plugins or self._is_newer_version(
                            metadata.version, self.plugins[name].version
                        ):
                            self.plugins[name] = metadata
                    except (KeyError, TypeError):
                        continue
            else:
                # Replace local registry with remote
                self.plugins = {
                    name: PluginMetadata.from_dict(meta)
                    for name, meta in remote_data.items()
                }

            self._save_registry()
            return True, f"Successfully synced {len(remote_data)} plugins from remote"

        except requests.RequestException as e:
            return False, f"Failed to sync from remote: {str(e)}"
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            return False, f"Invalid remote registry format: {str(e)}"

    def check_updates(self, remote_url: str) -> List[tuple[str, str, str]]:
        """Check for plugin updates from remote registry.

        Args:
            remote_url: URL to the remote registry JSON

        Returns:
            List of tuples (plugin_name, current_version, new_version)
        """
        updates = []

        try:
            response = requests.get(remote_url, timeout=30)
            response.raise_for_status()
            remote_data = response.json()

            for name, meta_dict in remote_data.items():
                if name in self.plugins:
                    remote_version = meta_dict.get("version", "0.0.0")
                    local_version = self.plugins[name].version

                    if self._is_newer_version(remote_version, local_version):
                        updates.append((name, local_version, remote_version))

        except (requests.RequestException, json.JSONDecodeError, KeyError):
            pass

        return updates

    def _is_newer_version(self, version1: str, version2: str) -> bool:
        """Compare two semantic versions.

        Args:
            version1: First version string (e.g., "1.2.3")
            version2: Second version string (e.g., "1.2.0")

        Returns:
            True if version1 is newer than version2
        """
        try:
            v1_parts = [int(x) for x in version1.split(".")]
            v2_parts = [int(x) for x in version2.split(".")]

            # Pad with zeros if needed
            max_len = max(len(v1_parts), len(v2_parts))
            v1_parts.extend([0] * (max_len - len(v1_parts)))
            v2_parts.extend([0] * (max_len - len(v2_parts)))

            return v1_parts > v2_parts
        except (ValueError, AttributeError):
            return False

    def export_to_file(self, output_path: str) -> None:
        """Export registry to a file.

        Args:
            output_path: Path to export the registry to
        """
        data = {name: meta.to_dict() for name, meta in self.plugins.items()}
        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)

    def import_from_file(self, input_path: str, merge: bool = True) -> tuple[bool, str]:
        """Import registry from a file.

        Args:
            input_path: Path to import the registry from
            merge: If True, merge with local registry; if False, replace

        Returns:
            Tuple of (success, message)
        """
        try:
            with open(input_path, "r") as f:
                data = json.load(f)

            if merge:
                for name, meta_dict in data.items():
                    try:
                        metadata = PluginMetadata.from_dict(meta_dict)
                        self.plugins[name] = metadata
                    except (KeyError, TypeError):
                        continue
            else:
                self.plugins = {
                    name: PluginMetadata.from_dict(meta)
                    for name, meta in data.items()
                }

            self._save_registry()
            return True, f"Successfully imported {len(data)} plugins"

        except FileNotFoundError:
            return False, f"File not found: {input_path}"
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            return False, f"Invalid registry format: {str(e)}"

    def get_stats(self) -> Dict[str, Any]:
        """Get registry statistics.

        Returns:
            Dictionary containing registry statistics
        """
        return {
            "total_plugins": len(self.plugins),
            "plugins_by_author": self._count_by_author(),
            "plugins_by_tag": self._count_by_tag(),
        }

    def _count_by_author(self) -> Dict[str, int]:
        """Count plugins by author"""
        counts: Dict[str, int] = {}
        for plugin in self.plugins.values():
            author = plugin.author or "Unknown"
            counts[author] = counts.get(author, 0) + 1
        return counts

    def _count_by_tag(self) -> Dict[str, int]:
        """Count plugins by tag"""
        counts: Dict[str, int] = {}
        for plugin in self.plugins.values():
            for tag in plugin.tags:
                counts[tag] = counts.get(tag, 0) + 1
        return counts
