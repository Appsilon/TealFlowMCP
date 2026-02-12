library(teal.modules.general)
library(teal.modules.clinical)
options(shiny.useragg = FALSE)

source("data.R")

# Configuration For Modules


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
