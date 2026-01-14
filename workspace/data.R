library(teal)

ADSL <- readRDS("workspace/ADSL.Rds")
ADTTE <- readRDS("workspace/ADTTE.Rds")
ADRS <- readRDS("workspace/ADRS.Rds")
ADQS <- readRDS("workspace/ADQS.Rds")
ADAE <- readRDS("workspace/ADAE.Rds")

## Data reproducible code ----
data <- teal_data(
  ADSL = ADSL,
  ADTTE = ADTTE,
  ADRS = ADRS,
  ADQS = ADQS,
  ADAE = ADAE,
  join_keys = default_cdisc_join_keys[c("ADSL", "ADTTE", "ADRS", "ADQS", "ADAE")]
)
