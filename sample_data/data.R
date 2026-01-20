library(teal)

ADSL <- readRDS("data/ADSL.Rds")
ADTTE <- readRDS("data/ADTTE.Rds")
ADRS <- readRDS("data/ADRS.Rds")
ADQS <- readRDS("data/ADQS.Rds")
ADAE <- readRDS("data/ADAE.Rds")

## Data reproducible code ----
data <- teal_data(
  ADSL = ADSL,
  ADTTE = ADTTE,
  ADRS = ADRS,
  ADQS = ADQS,
  ADAE = ADAE,
  join_keys = default_cdisc_join_keys[c("ADSL", "ADTTE", "ADRS", "ADQS", "ADAE")]
)
