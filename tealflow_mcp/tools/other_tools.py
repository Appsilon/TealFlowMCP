"""
Additional tool implementations: search, check datasets, list datasets, app template.
"""

import json

from ..core.constants import KNOWLEDGE_BASE_DIR
from ..core.enums import ResponseFormat
from ..data import (
    _get_clinical_by_analysis_type,
    _get_clinical_modules,
    _get_general_by_analysis_type,
    _get_general_modules,
)
from ..models import (
    CheckDatasetRequirementsInput,
    GetAppTemplateInput,
    ListDatasetsInput,
    SearchModulesInput,
)
from ..utils import _truncate_response, _validate_module_exists


async def tealflow_search_modules_by_analysis(params: SearchModulesInput) -> str:
    """
    Search for modules by analysis type using structured categories and text matching.

    First attempts exact/partial category matches from predefined analysis types,
    then falls back to text search across module descriptions. Scores and ranks
    results by relevance.
    """
    try:
        search_term = params.analysis_type.lower()

        # Load structured analysis type mappings
        clinical_by_type = _get_clinical_by_analysis_type()
        general_by_type = _get_general_by_analysis_type()

        # Also load module details for descriptions
        clinical_data = _get_clinical_modules()
        general_data = _get_general_modules()

        all_modules = {}
        all_modules.update(clinical_data.get("modules", {}))
        all_modules.update(general_data.get("modules", {}))

        # Step 1: Check for exact or partial category matches
        category_matches = []
        all_categories = {}

        # Process clinical categories
        for category_name, category_info in clinical_by_type.get("analysis_types", {}).items():
            all_categories[category_name] = {
                "type": "clinical",
                "description": category_info.get("description", ""),
                "modules": category_info.get("modules", []),
            }

        # Process general categories
        for category_name, category_info in general_by_type.get("analysis_types", {}).items():
            all_categories[category_name] = {
                "type": "general",
                "description": category_info.get("description", ""),
                "modules": category_info.get("modules", []),
            }

        # Find matching categories
        for category_name, category_info in all_categories.items():
            category_lower = category_name.lower().replace("_", " ")
            description_lower = category_info["description"].lower()

            # Calculate category match score
            score = 0
            if search_term in category_lower:
                score += 20  # Exact category match is highest priority
            if search_term in description_lower:
                score += 10

            # Check individual words
            search_words = search_term.split()
            for word in search_words:
                if len(word) > 2:
                    if word in category_lower:
                        score += 8
                    if word in description_lower:
                        score += 4

            if score > 0:
                category_matches.append(
                    {
                        "category": category_name,
                        "type": category_info["type"],
                        "description": category_info["description"],
                        "modules": category_info["modules"],
                        "score": score,
                    }
                )

        # Sort categories by relevance
        category_matches.sort(key=lambda x: x["score"], reverse=True)

        # Step 2: If we have category matches, use those (more precise)
        if category_matches:
            # Collect all modules from matching categories
            matched_modules = set()
            for cat_match in category_matches[:3]:  # Top 3 categories
                matched_modules.update(cat_match["modules"])

            # Get details for these modules
            matches = []
            for module_name in matched_modules:
                if module_name in all_modules:
                    module_info = all_modules[module_name]
                    matches.append(
                        {
                            "name": module_name,
                            "description": module_info.get("description", ""),
                            "required_datasets": module_info.get("required_datasets", []),
                            "categories": [
                                cat["category"]
                                for cat in category_matches
                                if module_name in cat["modules"]
                            ],
                        }
                    )

            # Format response with categories
            if params.response_format == ResponseFormat.MARKDOWN:
                lines = [f"# Modules for '{params.analysis_type}' Analysis", ""]

                # Show matching categories first
                lines.append("## Matching Analysis Categories")
                lines.append("")
                for cat_match in category_matches[:3]:
                    lines.append(
                        f"### {cat_match['category'].replace('_', ' ').title()} ({cat_match['type'].title()})"
                    )
                    lines.append(f"{cat_match['description']}")
                    lines.append(f"**Modules**: {', '.join(cat_match['modules'][:5])}")
                    if len(cat_match["modules"]) > 5:
                        lines.append(f"... and {len(cat_match['modules']) - 5} more")
                    lines.append("")

                # Show detailed module list
                lines.append(f"## All Matching Modules ({len(matches)} total)")
                lines.append("")

                for match in matches[:10]:
                    lines.append(f"### {match['name']}")
                    lines.append(f"**Description**: {match['description']}")
                    datasets = match["required_datasets"]
                    if datasets:
                        lines.append(f"**Required Datasets**: {', '.join(datasets)}")
                    else:
                        lines.append("**Required Datasets**: None (works with any data.frame)")
                    lines.append(f"**Categories**: {', '.join(match['categories'])}")
                    lines.append("")

                if len(matches) > 10:
                    lines.append(f"... and {len(matches) - 10} more modules")

                response = "\n".join(lines)
            else:
                response = json.dumps(
                    {
                        "query": params.analysis_type,
                        "matching_categories": category_matches[:5],
                        "count": len(matches),
                        "modules": matches[:20],
                    },
                    indent=2,
                )

        else:
            # Step 3: Fall back to text search if no category matches
            matches = []
            for module_name, module_info in all_modules.items():
                description = module_info.get("description", "").lower()
                name_lower = module_name.lower()

                # Calculate relevance score
                score = 0
                if search_term in name_lower:
                    score += 10
                if search_term in description:
                    score += 5

                # Check individual words
                search_words = search_term.split()
                for word in search_words:
                    if len(word) > 2:
                        if word in name_lower:
                            score += 3
                        if word in description:
                            score += 2

                if score > 0:
                    matches.append(
                        {
                            "name": module_name,
                            "description": module_info.get("description", ""),
                            "required_datasets": module_info.get("required_datasets", []),
                            "score": score,
                        }
                    )

            matches.sort(key=lambda x: x["score"], reverse=True)

            if not matches:
                # Suggest available categories
                available_categories = list(all_categories.keys())
                return (
                    f"No modules found for '{params.analysis_type}'.\n\n"
                    "Available analysis categories:\n"
                    + "\n".join(
                        [f"  - {cat.replace('_', ' ')}" for cat in available_categories[:10]]
                    )
                    + "\n\nTry terms like: 'survival', 'safety', 'efficacy', 'data exploration', 'visualization'"
                )

            # Format text search results
            if params.response_format == ResponseFormat.MARKDOWN:
                lines = [f"# Text Search Results for '{params.analysis_type}'", ""]
                lines.append(f"Found {len(matches)} matching module(s) via text search:")
                lines.append("")

                for match in matches[:10]:
                    lines.append(f"## {match['name']}")
                    lines.append(f"**Description**: {match['description']}")
                    datasets = match["required_datasets"]
                    if datasets:
                        lines.append(f"**Required Datasets**: {', '.join(datasets)}")
                    else:
                        lines.append("**Required Datasets**: None (works with any data.frame)")
                    lines.append("")

                if len(matches) > 10:
                    lines.append(f"... and {len(matches) - 10} more matches")

                response = "\n".join(lines)
            else:
                response = json.dumps(
                    {"query": params.analysis_type, "count": len(matches), "matches": matches[:20]},
                    indent=2,
                )

        return _truncate_response(response)

    except Exception as e:
        return f"Error searching modules: {e!s}"


async def tealflow_check_dataset_requirements(params: CheckDatasetRequirementsInput) -> str:
    """
    Validate dataset availability for a specific module.

    Compares module's required datasets against available datasets list.
    Returns compatibility status and lists any missing datasets.

    Supports flexible dataset types:
    - BDS_DATASET: Matches any BDS dataset (ADLB, ADVS, ADQS, etc.)
    - BDS_CONTINUOUS: Matches BDS datasets typically containing continuous data
    - BDS_BINARY: Matches BDS datasets that can have binary outcomes
    - Specific names: ADSL, ADTTE, ADAE, etc.
    """
    try:
        # Validate module exists
        exists, package, suggestion = _validate_module_exists(params.module_name)

        if not exists:
            msg = f"Error: Module '{params.module_name}' not found."
            if suggestion:
                msg += f" Did you mean '{suggestion}'?"
            return msg

        # Get module info
        if package == "clinical":
            clinical_data = _get_clinical_modules()
            module_info = clinical_data.get("modules", {}).get(params.module_name, {})
        else:
            general_data = _get_general_modules()
            module_info = general_data.get("modules", {}).get(params.module_name, {})

        required_datasets = module_info.get("required_datasets", [])
        typical_datasets = module_info.get("typical_datasets", [])
        dataset_requirements = module_info.get("dataset_requirements", {})
        notes = module_info.get("notes", "")
        available = params.available_datasets

        # Check compatibility
        if not required_datasets:
            # General modules typically work with any data.frame
            if params.response_format == ResponseFormat.MARKDOWN:
                return (
                    f"# Dataset Compatibility: {params.module_name}\n\n✅ **Compatible**\n\n"
                    "This module works with any data.frame and has no specific dataset requirements."
                )
            return json.dumps(
                {
                    "module_name": params.module_name,
                    "compatible": True,
                    "required_datasets": [],
                    "available_datasets": available,
                    "missing_datasets": [],
                },
                indent=2,
            )

        # Define BDS datasets (Basic Data Structure)
        bds_datasets = ["ADLB", "ADVS", "ADQS", "ADEG", "ADEX"]
        bds_continuous_typical = ["ADLB", "ADVS", "ADQS"]
        bds_binary_typical = ["ADRS"]

        # Check each required dataset
        missing = []
        matched_datasets = {}

        for req_ds in required_datasets:
            if req_ds == "BDS_DATASET":
                # Check if any BDS dataset is available
                matches = [ds for ds in available if ds in bds_datasets]
                if matches:
                    matched_datasets[req_ds] = matches
                else:
                    missing.append(req_ds)
            elif req_ds == "BDS_CONTINUOUS":
                # Check if any BDS dataset that typically has continuous data is available
                matches = [
                    ds for ds in available if ds in bds_continuous_typical or ds in bds_datasets
                ]
                if matches:
                    matched_datasets[req_ds] = matches
                else:
                    missing.append(req_ds)
            elif req_ds == "BDS_BINARY":
                # Check if any BDS dataset that can have binary data is available
                matches = [ds for ds in available if ds in bds_binary_typical or ds in bds_datasets]
                if matches:
                    matched_datasets[req_ds] = matches
                else:
                    missing.append(req_ds)
            else:
                # Specific dataset name
                if req_ds in available:
                    matched_datasets[req_ds] = [req_ds]
                else:
                    missing.append(req_ds)

        compatible = len(missing) == 0

        # Build compatible combinations for markdown output
        compatible_combinations = []
        if compatible:
            # Build all possible dataset combinations
            specific_datasets = []
            flexible_options = []

            for req_ds in required_datasets:
                matches = matched_datasets.get(req_ds, [])
                if req_ds in ["BDS_DATASET", "BDS_CONTINUOUS", "BDS_BINARY"]:
                    # Flexible type - can use any of the matches
                    flexible_options.append((req_ds, matches))
                else:
                    # Specific dataset
                    specific_datasets.extend(matches)

            # Generate combinations
            if flexible_options:
                # For each flexible dataset type, show options
                for _, options in flexible_options:
                    for opt in options:
                        combo_list = [*specific_datasets, opt]
                        compatible_combinations.append(" + ".join(combo_list))
            else:
                # Only specific datasets
                if specific_datasets:
                    compatible_combinations.append(" + ".join(specific_datasets))

        # Format response
        if params.response_format == ResponseFormat.MARKDOWN:
            lines = [f"# Dataset Compatibility: {params.module_name}", ""]

            if compatible:
                lines.append("✅ **Compatible** - All required datasets are available")
            else:
                lines.append("❌ **Incompatible** - Missing required datasets")

            lines.append("")

            # Show compatible combinations first (most important info)
            if compatible and compatible_combinations:
                lines.append("## Compatible Dataset Combinations")
                lines.append("")
                lines.append("You can use this module with any of these dataset combinations:")
                for combo in compatible_combinations:
                    lines.append(f"- **{combo}**")
                lines.append("")

            lines.append("## Details")
            lines.append("")
            lines.append(f"**Required Datasets**: {', '.join(required_datasets)}")

            if typical_datasets:
                lines.append(f"**Typical Datasets**: {', '.join(typical_datasets)}")

            lines.append(f"**Available Datasets**: {', '.join(available)}")

            # Show matched flexible datasets
            for req_ds, matches in matched_datasets.items():
                if req_ds in ["BDS_DATASET", "BDS_CONTINUOUS", "BDS_BINARY"]:
                    lines.append(f"**Matched {req_ds}**: {', '.join(matches)}")

            if missing:
                lines.append(f"**Missing Datasets**: {', '.join(missing)}")
                lines.append("")

                # Provide specific guidance for flexible dataset types
                for miss in missing:
                    if miss == "BDS_DATASET":
                        lines.append(
                            f"**{miss}**: This module needs a BDS (Basic Data Structure) dataset. "
                            "Typical options: ADLB, ADVS, ADQS. Use tealflow_get_dataset_info to verify "
                            "your dataset has BDS structure (PARAMCD, AVAL, USUBJID, AVISIT)."
                        )
                    elif miss == "BDS_CONTINUOUS":
                        lines.append(
                            f"**{miss}**: This module needs a BDS dataset with continuous AVAL. "
                            "Typical options: ADLB (lab values), ADVS (vitals), ADQS (questionnaire scores). "
                            "Use tealflow_get_dataset_info to verify AVAL contains numeric continuous values."
                        )
                    elif miss == "BDS_BINARY":
                        lines.append(
                            f"**{miss}**: This module needs a BDS dataset with binary AVAL (0/1). "
                            "Typical options: ADRS (response data) or derived binary variables. "
                            "Use tealflow_get_dataset_info to verify AVAL is binary."
                        )
                    else:
                        lines.append(
                            f"**{miss}**: Specific dataset required. Ensure this dataset is loaded "
                            "before using this module."
                        )

                lines.append("")
                lines.append(
                    "**Suggestion**: Use tealflow_get_dataset_info on your available datasets to verify "
                    "they meet the module's requirements, or choose a different module."
                )

            # Add dataset requirements details if available
            if dataset_requirements:
                lines.append("")
                lines.append("## Dataset Requirements Details")
                for ds, req in dataset_requirements.items():
                    lines.append(f"- **{ds}**: {req}")

            # Add notes if available
            if notes:
                lines.append("")
                lines.append(f"**Note**: {notes}")

            response = "\n".join(lines)
        else:
            response = json.dumps(
                {
                    "module_name": params.module_name,
                    "compatible": compatible,
                    "compatible_combinations": compatible_combinations,
                    "required_datasets": required_datasets,
                    "typical_datasets": typical_datasets,
                    "available_datasets": available,
                    "missing_datasets": missing,
                    "matched_datasets": matched_datasets,
                    "dataset_requirements": dataset_requirements,
                    "notes": notes,
                },
                indent=2,
            )

        return response

    except Exception as e:
        return f"Error checking dataset requirements: {e!s}"


async def tealflow_list_datasets(params: ListDatasetsInput) -> str:
    """
    List standard ADaM datasets available in the Flow project.

    Returns hardcoded information about the five standard CDISC ADaM datasets
    (ADSL, ADTTE, ADRS, ADQS, ADAE) including descriptions, usage statistics,
    and key modules that use each dataset.
    """
    try:
        # Dataset information
        datasets = {
            "ADSL": {
                "name": "ADSL",
                "full_name": "Subject-Level Analysis Dataset",
                "description": (
                    "Contains one record per subject with demographic and baseline characteristics. "
                    "This is the primary parent dataset used by most clinical modules."
                ),
                "usage": "Used in 37/37 clinical modules (100%)",
                "type": "Parent dataset",
            },
            "ADTTE": {
                "name": "ADTTE",
                "full_name": "Time-to-Event Analysis Dataset",
                "description": (
                    "Contains time-to-event data for survival analysis including event times and censoring information."
                ),
                "usage": "Used in 4 clinical modules (11%)",
                "type": "Analysis dataset",
                "modules": ["tm_g_km", "tm_g_forest_tte", "tm_t_coxreg", "tm_t_tte"],
            },
            "ADRS": {
                "name": "ADRS",
                "full_name": "Response Analysis Dataset",
                "description": "Contains tumor response data and endpoints for efficacy analysis.",
                "usage": "Used in 3 clinical modules (8%)",
                "type": "Analysis dataset",
                "modules": ["tm_g_forest_rsp", "tm_t_binary_outcome", "tm_t_logistic"],
            },
            "ADQS": {
                "name": "ADQS",
                "full_name": "Questionnaire Analysis Dataset",
                "description": "Contains patient-reported outcome and quality of life questionnaire data.",
                "usage": "Used in 3 clinical modules",
                "type": "Analysis dataset",
                "modules": ["tm_t_ancova", "tm_a_gee", "tm_a_mmrm"],
            },
            "ADAE": {
                "name": "ADAE",
                "full_name": "Adverse Events Analysis Dataset",
                "description": "Contains adverse event data including severity, relationship, and outcome information.",
                "usage": "Used in 9 clinical modules (24%)",
                "type": "Analysis dataset",
                "modules": [
                    "tm_g_barchart_simple",
                    "tm_g_pp_adverse_events",
                    "tm_t_events",
                    "tm_t_events_by_grade",
                ],
            },
        }

        if params.response_format == ResponseFormat.MARKDOWN:
            lines = ["# Clinical Trial Datasets in Flow", ""]
            lines.append(
                "These are the standard ADaM datasets available in the Flow project following CDISC standards."
            )
            lines.append("")

            for ds_name, ds_info in datasets.items():
                lines.append(f"## {ds_name} - {ds_info['full_name']}")  # type: ignore[index]
                lines.append(f"**Type**: {ds_info['type']}")  # type: ignore[index]
                lines.append(f"**Description**: {ds_info['description']}")  # type: ignore[index]
                lines.append(f"**Usage**: {ds_info['usage']}")  # type: ignore[index]

                if "modules" in ds_info:  # type: ignore[operator]
                    lines.append(f"**Key Modules**: {', '.join(ds_info['modules'][:4])}")  # type: ignore[index]

                lines.append("")

            response = "\n".join(lines)
        else:
            response = json.dumps(
                {"datasets": list(datasets.values()), "count": len(datasets)}, indent=2
            )

        return response

    except Exception as e:
        return f"Error listing datasets: {e!s}"


async def tealflow_get_app_template(params: GetAppTemplateInput) -> str:
    """
    Return the base R code template for Teal applications.

    Reads app.template.R from knowledge base directory and formats as markdown
    with usage instructions or as JSON with structured metadata.
    """
    try:
        template_path = KNOWLEDGE_BASE_DIR / "app.template.R"

        if not template_path.exists():
            return "Error: Template file not found at knowledge_base/app.template.R"

        with open(template_path) as f:
            template_content = f.read()

        if params.response_format == ResponseFormat.MARKDOWN:
            return (
                "# Teal App Template\n\n"
                "This is the base template for creating Teal applications. "
                "Copy this code as your starting point.\n\n"
                "```r\n"
                f"{template_content}\n"
                "```\n\n"
                "## Next Steps\n\n"
                "1. Copy the template above to `app.R`\n"
                "2. Use `tealflow_search_modules_by_analysis` to find modules for your analysis\n"
                "3. Use `tealflow_generate_module_code` to generate code for each module\n"
                "4. Add generated modules inside `modules()` (around line 78)\n"
                "5. Run the app with `Rscript app.R` or in RStudio\n\n"
                "## Example Module Addition\n\n"
                "```r\n"
                "# In the modules() section:\n"
                "app <- init(\n"
                "  data = data,\n"
                "  modules = modules(\n"
                "    tm_front_page(\n"
                '      label = "App Info",\n'
                "    ),\n"
                '    tm_data_table("Data Table"),\n'
                '    tm_variable_browser("Variable Browser"),\n'
                "    # Add your modules here:\n"
                "    tm_g_km(\n"
                '      label = "Kaplan-Meier Plot",\n'
                '      dataname = "ADTTE",\n'
                "      ...\n"
                "    )\n"
                "  )\n"
                ")\n"
                "```"
            )
        # JSON format
        return json.dumps(
            {
                "template": template_content,
                "file_name": "app.template.R",
                "usage_instructions": [
                    "Copy template to app.R",
                    "Search for modules with tealflow_search_modules_by_analysis",
                    "Generate module code with tealflow_generate_module_code",
                    "Add modules to the modules() section",
                    "Run the app",
                ],
            },
            indent=2,
        )

    except Exception as e:
        return f"Error getting app template: {e!s}"
