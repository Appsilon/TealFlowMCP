"""
Code generation tool implementation.
"""

from ..data import _get_clinical_module_requirements, _get_clinical_modules, _get_general_modules
from ..models import GenerateModuleCodeInput
from ..utils import _validate_module_exists


def _generate_general_module_code(params: GenerateModuleCodeInput, module_info: dict, basic_info: dict) -> str:
    """
    Generate R code for general modules using data_extract_spec patterns.

    General modules use data_extract_spec() which provides flexible data selection
    and filtering capabilities. This function generates the full structure with
    TODO comments for dataset-specific configuration.
    """
    lines = []

    if params.include_comments:
        lines.append(f"# {basic_info.get('description', params.module_name)}")
        lines.append("# General module - works with any data.frame")
        lines.append("# Configure data_extract_spec for your specific datasets")
        lines.append("")

    lines.append(f"{params.module_name}(")

    func_params = module_info.get("function_parameters", {}) or module_info
    req_params = func_params.get("required_parameters", {})
    opt_params = func_params.get("optional_parameters", {})

    param_lines = []

    # Process required parameters
    if req_params:
        for param_name, param_info in req_params.items():
            if param_name == "label":
                # Simple string parameter
                param_lines.append(f'  label = "{basic_info.get("description", params.module_name)}",')

            elif "data_extract_spec" in str(param_info.get("type", "")):
                # Generate data_extract_spec structure
                if params.include_comments:
                    param_lines.append(f"  # {param_info.get('description', '')}")

                param_lines.append(f"  {param_name} = data_extract_spec(")
                param_lines.append('    dataname = "ADSL",  # TODO: Specify your dataset name')
                param_lines.append("    select = select_spec(")
                param_lines.append('      label = "Select variable:",')
                param_lines.append('      choices = variable_choices("ADSL"),  # TODO: Specify available columns')
                param_lines.append("      selected = NULL,  # TODO: Set default selection")
                param_lines.append("      multiple = FALSE,  # Set TRUE to allow multiple selections")
                param_lines.append("      fixed = FALSE  # Set TRUE to prevent user changes")
                param_lines.append("    )")

                if params.include_comments:
                    param_lines.append("    # Optional: Add filter_spec to subset data before selection")
                    param_lines.append("    # filter = filter_spec(")
                    param_lines.append('    #   label = "Filter data:",')
                    param_lines.append('    #   vars = c("ARM", "SEX"),  # Variables to filter on')
                    param_lines.append('    #   choices = value_choices("ADSL", "ARM"),  # Available values')
                    param_lines.append("    #   selected = NULL,  # Default filter values")
                    param_lines.append("    #   multiple = TRUE  # Allow multiple selections")
                    param_lines.append("    # )")

                param_lines.append("  ),")
            else:
                # Other parameter types
                if params.include_comments:
                    param_lines.append(f"  # {param_info.get('description', '')}")
                default = opt_params.get(param_name, {}).get("default", "NULL")
                param_lines.append(f"  {param_name} = {default},  # TODO: Configure this parameter")

    # Remove trailing comma from last parameter
    if param_lines and param_lines[-1].endswith(","):
        param_lines[-1] = param_lines[-1][:-1]

    lines.extend(param_lines)
    lines.append(")")

    # Add helpful examples
    if params.include_comments:
        lines.append("")
        lines.append("# Example with actual configuration for ADSL dataset:")
        lines.append("# x = data_extract_spec(")
        lines.append('#   dataname = "ADSL",')
        lines.append("#   select = select_spec(")
        lines.append('#     label = "Select X variable:",')
        lines.append('#     choices = variable_choices(ADSL, c("AGE", "BMRKR1", "BMRKR2")),')
        lines.append('#     selected = "AGE",')
        lines.append("#     multiple = FALSE,")
        lines.append("#     fixed = FALSE")
        lines.append("#   )")
        lines.append("# )")
        lines.append("")
        lines.append("# For long datasets with filtering:")
        lines.append("# y = data_extract_spec(")
        lines.append('#   dataname = "ADLB",')
        lines.append("#   filter = filter_spec(")
        lines.append('#     vars = "PARAMCD",')
        lines.append('#     choices = value_choices(ADLB, "PARAMCD", "PARAM"),')
        lines.append('#     selected = "ALT",')
        lines.append("#     multiple = FALSE")
        lines.append("#   ),")
        lines.append("#   select = select_spec(")
        lines.append('#     choices = "AVAL",')
        lines.append('#     selected = "AVAL",')
        lines.append("#     fixed = TRUE")
        lines.append("#   )")
        lines.append("# )")
        lines.append("")
        lines.append("# Use tealflow_get_module_details for complete parameter documentation")

    return "\n".join(lines)


async def tealflow_generate_module_code(params: GenerateModuleCodeInput) -> str:
    """
    Generate R code for adding a module to a Teal application.

    This tool generates ready-to-use R code for adding a Teal module to your app.
    It includes all required parameters with sensible defaults based on the module's
    specifications and Flow's available datasets.

    Args:
        params (GenerateModuleCodeInput): Validated input parameters containing:
            - module_name (str): Name of the module to generate code for
            - parameters (Optional[Dict]): Parameter overrides (not yet implemented)
            - include_comments (bool): Include explanatory comments (default: True)

    Returns:
        str: Complete R code snippet ready to paste into a Teal app

        Includes:
        - Module function call with proper syntax
        - All required parameters
        - Common optional parameters with defaults
        - Explanatory comments (if requested)
        - Usage instructions

    Examples:
        - Generate KM plot code: params with module_name="tm_g_km"
        - Generate Cox regression code: params with module_name="tm_t_coxreg"
        - Generate without comments: params with include_comments=False

    Note:
        Generated code uses Flow's standard dataset configuration.
        You may need to adjust parameters for your specific use case.
    """
    try:
        # Validate module exists
        exists, package, suggestion = _validate_module_exists(params.module_name)

        if not exists:
            msg = f"Error: Module '{params.module_name}' not found."
            if suggestion:
                msg += f" Did you mean '{suggestion}'?"
            return msg

        # Get module requirements
        if package == "clinical":
            requirements_data = _get_clinical_module_requirements()
            modules = requirements_data.get("modules", {})
            module_info = modules.get(params.module_name, {})
            clinical_data = _get_clinical_modules()
            basic_info = clinical_data.get("modules", {}).get(params.module_name, {})
        else:  # general
            general_data = _get_general_modules()
            modules = general_data.get("modules", {})
            module_info = modules.get(params.module_name, {})
            basic_info = module_info
            # For general modules, use specialized generation
            return _generate_general_module_code(params, module_info, basic_info)

        # Generate code for clinical modules
        lines = []

        if params.include_comments:
            lines.append(f"# {basic_info.get('description', params.module_name)}")
            lines.append(f"# Required datasets: {', '.join(basic_info.get('required_datasets', []))}")
            lines.append("")

        # Start module call
        lines.append(f"{params.module_name}(")

        # Add required parameters
        func_params = module_info.get("function_parameters", {})
        req_params = func_params.get("required_params", {})

        param_lines = []

        # Track the actual dataset name for use in paramcd
        datasets = basic_info.get("required_datasets", [])
        actual_dataname = datasets[1] if len(datasets) > 1 else datasets[0] if datasets else "ADSL"
        parent_dataname = datasets[0] if datasets else "ADSL"  # Usually ADSL

        # Check if this is a patient profile module (only label required, special handling)
        is_patient_profile = params.module_name.startswith("tm_g_pp_") or params.module_name.startswith("tm_t_pp_")

        if is_patient_profile and len(req_params) == 1 and "label" in req_params:
            # Patient profile modules need dataname and parentname explicitly
            param_lines.append(f'  label = "{basic_info.get("description", params.module_name)}",')
            param_lines.append(f'  dataname = "{actual_dataname}",')
            if len(datasets) > 1:
                param_lines.append(f'  parentname = "{parent_dataname}",')
            # Don't process other params for patient profiles with minimal required params
            req_params = {}  # Clear to skip loop

        if req_params:
            for param_name, param_info in req_params.items():
                if params.include_comments:
                    param_lines.append(f"  # {param_info.get('description', '')}")

                # Generate sensible defaults based on common patterns
                if param_name == "label":
                    param_lines.append(f'  label = "{basic_info.get("description", params.module_name)}",')
                elif param_name == "dataname":
                    # Get first required dataset
                    datasets = basic_info.get("required_datasets", [])
                    actual_dataname = datasets[1] if len(datasets) > 1 else datasets[0] if datasets else "ADSL"
                    param_lines.append(f'  dataname = "{actual_dataname}",')
                elif "arm_var" in param_name:
                    param_lines.append(
                        '  arm_var = choices_selected(variable_choices(ADSL, subset = arm_vars), selected = "ARM"),'
                    )
                elif param_name == "paramcd":
                    # Use the actual dataset variable, not the string "dataname"
                    param_lines.append(
                        f"  paramcd = choices_selected(value_choices({actual_dataname}, "
                        f'"PARAMCD", "PARAM"), selected = NULL),'
                    )
                elif param_name == "strata_var":
                    param_lines.append(
                        "  strata_var = choices_selected(variable_choices(ADSL, "
                        'subset = strata_vars), selected = "STRATA1"),'
                    )
                elif param_name == "facet_var":
                    param_lines.append(
                        "  facet_var = choices_selected(variable_choices(ADSL, subset = facet_vars), selected = NULL),"
                    )
                elif "subgroup_var" in param_name:
                    # Limit to categorical variables (facet_vars) to avoid character type errors
                    param_lines.append(
                        "  subgroup_var = choices_selected(variable_choices(ADSL, "
                        "subset = facet_vars), selected = NULL),"
                    )
                elif param_name == "time_points":
                    # Common time points for survival analysis (days)
                    param_lines.append("  time_points = choices_selected(c(182, 365, 547), 182),")
                elif param_name == "hlt":
                    # High Level Term variable selection for adverse events (MedDRA hierarchy)
                    param_lines.append(
                        f"  hlt = choices_selected(variable_choices({actual_dataname}, "
                        f'c("AEBODSYS", "AEHLT")), selected = "AEBODSYS"),'
                    )
                elif param_name == "llt":
                    # Low Level Term variable selection for adverse events
                    param_lines.append(
                        f"  llt = choices_selected(variable_choices({actual_dataname}, "
                        f'c("AEDECOD", "AELLT")), selected = "AEDECOD"),'
                    )
                elif param_name == "grade":
                    # Grade/severity variable for AE
                    param_lines.append(
                        f"  grade = choices_selected(variable_choices({actual_dataname}, "
                        f'"AETOXGR"), selected = "AETOXGR"),'
                    )
                else:
                    # Generic placeholder
                    param_lines.append(f"  {param_name} = # TODO: Configure {param_name},")

        # Add some common optional parameters
        if params.include_comments:
            param_lines.append("  # Optional parameters - adjust as needed")

        # Remove trailing comma from last parameter
        if param_lines and param_lines[-1].endswith(","):
            param_lines[-1] = param_lines[-1][:-1]

        lines.extend(param_lines)
        lines.append(")")

        if params.include_comments:
            lines.append("")
            lines.append("# Note: Adjust parameters based on your specific requirements")
            lines.append("# Use tealflow_get_module_details for complete parameter documentation")

        return "\n".join(lines)

    except Exception as e:
        return f"Error generating code: {e!s}"
