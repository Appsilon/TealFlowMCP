"""
Get module details tool implementation.
"""

import json

from ..core.enums import ResponseFormat
from ..data import _get_clinical_module_requirements, _get_clinical_modules, _get_general_modules
from ..models import GetModuleDetailsInput
from ..utils import _get_r_help, _truncate_response, _validate_module_exists


async def tealflow_get_module_details(params: GetModuleDetailsInput) -> str:
    """
    Get detailed information about a specific Teal module.

    Validates module existence, retrieves module metadata and parameter information
    from JSON files, fetches R help documentation, and formats output.
    Includes fuzzy matching for typo suggestions.
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

        # Get R help documentation
        r_help = None
        r_package = f"teal.modules.{package}"
        try:
            r_help = _get_r_help(params.module_name, package=r_package)
        except (ValueError, FileNotFoundError) as e:
            # If help is not available, continue without it
            r_help = f"R help not available: {e}"

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
                    for param_name, default_value in list(opt_params.items())[
                        :10
                    ]:  # Limit to first 10
                        lines.append(f"### `{param_name}`")
                        lines.append(f"- **Default**: `{default_value}`")
                        lines.append("")

                    if len(opt_params) > 10:
                        lines.append(f"... and {len(opt_params) - 10} more optional parameters")
                        lines.append("")

            # Add R help documentation
            if r_help:
                lines.append("## R Help Documentation")
                lines.append("")
                lines.append("```")
                lines.append(r_help)
                lines.append("```")
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
                    "r_help": r_help,
                },
                indent=2,
            )

        return _truncate_response(response)

    except Exception as e:
        return f"Error getting module details: {e!s}"
