"""
List modules tool implementation.
"""

from ..core.enums import PackageFilter, ResponseFormat
from ..data import _get_clinical_modules, _get_general_modules
from ..models import ListModulesInput
from ..utils import _format_module_list_json, _format_module_list_markdown, _truncate_response


async def tealflow_list_modules(params: ListModulesInput) -> str:
    """
    List all available Teal modules with their descriptions and dataset requirements.

    This tool helps discover what analysis modules are available in the Teal framework.
    Modules can be filtered by package (clinical vs general) and optionally by category.

    Clinical modules are designed for clinical trial reporting and work with ADaM datasets.
    General modules are for general-purpose data exploration and work with any data.frame.

    Args:
        params (ListModulesInput): Validated input parameters containing:
            - package (PackageFilter): 'clinical', 'general', or 'all' (default: 'all')
            - category (Optional[str]): Filter by category like 'graphics', 'tables', 'analysis'
            - response_format (ResponseFormat): 'markdown' or 'json' (default: 'markdown')

    Returns:
        str: List of modules with names, descriptions, and required datasets

        Markdown format:
            # Teal Modules (Package Name)

            ## module_name
            **Description**: Module description
            **Required Datasets**: ADSL, ADTTE (or "None")

        JSON format:
            {
                "modules": [
                    {
                        "name": "tm_g_km",
                        "description": "Kaplan-Meier Plot",
                        "required_datasets": ["ADSL", "ADTTE"]
                    }
                ],
                "count": 10
            }

    Examples:
        - List all clinical modules: params with package="clinical"
        - List graphics modules: params with category="graphics"
        - Get machine-readable list: params with response_format="json"
    """
    try:
        modules_to_show = {}

        # Load modules based on package filter
        if params.package in [PackageFilter.ALL, PackageFilter.CLINICAL]:
            clinical_data = _get_clinical_modules()
            modules_to_show.update(clinical_data.get("modules", {}))

        if params.package in [PackageFilter.ALL, PackageFilter.GENERAL]:
            general_data = _get_general_modules()
            modules_to_show.update(general_data.get("modules", {}))

        # Filter by category if specified
        if params.category:
            category_lower = params.category.lower()
            modules_to_show = {
                name: info
                for name, info in modules_to_show.items()
                if category_lower in info.get("description", "").lower() or category_lower in name.lower()
            }

        if not modules_to_show:
            return f"No modules found matching filters (package={params.package}, category={params.category})"

        # Format response
        if params.response_format == ResponseFormat.MARKDOWN:
            response = _format_module_list_markdown(modules_to_show, params.package.value)
        else:
            response = _format_module_list_json(modules_to_show)

        return _truncate_response(response)

    except Exception as e:
        return f"Error listing modules: {e!s}"
