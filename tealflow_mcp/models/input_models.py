"""
Pydantic models for input validation in Teal Flow MCP Server.
"""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from ..core.enums import PackageFilter, ResponseFormat


class ListModulesInput(BaseModel):
    """Input model for listing Teal modules."""

    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True)

    package: PackageFilter = Field(
        default=PackageFilter.ALL, description="Filter by package: 'clinical', 'general', or 'all'"
    )
    category: str | None = Field(
        default=None, description="Filter by category (e.g., 'graphics', 'tables', 'analysis')"
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' for human-readable or 'json' for machine-readable",
    )


class GetModuleDetailsInput(BaseModel):
    """Input model for getting module details."""

    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True)

    module_name: str = Field(
        ...,
        description="Name of the module (e.g., 'tm_g_km', 'tm_t_coxreg', 'tm_g_scatterplot')",
        min_length=3,
        max_length=100,
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' for human-readable or 'json' for machine-readable",
    )

    @field_validator("module_name")
    @classmethod
    def validate_module_name(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Module name cannot be empty")
        return v.strip()


class SearchModulesInput(BaseModel):
    """Input model for searching modules by analysis type."""

    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True)

    analysis_type: str = Field(
        ...,
        description=(
            "Type of analysis (e.g., 'survival', 'kaplan-meier', 'forest plot', 'cox regression', 'scatter plot')"
        ),
        min_length=2,
        max_length=200,
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' for human-readable or 'json' for machine-readable",
    )

    @field_validator("analysis_type")
    @classmethod
    def validate_analysis_type(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Analysis type cannot be empty")
        return v.strip().lower()


class CheckDatasetRequirementsInput(BaseModel):
    """Input model for checking dataset requirements."""

    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True)

    module_name: str = Field(..., description="Name of the module to check", min_length=3, max_length=100)
    available_datasets: list[str] | None = Field(
        default=None,
        description="List of available datasets (defaults to Flow's standard: ADSL, ADTTE, ADRS, ADQS, ADAE)",
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' for human-readable or 'json' for machine-readable",
    )


class ListDatasetsInput(BaseModel):
    """Input model for listing datasets."""

    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True)

    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' for human-readable or 'json' for machine-readable",
    )


class GenerateModuleCodeInput(BaseModel):
    """Input model for generating module code."""

    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True)

    module_name: str = Field(..., description="Name of the module to generate code for", min_length=3, max_length=100)
    parameters: dict[str, Any] | None = Field(default=None, description="Optional parameter overrides as JSON object")
    include_comments: bool = Field(
        default=True, description="Whether to include explanatory comments in the generated code"
    )


class GetAppTemplateInput(BaseModel):
    """Input model for getting app template."""

    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True)

    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' for human-readable or 'json' for machine-readable",
    )


class DiscoverDatasetsInput(BaseModel):
    """Input model for discovering datasets."""

    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True)

    data_directory: str = Field(
        default="data/",
        description="Path to the directory containing dataset files",
    )
    file_formats: list[str] | None = Field(
        default=None,
        description="List of file formats to include (e.g., ['Rds', 'csv']). If None, all supported formats are included.",
    )
    pattern: str = Field(
        default="AD*",
        description="File pattern to match (default: 'AD*' for ADaM datasets)",
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' for human-readable or 'json' for machine-readable",
    )


class CheckShinyStartupInput(BaseModel):
    """Input model for checking Shiny app startup."""

    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True)

    app_path: str = Field(
        default=".",
        description="Path to the Shiny app directory",
    )
    app_filename: str = Field(
        default="app.R",
        description="Name of the app file (e.g., 'app.R', 'server.R')",
    )
    timeout_seconds: int = Field(
        default=15,
        description="Maximum time in seconds to allow the app to start",
        ge=1,
        le=120,
    )

    @field_validator("app_path")
    @classmethod
    def validate_app_path(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("App path cannot be empty")
        return v.strip()

    @field_validator("app_filename")
    @classmethod
    def validate_app_filename(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("App filename cannot be empty")
        if not v.endswith(".R"):
            raise ValueError("App filename must end with .R")
        return v.strip()
