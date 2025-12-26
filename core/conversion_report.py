"""
Conversion report system for tracking warnings and lossy conversions.

This module provides a centralized way to track conversion warnings,
lossy transformations, and generate human-readable reports for users.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any
from enum import Enum


class WarningLevel(Enum):
    """Severity levels for conversion warnings."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class ConversionWarning:
    """Individual conversion warning or notice."""
    level: WarningLevel
    category: str
    message: str
    details: Dict[str, Any] = field(default_factory=dict)


class ConversionReport:
    """
    Track and report on conversion warnings and changes.

    Used to collect warnings during conversion (e.g., lossy transformations,
    unsupported features) and generate a summary report for users.
    """

    def __init__(self):
        """Initialize empty conversion report."""
        self.warnings: List[ConversionWarning] = []
        self._lossy_conversions: List[Dict[str, str]] = []
        self._pattern_transformations: List[Dict[str, str]] = []

    def add_warning(self, category: str, message: str, level: WarningLevel = WarningLevel.WARNING):
        """
        Add a general warning to the report.

        Args:
            category: Warning category (e.g., "pattern_conversion", "unsupported_feature")
            message: Human-readable warning message
            level: Severity level (info, warning, error)
        """
        warning = ConversionWarning(
            level=level,
            category=category,
            message=message
        )
        self.warnings.append(warning)

    def add_lossy_conversion(self, rule: str, from_category: str, to_category: str,
                            reason: str = ""):
        """
        Track a lossy conversion (e.g., Claude deny → VS Code false).

        Args:
            rule: The permission rule being converted
            from_category: Original category (e.g., "deny")
            to_category: Converted category (e.g., "ask")
            reason: Explanation of why the conversion is lossy
        """
        lossy_info = {
            "rule": rule,
            "from": from_category,
            "to": to_category,
            "reason": reason
        }
        self._lossy_conversions.append(lossy_info)

        # Also add as warning
        message = f"Lossy conversion: '{rule}' from '{from_category}' to '{to_category}'"
        if reason:
            message += f" ({reason})"

        self.add_warning("lossy_conversion", message, WarningLevel.WARNING)

    def add_pattern_transformation(self, original: str, transformed: str,
                                  transformation_type: str = ""):
        """
        Track a pattern transformation (e.g., regex preservation, glob conversion).

        Args:
            original: Original pattern
            transformed: Transformed pattern
            transformation_type: Type of transformation (e.g., "regex_preserved", "glob_simplified")
        """
        transform_info = {
            "original": original,
            "transformed": transformed,
            "type": transformation_type
        }
        self._pattern_transformations.append(transform_info)

        # Add as info-level warning
        message = f"Pattern '{original}' → '{transformed}'"
        if transformation_type:
            message += f" ({transformation_type})"

        self.add_warning("pattern_transformation", message, WarningLevel.INFO)

    def has_warnings(self) -> bool:
        """Check if any warnings were recorded."""
        return len(self.warnings) > 0

    def has_errors(self) -> bool:
        """Check if any errors occurred (for --strict mode)."""
        return any(w.level == WarningLevel.ERROR for w in self.warnings)

    def get_warning_count(self, level: WarningLevel = None) -> int:
        """
        Get count of warnings, optionally filtered by level.

        Args:
            level: Optional level filter (returns all if None)

        Returns:
            Count of matching warnings
        """
        if level is None:
            return len(self.warnings)
        return sum(1 for w in self.warnings if w.level == level)

    def get_lossy_conversions(self) -> List[Dict[str, str]]:
        """Get list of all lossy conversions."""
        return self._lossy_conversions.copy()

    def generate_report(self, verbose: bool = False) -> str:
        """
        Generate human-readable summary report.

        Args:
            verbose: Include all info-level warnings (default: only warnings and errors)

        Returns:
            Formatted report string
        """
        if not self.has_warnings():
            return "Conversion completed successfully with no warnings."

        lines = []
        lines.append("=" * 70)
        lines.append("CONVERSION REPORT")
        lines.append("=" * 70)

        # Summary
        error_count = self.get_warning_count(WarningLevel.ERROR)
        warning_count = self.get_warning_count(WarningLevel.WARNING)
        info_count = self.get_warning_count(WarningLevel.INFO)

        lines.append("")
        lines.append(f"Summary: {error_count} errors, {warning_count} warnings, {info_count} info")
        lines.append("")

        # Errors (always show)
        if error_count > 0:
            lines.append("ERRORS:")
            lines.append("-" * 70)
            for warning in self.warnings:
                if warning.level == WarningLevel.ERROR:
                    lines.append(f"  [{warning.category}] {warning.message}")
            lines.append("")

        # Warnings (always show)
        if warning_count > 0:
            lines.append("WARNINGS:")
            lines.append("-" * 70)
            for warning in self.warnings:
                if warning.level == WarningLevel.WARNING:
                    lines.append(f"  [{warning.category}] {warning.message}")
            lines.append("")

        # Info (only in verbose mode)
        if verbose and info_count > 0:
            lines.append("INFO:")
            lines.append("-" * 70)
            for warning in self.warnings:
                if warning.level == WarningLevel.INFO:
                    lines.append(f"  [{warning.category}] {warning.message}")
            lines.append("")

        # Lossy conversions section (if any)
        if self._lossy_conversions:
            lines.append("LOSSY CONVERSIONS:")
            lines.append("-" * 70)
            for lossy in self._lossy_conversions:
                lines.append(f"  Rule: {lossy['rule']}")
                lines.append(f"    {lossy['from']} → {lossy['to']}")
                if lossy.get('reason'):
                    lines.append(f"    Reason: {lossy['reason']}")
                lines.append("")

        lines.append("=" * 70)

        return "\n".join(lines)

    def print_report(self, verbose: bool = False):
        """
        Print the conversion report to stdout.

        Args:
            verbose: Include all info-level warnings
        """
        print(self.generate_report(verbose=verbose))

    def clear(self):
        """Clear all warnings and reset the report."""
        self.warnings.clear()
        self._lossy_conversions.clear()
        self._pattern_transformations.clear()
