library(teal)

ADSL <- readRDS("knowledge_base/ADSL.Rds")
ADTTE <- readRDS("knowledge_base/ADTTE.Rds")
ADRS <- readRDS("knowledge_base/ADRS.Rds")
ADQS <- readRDS("knowledge_base/ADQS.Rds")
ADAE <- readRDS("knowledge_base/ADAE.Rds")

## Data reproducible code ----
data <- teal_data(
  ADSL = ADSL,
  ADTTE = ADTTE,
  ADRS = ADRS,
  ADQS = ADQS,
  ADAE = ADAE,
  join_keys = default_cdisc_join_keys[c("ADSL", "ADTTE", "ADRS", "ADQS", "ADAE")]
)
