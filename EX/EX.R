# options(error=traceback)
# install.packages("tidyverse")
suppressPackageStartupMessages(library(tidyverse))
library(readr)
library(dplyr)
library(purrr)
library(cli)

#  Rscript EX.R "$cruise_number" "$dive_number" "$dive_start_date" "$tmp_output_destination" "$output_destination_path"

#  Access the arguments
args <- commandArgs(trailingOnly = TRUE)
cruise_number <- args[1]
dive_number <- args[2]
dive_start_date <- args[3]
tmp_input_files <- args[4]
output_destination_path <- args[5]

format_time <- function(timestamp) {
  return (format(as.POSIXct(timestamp, format = "%Y-%m-%dT%H:%M:%S"), format = "%Y%m%dT%H%M%SZ"))
}

read_ctd_data <- function() {
  ctd_folder_path <- paste0(tmp_input_files, "/ctd")
  ctd_file_pattern <- paste0(cruise_number, "_", dive_number, ".*", ".cnv")
  ctd_file <- list.files(ctd_folder_path, pattern = ctd_file_pattern, full.names = TRUE)

  # these can can be changed as needed to match the column names in the CTD file
  column_names <- c("Timestamp", "prDM", "prDE", "Temperature", "c0S/m", "seaTurbMtr", "sbeox0V", "upoly0",
                    "modError", "Depth", "Salinity", "svCM", "sbeox0Mg/L", "Oxygen.Mg.L", "sbox0Mm/Kg", "flag")

  file_conn <- file(ctd_file, open="r")
  line_count <- 0

  # read thorough file until "*END*" is found
  while (TRUE) {
      line <- readLines(file_conn, n = 1)
      line_count <- line_count + 1
      if (grepl("*END*", line)) {
          break
      }
  }
  close(file_conn)

  # Read and combine the files into a table
  all_ctd_data <- read.table(ctd_file, skip = line_count, header = FALSE, col.names = column_names)
  pruned_seconds <- all_ctd_data[!duplicated(all_ctd_data[, 1]), ]  # Only grab one row for each second

  # convert timestamp
  base_time <- as.POSIXct("2000-01-01 00:00:00", tz = "UTC")
  pruned_seconds$datetime_converted <- base_time + as.numeric(pruned_seconds[,1])
  pruned_seconds$Datetime <- format(pruned_seconds$datetime_converted, "%Y%m%dT%H%M%SZ")

  # Select the relevant columns
  relevant_data <- pruned_seconds[, c("Datetime", "Temperature", "Depth", "Salinity", "Oxygen.Mg.L")]

  return(as_tibble(relevant_data))
}

read_nav_data <- function() {
  nav_folder_path <- paste0(tmp_input_files,"/nav")
  nav_file_pattern <- paste0(cruise_number, "_", dive_number, ".*", ".csv")
  nav_file <- list.files(nav_folder_path, pattern = nav_file_pattern, full.names = TRUE)
  column_names <- c("DATE", "TIME", "UNIXTIME", "DEPTH", "Alt", "Lat", "Long")

  nav_data <- read_csv(nav_file,
                       col_names = column_names,
                       col_select = c("UNIXTIME", "Alt", "Lat", "Long"),
                       col_types = cols(
                         UNIXTIME = col_datetime(format = "%s"),
                       ),
                       show_col_types = FALSE)

  nav_data$Datetime <- format(nav_data$UNIXTIME, "%Y%m%dT%H%M%SZ") # convert timestamp

  # Select only the rows that don't have NA for Alt, Lat, and Long
  nav_data <- nav_data[complete.cases(nav_data[, c("Alt", "Lat", "Long")]), ]

  # Select the relevant columns
  relevant_data <- nav_data[, c("Datetime", "Alt", "Lat", "Long")]

  return(relevant_data)
}

# Merge filtered tibbles
merged_data <- inner_join(read_ctd_data(), read_nav_data(), by="Datetime")

file_name <- paste0(cruise_number, "_", dive_number, "_", dive_start_date, "_ROVDATA.csv")
output_file_path <- paste0(output_destination_path, "/", file_name)

selected_columns <- c("Lat", "Long", "Depth", "Temperature", "Oxygen.Mg.L", "Salinity", "Datetime", "Alt")  # Specify the columns you want to select
new_header_names <- c('Latitude','Longitude','Depth','Temperature','oxygen_mg_per_l', 'Salinity','Date','Alt')  # Specify the new header names

# Subset the tibble to select the desired columns
selected_data <- merged_data[, selected_columns]

# Rename the selected columns
colnames(selected_data) <- new_header_names

# Write the selected and renamed data to a CSV file
time_write_csv <- write.csv(selected_data, file=output_file_path, row.names = FALSE)

cli_alert_success("Merged files")
