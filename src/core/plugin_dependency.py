"""
Plugin Dependency Management

This module provides dependency resolution for plugins.
"""

from typing import List, Dict, Set, Optional, Tuple
from dataclasses import dataclass
import re


@dataclass
class PluginDependency:
    """Plugin dependency specification"""
    name: str
    version_constraint: Optional[str] = None  # e.g., ">=1.0.0", "==1.2.3", "<2.0.0"

    @classmethod
    def parse(cls, dep_string: str) -> "PluginDependency":
        """
        Parse dependency string

        Args:
            dep_string: Dependency string (e.g., "plugin_name>=1.0.0")

        Returns:
            PluginDependency instance
        """
        # Match pattern: name[operator][version]
        pattern = r"^([a-zA-Z0-9_-]+)(>=|<=|==|>|<)?(.+)?$"
        match = re.match(pattern, dep_string.strip())

        if not match:
            raise ValueError(f"Invalid dependency string: {dep_string}")

        name = match.group(1)
        operator = match.group(2)
        version = match.group(3)

        version_constraint = None
        if operator and version:
            version_constraint = f"{operator}{version}"

        return cls(name=name, version_constraint=version_constraint)

    def check_version(self, version: str) -> bool:
        """
        Check if version satisfies constraint

        Args:
            version: Version string to check

        Returns:
            True if version satisfies constraint
        """
        if not self.version_constraint:
            return True

        # Parse constraint
        pattern = r"^(>=|<=|==|>|<)(.+)$"
        match = re.match(pattern, self.version_constraint)

        if not match:
            return True

        operator = match.group(1)
        required_version = match.group(2)

        # Simple version comparison (assumes semantic versioning)
        version_parts = [int(x) for x in version.split(".")]
        required_parts = [int(x) for x in required_version.split(".")]

        # Pad to same length
        max_len = max(len(version_parts), len(required_parts))
        version_parts += [0] * (max_len - len(version_parts))
        required_parts += [0] * (max_len - len(required_parts))

        if operator == "==":
            return version_parts == required_parts
        elif operator == ">=":
            return version_parts >= required_parts
        elif operator == "<=":
            return version_parts <= required_parts
        elif operator == ">":
            return version_parts > required_parts
        elif operator == "<":
            return version_parts < required_parts

        return True


class DependencyResolver:
    """
    Dependency resolver for plugins

    Resolves plugin dependencies and determines load order.
    """

    def __init__(self) -> None:
        self.plugins: Dict[str, Tuple[str, List[PluginDependency]]] = {}

    def add_plugin(
        self,
        name: str,
        version: str,
        dependencies: List[str]
    ) -> None:
        """
        Add plugin to resolver

        Args:
            name: Plugin name
            version: Plugin version
            dependencies: List of dependency strings
        """
        parsed_deps = [PluginDependency.parse(dep) for dep in dependencies]
        self.plugins[name] = (version, parsed_deps)

    def check_dependencies(self, plugin_name: str) -> Tuple[bool, List[str]]:
        """
        Check if plugin dependencies are satisfied

        Args:
            plugin_name: Name of plugin to check

        Returns:
            Tuple of (all_satisfied, missing_dependencies)
        """
        if plugin_name not in self.plugins:
            return False, [f"Plugin {plugin_name} not found"]

        _, dependencies = self.plugins[plugin_name]
        missing = []

        for dep in dependencies:
            if dep.name not in self.plugins:
                missing.append(f"{dep.name} (not installed)")
                continue

            dep_version, _ = self.plugins[dep.name]
            if not dep.check_version(dep_version):
                constraint = dep.version_constraint or "any"
                missing.append(
                    f"{dep.name} (requires {constraint}, found {dep_version})"
                )

        return len(missing) == 0, missing

    def resolve_load_order(self) -> Tuple[bool, List[str], List[str]]:
        """
        Resolve plugin load order using topological sort

        Returns:
            Tuple of (success, load_order, errors)
        """
        # Build dependency graph
        graph: Dict[str, Set[str]] = {}
        in_degree: Dict[str, int] = {}

        for plugin_name in self.plugins:
            graph[plugin_name] = set()
            in_degree[plugin_name] = 0

        for plugin_name, (_, dependencies) in self.plugins.items():
            for dep in dependencies:
                if dep.name in self.plugins:
                    graph[dep.name].add(plugin_name)
                    in_degree[plugin_name] += 1

        # Topological sort (Kahn's algorithm)
        queue = [name for name, degree in in_degree.items() if degree == 0]
        load_order = []

        while queue:
            current = queue.pop(0)
            load_order.append(current)

            for neighbor in graph[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        # Check for circular dependencies
        if len(load_order) != len(self.plugins):
            remaining = set(self.plugins.keys()) - set(load_order)
            errors = [f"Circular dependency detected involving: {', '.join(remaining)}"]
            return False, [], errors

        return True, load_order, []

    def get_dependency_tree(self, plugin_name: str) -> Dict[str, List[str]]:
        """
        Get dependency tree for a plugin

        Args:
            plugin_name: Name of plugin

        Returns:
            Dictionary mapping plugin names to their dependencies
        """
        if plugin_name not in self.plugins:
            return {}

        tree: Dict[str, List[str]] = {}
        visited: Set[str] = set()

        def build_tree(name: str) -> None:
            if name in visited or name not in self.plugins:
                return

            visited.add(name)
            _, dependencies = self.plugins[name]
            tree[name] = [dep.name for dep in dependencies]

            for dep in dependencies:
                build_tree(dep.name)

        build_tree(plugin_name)
        return tree
