"""
Format handlers for different data file types.

This module provides an extensible system for handling different data formats
when generating data loading code.
"""

from abc import ABC, abstractmethod
from pathlib import Path


class DataFormatHandler(ABC):
    """Abstract base class for data format handlers."""

    @abstractmethod
    def detect(self, file_path: Path) -> bool:
        """
        Check if the file matches this format.

        Args:
            file_path: Path to the file to check

        Returns:
            True if this handler can process the file
        """
        pass

    @abstractmethod
    def get_loading_code(self, dataset_name: str, file_path: str) -> str:
        """
        Generate R code to load this dataset.

        Args:
            dataset_name: Name of the dataset variable in R
            file_path: Path to the data file

        Returns:
            R code as a string
        """
        pass

    @abstractmethod
    def get_required_packages(self) -> list[str]:
        """
        Get list of R packages required for this format.

        Returns:
            List of package names (empty list if base R)
        """
        pass

    @property
    @abstractmethod
    def format_name(self) -> str:
        """Return the format name (e.g., 'Rds', 'csv')."""
        pass


class RdsFormatHandler(DataFormatHandler):
    """Handler for RDS (R Data Serialization) format."""

    def detect(self, file_path: Path) -> bool:
        """Check if file has .Rds or .rds extension."""
        return file_path.suffix.lower() == '.rds'

    def get_loading_code(self, dataset_name: str, file_path: str) -> str:
        """Generate readRDS() code."""
        return f'{dataset_name} <- readRDS("{file_path}")'

    def get_required_packages(self) -> list[str]:
        """No additional packages needed (base R)."""
        return []

    @property
    def format_name(self) -> str:
        return "Rds"


class CsvFormatHandler(DataFormatHandler):
    """Handler for CSV format."""

    def detect(self, file_path: Path) -> bool:
        """Check if file has .csv extension."""
        return file_path.suffix.lower() == '.csv'

    def get_loading_code(self, dataset_name: str, file_path: str) -> str:
        """Generate read.csv() code with stringsAsFactors = FALSE."""
        return f'{dataset_name} <- read.csv("{file_path}", stringsAsFactors = FALSE)'

    def get_required_packages(self) -> list[str]:
        """No additional packages needed (base R)."""
        return []

    @property
    def format_name(self) -> str:
        return "csv"


class FormatHandlerRegistry:
    """Registry for managing format handlers."""

    def __init__(self):
        self._handlers: list[DataFormatHandler] = []
        self._register_default_handlers()

    def _register_default_handlers(self):
        """Register default format handlers."""
        self.register(RdsFormatHandler())
        self.register(CsvFormatHandler())
        # Future formats can be added here:
        # self.register(ParquetFormatHandler())
        # self.register(SasFormatHandler())

    def register(self, handler: DataFormatHandler):
        """Register a new format handler."""
        self._handlers.append(handler)

    def get_handler(self, file_path: Path) -> DataFormatHandler | None:
        """
        Get the appropriate handler for a file.

        Args:
            file_path: Path to the file

        Returns:
            Handler instance or None if no handler found
        """
        for handler in self._handlers:
            if handler.detect(file_path):
                return handler
        return None

    def get_handler_by_format_name(self, format_name: str) -> DataFormatHandler | None:
        """
        Get handler by format name.

        Args:
            format_name: Format name (e.g., "Rds", "csv")

        Returns:
            Handler instance or None if not found
        """
        format_lower = format_name.lower()
        for handler in self._handlers:
            if handler.format_name.lower() == format_lower:
                return handler
        return None

    def get_supported_formats(self) -> list[str]:
        """Get list of supported format names."""
        return [handler.format_name for handler in self._handlers]


# Global registry instance
_registry = FormatHandlerRegistry()


def get_format_handler(file_path: Path) -> DataFormatHandler | None:
    """
    Get handler for a file path.

    Args:
        file_path: Path to the file

    Returns:
        Handler instance or None if no handler found
    """
    return _registry.get_handler(file_path)


def get_format_handler_by_name(format_name: str) -> DataFormatHandler | None:
    """
    Get handler by format name.

    Args:
        format_name: Format name (case-insensitive)

    Returns:
        Handler instance or None if not found
    """
    return _registry.get_handler_by_format_name(format_name)


def get_supported_formats() -> list[str]:
    """Get list of supported format names."""
    return _registry.get_supported_formats()
