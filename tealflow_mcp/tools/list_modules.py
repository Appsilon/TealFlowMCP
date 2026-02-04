"""
List modules tool implementation.
"""

from ..core.enums import PackageFilter, ResponseFormat
from ..data import _get_clinical_modules, _get_general_modules
from ..models import ListModulesInput
from ..utils import _format_module_list_json, _format_module_list_markdown, _truncate_response


async def tealflow_list_modules(params: ListModulesInput) -> str:
    """
    List available Teal modules with filtering by package and category.

    Loads module data from JSON files and applies user-specified filters.
    Formats output as markdown or JSON based on response_format parameter.
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
                if category_lower in info.get("description", "").lower()
                or category_lower in name.lower()
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
