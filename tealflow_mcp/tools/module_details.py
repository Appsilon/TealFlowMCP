"""
Get module details tool implementation.
"""

import json

from ..core.enums import ResponseFormat
from ..data import _get_clinical_module_requirements, _get_clinical_modules, _get_general_modules
from ..models import GetModuleDetailsInput
from ..utils import _truncate_response, _validate_module_exists


async def tealflow_get_module_details(params: GetModuleDetailsInput) -> str:
    """
    Get comprehensive details about a specific Teal module including all parameters.

    This tool provides complete information about a module's required and optional
    parameters, their types, default values, and descriptions. Use this after
    discovering a module to understand how to configure it properly.

    Args:
        params (GetModuleDetailsInput): Validated input parameters containing:
            - module_name (str): Name of the module (e.g., 'tm_g_km', 'tm_t_coxreg')
            - response_format (ResponseFormat): 'markdown' or 'json' (default: 'markdown')

    Returns:
        str: Detailed module information including parameters, datasets, and usage

        Includes:
        - Module description
        - Required datasets
        - Required parameters (no defaults)
        - Optional parameters (with defaults)
        - Parameter types and constraints
        - Usage examples

    Error Handling:
        - Returns error if module not found
        - Suggests similar module names for typos
        - Provides guidance on correct module names

    Examples:
        - Get details for KM plot: params with module_name="tm_g_km"
        - Get Cox regression info: params with module_name="tm_t_coxreg"
        - Get JSON format: params with response_format="json"
    """
    try:
        # Validate module exists
        exists, package, suggestion = _validate_module_exists(params.module_name)

        if not exists:
            msg = f"Error: Module '{params.module_name}' not found."
            if suggestion:
                msg += f" Did you mean '{suggestion}'?"
            msg += "\n\nUse tealflow_list_modules to see all available modules."
            return msg

        # Get module details based on package
        if package == "clinical":
            requirements_data = _get_clinical_module_requirements()
            modules = requirements_data.get("modules", {})
            module_info = modules.get(params.module_name, {})

            # Also get basic info
            clinical_data = _get_clinical_modules()
            basic_info = clinical_data.get("modules", {}).get(params.module_name, {})

        else:  # general
            general_data = _get_general_modules()
            modules = general_data.get("modules", {})
            module_info = modules.get(params.module_name, {})
            basic_info = module_info

        if params.response_format == ResponseFormat.MARKDOWN:
            lines = [f"# {params.module_name}", ""]
            lines.append(f"**Package**: teal.modules.{package}")
            lines.append(f"**Description**: {basic_info.get('description', 'N/A')}")
            lines.append("")

            # Required datasets
            datasets = basic_info.get("required_datasets", [])
            if datasets:
                lines.append(f"**Required Datasets**: {', '.join(datasets)}")
            else:
                lines.append("**Required Datasets**: None (works with any data.frame)")
            lines.append("")

            # Function parameters
            if "function_parameters" in module_info:
                params_info = module_info["function_parameters"]

                # Required parameters
                req_params = params_info.get("required_params", {})
                if req_params:
                    lines.append("## Required Parameters")
                    lines.append("")
                    for param_name, param_info in req_params.items():
                        lines.append(f"### `{param_name}`")
                        lines.append(f"- **Type**: {param_info.get('type', 'N/A')}")
                        lines.append(f"- **Description**: {param_info.get('description', 'N/A')}")
                        lines.append("")

                # Optional parameters (with defaults)
                opt_params = params_info.get("params_with_defaults", {})
                if opt_params:
                    lines.append("## Optional Parameters (with defaults)")
                    lines.append("")
                    for param_name, default_value in list(opt_params.items())[:10]:  # Limit to first 10
                        lines.append(f"### `{param_name}`")
                        lines.append(f"- **Default**: `{default_value}`")
                        lines.append("")

                    if len(opt_params) > 10:
                        lines.append(f"... and {len(opt_params) - 10} more optional parameters")
                        lines.append("")

            response = "\n".join(lines)
        else:
            # JSON format
            response = json.dumps(
                {
                    "module_name": params.module_name,
                    "package": f"teal.modules.{package}",
                    "description": basic_info.get("description", ""),
                    "required_datasets": basic_info.get("required_datasets", []),
                    "parameters": module_info.get("function_parameters", {}),
                },
                indent=2,
            )

        return _truncate_response(response)

    except Exception as e:
        return f"Error getting module details: {e!s}"
