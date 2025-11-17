"""
MCP Safety Policy

Defines safety policies and execution modes for MCP operations.
Ensures safe interaction between LLM and software APIs.
"""

from enum import Enum
from typing import Any, List, Optional, Type, Dict
from dataclasses import dataclass


class ExecutionMode(Enum):
    """
    MCP execution mode.

    Modes:
        PLAN: Read-only mode for planning, no writes allowed
        EXECUTE: Full execution mode, requires confirmations for writes
        UNSAFE: Unrestricted mode (use with caution, testing only)
    """
    PLAN = "plan"
    EXECUTE = "execute"
    UNSAFE = "unsafe"


class SafetyLevel(Enum):
    """
    Safety level for MCP operations.

    Levels:
        READ_ONLY: Safe read operations, no side effects
        WRITE_SAFE: Write operations that require confirmation
        RESTRICTED_WRITE: Write operations with additional validation
        TRANSACTIONAL: Operations that support rollback
        CACHED: Read operations with caching for performance
    """
    READ_ONLY = "read_only"
    WRITE_SAFE = "write_safe"
    RESTRICTED_WRITE = "restricted_write"
    TRANSACTIONAL = "transactional"
    CACHED = "cached"


@dataclass
class OperationPolicy:
    """
    Policy for a specific MCP operation.

    Attributes:
        name: Operation name
        safety_level: Safety level (read_only, write_safe, etc.)
        requires_confirmation: Whether user confirmation is needed
        allowed_modes: Execution modes where operation is allowed
        type_validation: Whether to validate object types
        allowed_types: List of allowed object types (for validation)
        rollback_supported: Whether operation can be rolled back
        cache_ttl: Cache time-to-live in seconds (for cached operations)
    """
    name: str
    safety_level: SafetyLevel
    requires_confirmation: bool = False
    allowed_modes: List[ExecutionMode] = None
    type_validation: bool = False
    allowed_types: List[str] = None
    rollback_supported: bool = False
    cache_ttl: Optional[int] = None

    def __post_init__(self):
        """Set defaults based on safety level"""
        if self.allowed_modes is None:
            # Default: allow in all modes except read-only operations in PLAN mode
            if self.safety_level == SafetyLevel.READ_ONLY:
                self.allowed_modes = [ExecutionMode.PLAN, ExecutionMode.EXECUTE, ExecutionMode.UNSAFE]
            else:
                # Write operations not allowed in PLAN mode
                self.allowed_modes = [ExecutionMode.EXECUTE, ExecutionMode.UNSAFE]

        # Set default confirmation requirement
        if self.safety_level in [SafetyLevel.WRITE_SAFE, SafetyLevel.RESTRICTED_WRITE]:
            self.requires_confirmation = True

        # Restricted write operations have type validation
        if self.safety_level == SafetyLevel.RESTRICTED_WRITE:
            self.type_validation = True


class SafetyPolicy:
    """
    Safety policy enforcement for MCP operations.

    Validates operations against policies, checks type safety,
    and manages confirmation requirements.

    Example:
        >>> policy = SafetyPolicy()
        >>> policy.register_platform('aimsun', ['GKSection', 'GKNode'])
        >>> is_allowed = policy.validate_operation(
        ...     mode=ExecutionMode.PLAN,
        ...     operation='read_script',
        ...     safety_level=SafetyLevel.READ_ONLY
        ... )
    """

    # Known safe types for different platforms
    PLATFORM_TYPES = {
        'aimsun': [
            'GKSection', 'GKNode', 'GKCentroid', 'GKTurning',
            'GKDetector', 'GKReplication', 'GKExperiment',
            'GKModel', 'GKCatalog', 'GKLayer', 'GKFolder'
        ],
        'qgis': [
            'QgsVectorLayer', 'QgsRasterLayer', 'QgsFeature',
            'QgsGeometry', 'QgsProject', 'QgsLayerTreeLayer',
            'QgsMapCanvas', 'QgsPoint', 'QgsRectangle'
        ],
        'python': [
            'Path', 'str', 'int', 'float', 'dict', 'list',
            'set', 'tuple', 'bool', 'None'
        ]
    }

    def __init__(self):
        """Initialize safety policy"""
        self.policies: Dict[str, OperationPolicy] = {}
        self.current_mode: ExecutionMode = ExecutionMode.EXECUTE
        self.custom_platforms: Dict[str, List[str]] = {}

    def register_platform(self, platform: str, allowed_types: List[str]) -> None:
        """
        Register custom platform with allowed types.

        Args:
            platform: Platform name
            allowed_types: List of allowed type names
        """
        self.custom_platforms[platform] = allowed_types

    def set_mode(self, mode: ExecutionMode) -> None:
        """
        Set current execution mode.

        Args:
            mode: Execution mode to set
        """
        self.current_mode = mode

    def register_operation(self, operation: str, safety_level: SafetyLevel,
                          **kwargs) -> None:
        """
        Register an operation with its policy.

        Args:
            operation: Operation name
            safety_level: Safety level
            **kwargs: Additional policy parameters
        """
        policy = OperationPolicy(
            name=operation,
            safety_level=safety_level,
            **kwargs
        )
        self.policies[operation] = policy

    def get_policy(self, operation: str) -> Optional[OperationPolicy]:
        """
        Get policy for an operation.

        Args:
            operation: Operation name

        Returns:
            OperationPolicy if registered, None otherwise
        """
        return self.policies.get(operation)

    def validate_operation(self, operation: str, mode: ExecutionMode = None,
                          target: Any = None) -> tuple[bool, Optional[str]]:
        """
        Validate if an operation is allowed.

        Args:
            operation: Operation name
            mode: Execution mode (uses current mode if not specified)
            target: Optional target object for type validation

        Returns:
            Tuple of (is_allowed, reason)

        Example:
            >>> policy = SafetyPolicy()
            >>> is_allowed, reason = policy.validate_operation(
            ...     'write_file',
            ...     mode=ExecutionMode.PLAN
            ... )
            >>> print(is_allowed, reason)
            False "Write operations not allowed in PLAN mode"
        """
        if mode is None:
            mode = self.current_mode

        # Get operation policy
        policy = self.get_policy(operation)
        if not policy:
            # No policy registered - allow by default in UNSAFE mode only
            if mode == ExecutionMode.UNSAFE:
                return True, None
            return False, f"Operation '{operation}' has no registered policy"

        # Check if operation is allowed in current mode
        if mode not in policy.allowed_modes:
            return False, f"Operation '{operation}' not allowed in {mode.value} mode"

        # Type validation for restricted operations
        if policy.type_validation and target is not None:
            is_valid, type_error = self.check_type_safety(target, policy.allowed_types)
            if not is_valid:
                return False, type_error

        return True, None

    def check_type_safety(self, obj: Any, allowed_types: Optional[List[str]] = None,
                         platform: Optional[str] = None) -> tuple[bool, Optional[str]]:
        """
        Check if an object is a known safe type.

        Args:
            obj: Object to check
            allowed_types: Specific allowed type names
            platform: Platform to check against (aimsun, qgis, python)

        Returns:
            Tuple of (is_safe, error_message)

        Example:
            >>> policy = SafetyPolicy()
            >>> from pathlib import Path
            >>> is_safe, error = policy.check_type_safety(Path('.'), platform='python')
            >>> print(is_safe)
            True
        """
        obj_type = type(obj).__name__

        # Check against specific allowed types
        if allowed_types:
            if obj_type in allowed_types:
                return True, None
            return False, f"Object type '{obj_type}' not in allowed types: {allowed_types}"

        # Check against platform types
        if platform:
            platform_types = self._get_platform_types(platform)
            if obj_type in platform_types:
                return True, None
            return False, f"Object type '{obj_type}' not a known {platform} type"

        # Check against all known platforms
        for platform_name, types in self.PLATFORM_TYPES.items():
            if obj_type in types:
                return True, None

        # Check custom platforms
        for platform_name, types in self.custom_platforms.items():
            if obj_type in types:
                return True, None

        return False, f"Object type '{obj_type}' is not a recognized safe type"

    def _get_platform_types(self, platform: str) -> List[str]:
        """Get known types for a platform"""
        # Check built-in platforms
        if platform in self.PLATFORM_TYPES:
            return self.PLATFORM_TYPES[platform]

        # Check custom platforms
        if platform in self.custom_platforms:
            return self.custom_platforms[platform]

        return []

    def requires_confirmation(self, operation: str) -> bool:
        """
        Check if an operation requires user confirmation.

        Args:
            operation: Operation name

        Returns:
            True if confirmation required, False otherwise
        """
        policy = self.get_policy(operation)
        if not policy:
            # Default: require confirmation for unknown operations
            return True

        return policy.requires_confirmation

    def supports_rollback(self, operation: str) -> bool:
        """
        Check if an operation supports rollback.

        Args:
            operation: Operation name

        Returns:
            True if rollback supported, False otherwise
        """
        policy = self.get_policy(operation)
        if not policy:
            return False

        return policy.rollback_supported

    def get_cache_ttl(self, operation: str) -> Optional[int]:
        """
        Get cache TTL for an operation.

        Args:
            operation: Operation name

        Returns:
            Cache TTL in seconds, or None if not cached
        """
        policy = self.get_policy(operation)
        if not policy:
            return None

        return policy.cache_ttl

    def list_operations(self, mode: ExecutionMode = None,
                       safety_level: SafetyLevel = None) -> List[str]:
        """
        List operations matching criteria.

        Args:
            mode: Filter by execution mode
            safety_level: Filter by safety level

        Returns:
            List of operation names
        """
        operations = []

        for name, policy in self.policies.items():
            # Filter by mode
            if mode and mode not in policy.allowed_modes:
                continue

            # Filter by safety level
            if safety_level and policy.safety_level != safety_level:
                continue

            operations.append(name)

        return sorted(operations)

    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary of all registered policies.

        Returns:
            Dictionary with policy statistics
        """
        by_safety = {}
        for policy in self.policies.values():
            level = policy.safety_level.value
            if level not in by_safety:
                by_safety[level] = []
            by_safety[level].append(policy.name)

        return {
            'total_operations': len(self.policies),
            'current_mode': self.current_mode.value,
            'by_safety_level': by_safety,
            'platforms': list(self.PLATFORM_TYPES.keys()) + list(self.custom_platforms.keys())
        }


# Global safety policy instance
_global_policy: Optional[SafetyPolicy] = None


def get_safety_policy() -> SafetyPolicy:
    """
    Get or create global safety policy instance.

    Returns:
        Global SafetyPolicy instance
    """
    global _global_policy
    if _global_policy is None:
        _global_policy = SafetyPolicy()
    return _global_policy
