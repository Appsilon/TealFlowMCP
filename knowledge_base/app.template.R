library(teal.modules.general)
library(teal.modules.clinical)
options(shiny.useragg = FALSE)

source("data.R")

# Configuration For Modules
ADSL <- data[["ADSL"]]
ADTTE <- data[["ADTTE"]]
ADRS <- data[["ADRS"]]
ADQS <- data[["ADQS"]]
ADAE <- data[["ADAE"]]

arm_vars <- c("ARMCD", "ARM")
strata_vars <- c("STRATA1", "STRATA2")
facet_vars <- c("AGEGR1", "BMRKR2", "SEX", "COUNTRY")
visit_vars <- c("AVISIT", "AVISITN")

cs_arm_var <- choices_selected(
  choices = variable_choices(ADSL, subset = arm_vars),
  selected = "ARM"
)

cs_strata_var <- choices_selected(
  choices = variable_choices(ADSL, subset = strata_vars),
  selected = "STRATA1"
)

cs_facet_var <- choices_selected(
  choices = variable_choices(ADSL, subset = facet_vars),
  selected = "AGEGR1"
)

cs_paramcd_tte <- choices_selected(
  choices = value_choices(ADTTE, "PARAMCD", "PARAM"),
  selected = "OS"
)

cs_paramcd_rsp <- choices_selected(
  choices = value_choices(ADRS, "PARAMCD", "PARAM"),
  selected = "BESRSPI"
)

cs_paramcd_qs <- choices_selected(
  choices = value_choices(ADQS, "PARAMCD", "PARAM"),
  selected = "FKSI-FWB"
)

cs_visit_var_qs <- choices_selected(
  choices = variable_choices(ADQS, subset = visit_vars),
  selected = "AVISIT"
)

arm_ref_comp <- list(
  ARMCD = list(
    ref = value_choices("ADSL", var_choices = "ARMCD", var_label = "ARM", subset = "ARM A"),
    comp = value_choices("ADSL", var_choices = "ARMCD", var_label = "ARM", subset = c("ARM B", "ARM C"))
  ),
  ARM = list(ref = "A: Drug X", comp = c("B: Placebo", "C: Combination"))
)

ae_anl_vars <- names(ADAE)[startsWith(names(ADAE), "TMPFL_")]

# flag variables for AE baskets; set to NULL if not applicable to study
aesi_vars <-
  names(ADAE)[startsWith(names(ADAE), "TMP_SMQ") |
    startsWith(names(ADAE), "TMP_CQ")]

#  App
app <- init(
  data = data,
  modules = modules(
    tm_front_page(
      label = "App Info",
    ),
    tm_data_table("Data Table"),
    tm_variable_browser("Variable Browser")
    # Add modules here
  )
)

shinyApp(app$ui, app$server)
