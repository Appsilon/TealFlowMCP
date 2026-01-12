teal is a shiny-based interactive exploration framework for analyzing data. teal applications require app developers to specify:

Data, which can be:
CDISC data, commonly used for clinical trial reporting
Independent datasets, for example from a data.frame
Related datasets, for example a set of data.frames with key columns to enable data joins
MultiAssayExperiment objects which are R data structures for representing and analyzing multi-omics experiments
teal modules:
teal modules are shiny modules built within the teal framework that specify analysis to be performed. For example, it can be a module for exploring outliers in the data, or a module for visualizing the data in line plots. Although these can be created from scratch, many teal modules have been released and we recommend starting with modules found in the following packages:
teal.modules.general: general modules for exploring relational/independent/CDISC data
teal.modules.clinical: modules specific to CDISC data and clinical trial reporting

### teal.modules.general (general analysis modules)

The teal.modules.general package is a collection of standard Shiny modules for common exploratory analyses. These modules are designed to work with a variety of data types (independent data frames, related datasets, or CDISC structured data). They cover general-purpose functionality that is useful in many applications. For example, teal.modules.general includes modules for:

- **Data viewing and summarization:** e.g. `tm_data_table` (tabular data view), `tm_variable_browser` (view variable metadata/distribution), `tm_missing_data` (summarize missing values)
- **Visualizations:** e.g. `tm_g_scatterplot` for scatter plots, `tm_g_distribution` for distribution histograms, `tm_g_association` for categorical association plots
- **Statistical analysis (simple):** e.g. `tm_a_pca` for principal component analysis, `tm_a_regression` for basic regression modeling
- **Outlier detection:** e.g. `tm_outliers` to identify potential outliers in numeric data
- **File viewing:** e.g. `tm_file_viewer` if the app needs to display an external file (like a PDF report or image).

These modules act as building blocks – an app developer can pick and configure them to quickly assemble a functioning app without writing custom analysis code. All modules in teal.modules.general follow the teal framework's conventions, meaning they will automatically receive the filtered data and produce outputs accordingly. They can handle CDISC-like data as well as generic data frames, making them versatile.

The package also provides a teal Gallery of example apps and a TLG (Tables, Listings, Graphs) catalog to demonstrate how these modules look and behave in practice. In practice, you might include modules like a summary table, a histogram plot, and a data table in an exploratory app – teal.modules.general has ready-made modules for each of those needs.

### teal.modules.clinical (clinical trial specific modules)

The teal.modules.clinical package extends teal with modules specifically tailored for clinical trial reporting and analysis. These modules produce many standard outputs used in clinical development, which makes {teal} especially powerful in a pharma context. Highlights of what's included:

- **Efficacy and Safety Plots:** For example, Kaplan-Meier survival curves (`tm_g_km()` for time-to-event endpoints), forest plots for subgroup analyses (response or time-to-event variants), line plots for metrics over time (e.g. lab values or efficacy measures), etc.

- **Statistical Models:** Pre-built modules for common analyses like MMRM (mixed models for repeated measures, via `tm_a_mmrm()`), logistic regression (`tm_t_logistic()` for binary outcomes), Cox proportional hazards (`tm_t_coxreg()` for survival outcomes), among others. These modules allow users to fit models and view results interactively without writing model code each time.

- **Summary Tables:** Modules that generate tables frequently needed in reporting, such as summary of unique patients in each category (`tm_t_summary()`), exposure summaries (`tm_t_exposure()`), and change-from-baseline summaries by treatment (`tm_t_summary_by()`). These leverage the tern package under the hood for creating well-formatted tables.

- **Patient Profile modules:** Specialized modules to review individual patient data, for example, a patient profile timeline (`tm_g_pp_patient_timeline()`), patient-level vitals over time (`tm_g_pp_vitals()` plot), and a patient-level data table (`tm_t_pp_basic_info()` for demographic/baseline info). These are very useful for medical monitors or safety reviewers to drill down into single subject narratives.

By using teal.modules.clinical, an app developer can rapidly assemble an interactive version of what would otherwise be static TLF outputs. For instance, instead of a static PDF of a KM plot by subgroup, a teal app could include a KM module where the user dynamically selects subgroups or endpoints and the plot updates accordingly. Because these modules are implemented with validated R routines (often using {tern} and other pharma-specific libraries), they produce outputs comparable to traditional reports but with the benefit of interactivity. This package is a key part of making {teal} a plug-and-play solution for clinical trial analyses.

# Detailed description of the modules:

## tm_g_km

### Purpose

This module produces a ggplot-style Kaplan-Meier plot for data with ADaM structure.

### Arguments

**Required arguments**

- **label** (`character`): menu item label of the module in the teal app.
- **dataname** (`character`): name of the analysis dataset to use.
- **arm_var** (`choices_selected`): grouping variable(s); object containing available choices and preselected arm variable(s).
- **paramcd** (`choices_selected`): parameter code variable from the dataset.
- **strata_var** (`choices_selected`): variable(s) for stratified analysis.
- **facet_var** (`choices_selected`): variable(s) for plot faceting.

**Optional arguments (with defaults)**

- **parentname** (`character`, default = ifelse(inherits(arm_var, "data_extract_spec"), teal.transform::datanames_input(arm_var), "ADSL")): name of the parent analysis dataset, usually “ADSL”.
- **arm_ref_comp** (`list`, default = NULL): named list defining reference and comparison arms for each arm variable.
- **time_unit_var** (`choices_selected`, default = choices_selected(variable_choices(dataname, "AVALU"), "AVALU", fixed = TRUE)): time unit variable.
- **aval_var** (`choices_selected`, default = choices_selected(variable_choices(dataname, "AVAL"), "AVAL", fixed = TRUE)): analysis value variable.
- **cnsr_var** (`choices_selected`, default = choices_selected(variable_choices(dataname, "CNSR"), "CNSR", fixed = TRUE)): censoring indicator variable.
- **conf_level** (`choices_selected`, default = choices_selected(c(0.95, 0.9, 0.8), 0.95, keep_order = TRUE)): confidence level for median survival.
- **font_size** (`numeric`, default = c(11L, 1L, 30)): vector of current, minimum, and maximum font sizes.
- **control_annot_surv_med** (`list`, default = control_surv_med_annot()): parameters controlling survival-median annotation.
- **control_annot_coxph** (`list`, default = control_coxph_annot(x = 0.27, y = 0.35, w = 0.3)): parameters controlling Cox-model annotation.
- **legend_pos** (`numeric(2)` or `NULL`, default = c(0.9, 0.5)): legend position; if `NULL`, auto bottom-right or middle-right.
- **rel_height_plot** (`numeric`, default = c(80L, 0L, 100L)): proportion of height for KM plot.
- **plot_height** (`numeric`, default = c(800L, 400L, 5000L)): plot height controls.
- **plot_width** (`numeric`, default = NULL): plot width controls.
- **pre_output** (`shiny.tag`, default = NULL): UI element placed before the plot.
- **post_output** (`shiny.tag`, default = NULL): UI element placed after the plot.

## tm_g_forest_tte

Important:
- The parameter facet_var should NEVER be used with tm_g_forest_tte, as it is not supported by this module.
- ALL the required parameters, including subgroup_var, should be included in the call.

### Purpose

This module produces a grid‐style forest survival plot for time-to-event data with ADaM structure.

### Arguments

**Required arguments**

* **label** (`character`): menu item label of the module in the teal app.
* **dataname** (`character`): analysis data used in the module.
* **arm_var** (`teal.transform::choices_selected()`): object with all available choices and a preselected option for the grouping variable in the results table.
* **subgroup_var** (`teal.transform::choices_selected()`): object with all available choices and a preselected option for defining default subgroups.
* **paramcd** (`teal.transform::choices_selected()`): object with all available choices and a preselected option for the parameter code variable from the analysis data.
* **strata_var** (`teal.transform::choices_selected()`): names of the variables for stratified analysis.

**Optional arguments (with defaults)**

* **parentname** (`character`, default = `ifelse(inherits(arm_var, "data_extract_spec"), teal.transform::datanames_input(arm_var), "ADSL")`): parent analysis data used in the module, usually `ADSL`.
* **arm_ref_comp** (`list`, default = `NULL`): named list defining default reference and comparison arms for each arm variable in `ADSL`.
* **aval_var** (`teal.transform::choices_selected()`, default = `teal.transform::choices_selected(teal.transform::variable_choices(dataname, "AVAL"), "AVAL", fixed = TRUE)`): object with all available choices and a preselected option for the analysis variable.
* **cnsr_var** (`teal.transform::choices_selected()`, default = `teal.transform::choices_selected(teal.transform::variable_choices(dataname, "CNSR"), "CNSR", fixed = TRUE)`): object with all available choices and a preselected option for the censoring variable.
* **stats** (`character`, default = `c("n_tot_events", "n_events", "median", "hr", "ci")`): names of statistics to report (e.g., number of events, median survival, hazard ratio, confidence interval).
* **riskdiff** (`list`, default = `NULL`): settings for adding a risk-difference column; if `NULL`, no risk difference is added.
* **conf_level** (`teal.transform::choices_selected()`, default = `teal.transform::choices_selected(c(0.95, 0.9, 0.8), 0.95, keep_order = TRUE)`): object with choices of confidence level (values in (0, 1)).
* **time_unit_var** (`teal.transform::choices_selected()`, default = `teal.transform::choices_selected(teal.transform::variable_choices(dataname, "AVALU"), "AVALU", fixed = TRUE)`): object with choices and a preselected option for the time unit variable.
* **fixed_symbol_size** (`logical`, default = `TRUE`): when `TRUE`, uses the same symbol size for each estimate; otherwise, size is proportional to sample size.
* **plot_height** (`numeric`, default = `c(500L, 200L, 2000L)`): vector (`value`, `min`, `max`) specifying plot height and enabling an interactive slider.
* **plot_width** (`numeric`, default = `c(1500L, 800L, 3000L)`): vector (`value`, `min`, `max`) specifying plot width and enabling an interactive slider.
* **rel_width\_forest** (`proportion`, default = `c(25L, 0L, 100L)`): proportion of total width allocated to the forest plot (table width = 1 – this value).
* **font_size** (`numeric(1)`, default = `c(15L, 1L, 30L)`): font size.
* **pre_output** (`shiny.tag`, default = `NULL`): content placed before the output for context.
* **post_output** (`shiny.tag`, default = `NULL`): content placed after the output for context.
* **ggplot2_args** (`ggplot2_args`, default = `teal.widgets::ggplot2_args()`): object with custom settings for the module’s plot.
* **transformators** (`list`, default = `list()`): list of transformations to apply to the module’s data input.
* **decorators** (`list`, default = `list()`): named list of decorators for tables or plots in the module output.

## tm_t_tte

### Purpose

This module produces a time-to-event analysis summary table consistent with the TLG Catalog template `TTET01`.

### Arguments

**Required arguments**

* **label** (`character`): menu item label of the module in the teal app.
* **dataname** (`character`): analysis data used in teal module.
* **arm_var** (`teal.transform::choices_selected()`): object with all available choices and preselected option for the grouping variable in the results table.
* **paramcd** (`teal.transform::choices_selected()`): object with all available choices and preselected option for the parameter code variable from `dataname`.
* **strata_var** (`teal.transform::choices_selected()`): names of the variables for stratified analysis.
* **time_points** (`teal.transform::choices_selected()`): object with all available choices and preselected option for time points that can be used in `tern::surv_timepoint()`. Example: `choices_selected(c(182, 365, 547), 182)`

**Optional arguments (with defaults)**

* **parentname** (`character`, default = `ifelse(inherits(arm_var, "data_extract_spec"), teal.transform::datanames_input(arm_var), "ADSL")`): parent analysis data used in the module, usually this refers to `ADSL`.
* **arm_ref_comp** (`list`, default = `NULL`): named list defining default reference and comparison arms for each arm variable in `ADSL`.
* **aval_var** (`teal.transform::choices_selected()`, default = `teal.transform::choices_selected(teal.transform::variable_choices(dataname, "AVAL"), "AVAL", fixed = TRUE)`): object with all available choices and pre-selected option for the analysis variable.
* **cnsr_var** (`teal.transform::choices_selected()`, default = `teal.transform::choices_selected(teal.transform::variable_choices(dataname, "CNSR"), "CNSR", fixed = TRUE)`): object with all available choices and preselected option for the censoring variable.
* **conf_level_coxph** (`teal.transform::choices_selected()`, default = `teal.transform::choices_selected(c(0.95, 0.9, 0.8), 0.95, keep_order = TRUE)`): object with available choices and pre-selected option for the Cox PH confidence level.
* **conf_level_survfit** (`teal.transform::choices_selected()`, default = `teal.transform::choices_selected(c(0.95, 0.9, 0.8), 0.95, keep_order = TRUE)`): object with available choices and pre-selected option for the survival fit confidence level.
* **time_unit_var** (`teal.transform::choices_selected()`, default = `teal.transform::choices_selected(teal.transform::variable_choices(dataname, "AVALU"), "AVALU", fixed = TRUE)`): object with all available choices and pre-selected option for the time unit variable.
* **event_desc_var** (`character` or `teal.transform::data_extract_spec()`, default = `teal.transform::choices_selected("EVNTDESC", "EVNTDESC", fixed = TRUE)`): variable name with the event description information.
* **add_total** (`logical`, default = `FALSE`): whether to include a column with the total number of patients.
* **total_label** (`string`, default = `default_total_label()`): string to display as the total column/row label if enabled.
* **na_level** (`string`, default = `default_na_str()`): string used to replace missing or empty values in character or factor variables.
* **pre_output** (`shiny.tag`, default = `NULL`): content placed before the output for context.
* **post_output** (`shiny.tag`, default = `NULL`): content placed after the output for context.
* **basic_table_args** (`basic_table_args`, default = `teal.widgets::basic_table_args()`): object with settings for the module table.
* **transformators** (`list`, default = `list()`): list of transformations to apply to the module’s data input.
* **decorators** (`list`, default = `list()`): named list of decorators for tables or plots in the module output.

## tm_t_coxreg

### Purpose

This module fits Cox univariable or multivariable regression models to time-to-event data, generating tables consistent with the TLG Catalog templates COXT01 and COXT02.

### Arguments

**Required arguments**

* **label** (`character`): menu item label of the module in the teal app.
* **dataname** (`character`): analysis data used in teal module.
* **arm_var** (`teal.transform::choices_selected()`): object with all available choices and preselected option for variable names that can be used as arm\_var. It defines the grouping variable in the results table.
* **paramcd** (`teal.transform::choices_selected()`): object with all available choices and preselected option for the parameter code variable from dataname.
* **cov_var** (`teal.transform::choices_selected()`): object with all available choices and preselected option for the covariates variables.
* **strata_var** (`teal.transform::choices_selected()`): names of the variables for stratified analysis.

**Optional arguments (with defaults)**

* **parentname** (`character`, default = `ifelse(inherits(arm_var, "data_extract_spec"), teal.transform::datanames_input(arm_var), "ADSL")`): parent analysis data used in teal module, usually this refers to ADSL.
* **arm_ref_comp** (`list`, default = `NULL`): named list defining default reference and comparison arms for each arm variable in ADSL.
* **aval_var** (`teal.transform::choices_selected()`, default = `teal.transform::choices_selected(teal.transform::variable_choices(dataname, "AVAL"), "AVAL", fixed = TRUE)`): object with all available choices and pre-selected option for the analysis variable.
* **cnsr_var** (`teal.transform::choices_selected()`, default = `teal.transform::choices_selected(teal.transform::variable_choices(dataname, "CNSR"), "CNSR", fixed = TRUE)`): object with all available choices and preselected option for the censoring variable.
* **multivariate** (`logical`, default = `TRUE`): if FALSE, the univariable approach is used instead of the multivariable model.
* **na_level** (`string`, default = `default_na_str()`): used to replace all NA or empty values in character or factor variables in the data. Defaults to "<Missing>".
* **conf_level** (`teal.transform::choices_selected()`, default = `teal.transform::choices_selected(c(0.95, 0.9, 0.8), 0.95, keep_order = TRUE)`): object with all available choices and pre-selected option for the confidence level, each within range of (0, 1).
* **pre_output** (`shiny.tag`, default = `NULL`): content placed before the output for context.
* **post_output** (`shiny.tag`, default = `NULL`): content placed after the output for context.
* **basic_table_args** (`basic_table_args`, default = `teal.widgets::basic_table_args()`): object with settings for the module table.
* **transformators** (`list`, default = `list()`): list of transformations to apply to the module’s data input.
* **decorators** (`list`, default = `list()`): named list of decorators for tables or plots in the module output.
