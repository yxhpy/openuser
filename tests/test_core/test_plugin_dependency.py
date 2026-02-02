"""Tests for plugin dependency management"""

import pytest
from src.core.plugin_dependency import (
    PluginDependency,
    DependencyResolver,
)


class TestPluginDependency:
    """Test PluginDependency class"""

    def test_parse_simple_dependency(self):
        """Test parsing simple dependency without version"""
        dep = PluginDependency.parse("plugin_name")

        assert dep.name == "plugin_name"
        assert dep.version_constraint is None

    def test_parse_dependency_with_version_gte(self):
        """Test parsing dependency with >= constraint"""
        dep = PluginDependency.parse("plugin_name>=1.0.0")

        assert dep.name == "plugin_name"
        assert dep.version_constraint == ">=1.0.0"

    def test_parse_dependency_with_version_eq(self):
        """Test parsing dependency with == constraint"""
        dep = PluginDependency.parse("plugin_name==1.2.3")

        assert dep.name == "plugin_name"
        assert dep.version_constraint == "==1.2.3"

    def test_parse_dependency_with_version_lt(self):
        """Test parsing dependency with < constraint"""
        dep = PluginDependency.parse("plugin_name<2.0.0")

        assert dep.name == "plugin_name"
        assert dep.version_constraint == "<2.0.0"

    def test_parse_dependency_with_hyphen(self):
        """Test parsing dependency with hyphen in name"""
        dep = PluginDependency.parse("plugin-name>=1.0.0")

        assert dep.name == "plugin-name"
        assert dep.version_constraint == ">=1.0.0"

    def test_parse_empty_dependency(self):
        """Test parsing empty dependency string"""
        with pytest.raises(ValueError):
            PluginDependency.parse("")

    def test_check_version_unknown_operator(self):
        """Test version check with unknown operator (defensive code path)"""
        dep = PluginDependency(name="plugin", version_constraint="~=1.0.0")

        # Should return True for unknown operators (defensive fallback)
        assert dep.check_version("1.0.0") is True

    def test_check_version_invalid_constraint(self):
        """Test version check with invalid constraint format"""
        dep = PluginDependency(name="plugin", version_constraint="invalid")

        # Should return True for invalid constraints
        assert dep.check_version("1.0.0") is True

    def test_check_version_with_different_length_versions(self):
        """Test version check with different length version numbers"""
        dep = PluginDependency(name="plugin", version_constraint=">=1.0")

        # Should pad shorter versions with zeros
        assert dep.check_version("1.0.0") is True
        assert dep.check_version("1.0.1") is True
        assert dep.check_version("0.9.9") is False

    def test_check_version_no_constraint(self):
        """Test version check with no constraint"""
        dep = PluginDependency(name="plugin", version_constraint=None)

        assert dep.check_version("1.0.0") is True
        assert dep.check_version("2.5.3") is True

    def test_check_version_eq(self):
        """Test version check with == constraint"""
        dep = PluginDependency(name="plugin", version_constraint="==1.2.3")

        assert dep.check_version("1.2.3") is True
        assert dep.check_version("1.2.4") is False
        assert dep.check_version("1.2.2") is False

    def test_check_version_gte(self):
        """Test version check with >= constraint"""
        dep = PluginDependency(name="plugin", version_constraint=">=1.2.0")

        assert dep.check_version("1.2.0") is True
        assert dep.check_version("1.2.1") is True
        assert dep.check_version("2.0.0") is True
        assert dep.check_version("1.1.9") is False

    def test_check_version_lte(self):
        """Test version check with <= constraint"""
        dep = PluginDependency(name="plugin", version_constraint="<=2.0.0")

        assert dep.check_version("2.0.0") is True
        assert dep.check_version("1.9.9") is True
        assert dep.check_version("2.0.1") is False

    def test_check_version_gt(self):
        """Test version check with > constraint"""
        dep = PluginDependency(name="plugin", version_constraint=">1.0.0")

        assert dep.check_version("1.0.1") is True
        assert dep.check_version("2.0.0") is True
        assert dep.check_version("1.0.0") is False

    def test_check_version_lt(self):
        """Test version check with < constraint"""
        dep = PluginDependency(name="plugin", version_constraint="<2.0.0")

        assert dep.check_version("1.9.9") is True
        assert dep.check_version("2.0.0") is False
        assert dep.check_version("2.0.1") is False


class TestDependencyResolver:
    """Test DependencyResolver class"""

    def test_add_plugin(self):
        """Test adding plugin to resolver"""
        resolver = DependencyResolver()
        resolver.add_plugin("plugin1", "1.0.0", [])

        assert "plugin1" in resolver.plugins
        version, deps = resolver.plugins["plugin1"]
        assert version == "1.0.0"
        assert len(deps) == 0

    def test_add_plugin_with_dependencies(self):
        """Test adding plugin with dependencies"""
        resolver = DependencyResolver()
        resolver.add_plugin("plugin1", "1.0.0", ["plugin2>=1.0.0"])

        version, deps = resolver.plugins["plugin1"]
        assert len(deps) == 1
        assert deps[0].name == "plugin2"
        assert deps[0].version_constraint == ">=1.0.0"

    def test_check_dependencies_satisfied(self):
        """Test checking satisfied dependencies"""
        resolver = DependencyResolver()
        resolver.add_plugin("plugin1", "1.0.0", [])
        resolver.add_plugin("plugin2", "1.5.0", ["plugin1"])

        satisfied, missing = resolver.check_dependencies("plugin2")
        assert satisfied is True
        assert len(missing) == 0

    def test_check_dependencies_missing(self):
        """Test checking missing dependencies"""
        resolver = DependencyResolver()
        resolver.add_plugin("plugin1", "1.0.0", ["plugin2"])

        satisfied, missing = resolver.check_dependencies("plugin1")
        assert satisfied is False
        assert len(missing) == 1
        assert "plugin2" in missing[0]

    def test_check_dependencies_version_mismatch(self):
        """Test checking dependencies with version mismatch"""
        resolver = DependencyResolver()
        resolver.add_plugin("plugin1", "1.0.0", [])
        resolver.add_plugin("plugin2", "1.0.0", ["plugin1>=2.0.0"])

        satisfied, missing = resolver.check_dependencies("plugin2")
        assert satisfied is False
        assert len(missing) == 1
        assert "plugin1" in missing[0]

    def test_check_dependencies_plugin_not_found(self):
        """Test checking dependencies for non-existent plugin"""
        resolver = DependencyResolver()

        satisfied, missing = resolver.check_dependencies("nonexistent")
        assert satisfied is False
        assert len(missing) == 1

    def test_resolve_load_order_simple(self):
        """Test resolving load order for simple case"""
        resolver = DependencyResolver()
        resolver.add_plugin("plugin1", "1.0.0", [])
        resolver.add_plugin("plugin2", "1.0.0", ["plugin1"])
        resolver.add_plugin("plugin3", "1.0.0", ["plugin2"])

        success, load_order, errors = resolver.resolve_load_order()
        assert success is True
        assert len(errors) == 0
        assert load_order.index("plugin1") < load_order.index("plugin2")
        assert load_order.index("plugin2") < load_order.index("plugin3")

    def test_resolve_load_order_complex(self):
        """Test resolving load order for complex dependencies"""
        resolver = DependencyResolver()
        resolver.add_plugin("plugin1", "1.0.0", [])
        resolver.add_plugin("plugin2", "1.0.0", [])
        resolver.add_plugin("plugin3", "1.0.0", ["plugin1", "plugin2"])
        resolver.add_plugin("plugin4", "1.0.0", ["plugin3"])

        success, load_order, errors = resolver.resolve_load_order()
        assert success is True
        assert len(errors) == 0
        assert load_order.index("plugin1") < load_order.index("plugin3")
        assert load_order.index("plugin2") < load_order.index("plugin3")
        assert load_order.index("plugin3") < load_order.index("plugin4")

    def test_resolve_load_order_circular(self):
        """Test resolving load order with circular dependencies"""
        resolver = DependencyResolver()
        resolver.add_plugin("plugin1", "1.0.0", ["plugin2"])
        resolver.add_plugin("plugin2", "1.0.0", ["plugin1"])

        success, load_order, errors = resolver.resolve_load_order()
        assert success is False
        assert len(errors) > 0
        assert "Circular dependency" in errors[0]

    def test_get_dependency_tree(self):
        """Test getting dependency tree"""
        resolver = DependencyResolver()
        resolver.add_plugin("plugin1", "1.0.0", [])
        resolver.add_plugin("plugin2", "1.0.0", ["plugin1"])
        resolver.add_plugin("plugin3", "1.0.0", ["plugin2"])

        tree = resolver.get_dependency_tree("plugin3")
        assert "plugin3" in tree
        assert "plugin2" in tree
        assert "plugin1" in tree
        assert tree["plugin3"] == ["plugin2"]
        assert tree["plugin2"] == ["plugin1"]
        assert tree["plugin1"] == []

    def test_get_dependency_tree_nonexistent(self):
        """Test getting dependency tree for non-existent plugin"""
        resolver = DependencyResolver()

        tree = resolver.get_dependency_tree("nonexistent")
        assert tree == {}

    def test_get_dependency_tree_with_missing_deps(self):
        """Test getting dependency tree with missing dependencies"""
        resolver = DependencyResolver()
        resolver.add_plugin("plugin1", "1.0.0", ["nonexistent"])

        tree = resolver.get_dependency_tree("plugin1")
        assert "plugin1" in tree
        assert tree["plugin1"] == ["nonexistent"]
        # nonexistent plugin should not be in tree
        assert "nonexistent" not in tree
