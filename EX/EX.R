# options(error=traceback)
# install.packages("tidyverse")
# install.packages("jsonlite")
suppressPackageStartupMessages(library(tidyverse))
library(readr)
library(dplyr)
library(purrr)
suppressPackageStartupMessages(library(jsonlite))
library(cli)

#  Rscript EX.R "$config_file" "$dive_number" "$dive_start_date" "$tmp_output_destination"

#  Access the arguments
args <- commandArgs(trailingOnly = TRUE)
config_file_path <- args[1]
dive_number <- args[2]
dive_start_date <- args[3]
tmp_output_dest <- args[4]

config_data <- fromJSON(config_file_path)

read_ctd_data <- function() {
  ctd_folder_path <- paste0(tmp_output_dest, "/ctd")
  ctd_file_pattern <- paste0(config_data$cruise_number, "_", dive_number, ".*", ".cnv")
  ctd_file <- list.files(ctd_folder_path, pattern = ctd_file_pattern, full.names = TRUE)

  column_names <- c("1", "2", "3", "4", "5", "6", "7", "8",
                    "9", "10", "11", "12", "13", "14", "15", "16")

  column_names[as.integer(config_data$ctd_cols$timestamp)] <- "Timestamp"
  column_names[as.integer(config_data$ctd_cols$temperature)] <- "Temperature"
  column_names[as.integer(config_data$ctd_cols$depth)] <- "Depth"
  column_names[as.integer(config_data$ctd_cols$salinity)] <- "Salinity"
  column_names[as.integer(config_data$ctd_cols$oxygen)] <- "Oxygen.ML.L"

  file_conn <- file(ctd_file, open="r")
  line_count <- 0

  system_start_time <- NULL

  # grab the system start time, then read thorough file until "*END*" is found
  while (TRUE) {
      line <- readLines(file_conn, n = 1)
      line_count <- line_count + 1
      if (grepl("* System UTC = ", line)) {
          raw_start_time <- strsplit(line, " = ")[[1]][2]
          system_start_time <- as.POSIXct(raw_start_time, format = "%b %d %Y %H:%M:%S", tz = "UTC")
      }
      if (grepl("*END*", line)) {
          break
      }
  }
  close(file_conn)

  # Read and combine the files into a table
  all_ctd_data <- read.table(ctd_file, skip = line_count, header = FALSE, col.names = column_names)
  pruned_seconds <- all_ctd_data[!duplicated(all_ctd_data[, 1]), ]  # Only grab one row for each second

  # convert timestamp
  seconds_from <- config_data$ctd_seconds_from
  if (seconds_from == "2000") {
    base_time <- as.POSIXct("2000-01-01 00:00:00", tz = "UTC")
  } else if (seconds_from == "UNIX") {
    base_time <- as.POSIXct("1970-01-01 00:00:00", tz = "UTC")
  } else if (seconds_from == "ELAPSED") {
    if (system_start_time == NULL) {
      stop("System start time not found")
    }
    base_time <- system_start_time
  } else {
    stop("Invalid ctd_seconds_from value")
  }
  pruned_seconds$datetime_converted <- base_time + as.numeric(pruned_seconds[,1])
  pruned_seconds$Datetime <- format(pruned_seconds$datetime_converted, "%Y%m%dT%H%M%SZ")

  # Select the relevant columns
  relevant_data <- pruned_seconds[, c("Datetime", "Temperature", "Depth", "Salinity", "Oxygen.ML.L")]

  return(as_tibble(relevant_data))
}

read_nav_data <- function() {
  nav_folder_path <- paste0(tmp_output_dest, "/nav")
  nav_file_pattern <- paste0(config_data$cruise_number, "_", dive_number, ".*", ".csv")
  nav_file <- list.files(nav_folder_path, pattern = nav_file_pattern, full.names = TRUE)
  column_names <- c("1", "2", "3", "4", "5", "6", "7")

  column_names[as.integer(config_data$tracking_cols$unix_time)] <- "UNIXTIME"
  column_names[as.integer(config_data$tracking_cols$altitude)] <- "Alt"
  column_names[as.integer(config_data$tracking_cols$latitude)] <- "Lat"
  column_names[as.integer(config_data$tracking_cols$longitude)] <- "Long"

  nav_data <- read_csv(nav_file,
                       col_names = column_names,
                       col_select = c("UNIXTIME", "Alt", "Lat", "Long"),
                       col_types = cols(
                         UNIXTIME = col_datetime(format = "%s"),
                       ),
                       show_col_types = FALSE)

  nav_data$Datetime <- format(nav_data$UNIXTIME, "%Y%m%dT%H%M%SZ") # convert timestamp

  # Select only the rows that don't have NA for Alt, Lat, and Long
  nav_data <- nav_data[complete.cases(nav_data[, c("Lat", "Long")]), ]

  # Select the relevant columns
  relevant_data <- nav_data[, c("Datetime", "Alt", "Lat", "Long")]

  return(relevant_data)
}

# Merge filtered tibbles
merged_data <- inner_join(read_ctd_data(), read_nav_data(), by="Datetime")

file_name <- paste0(config_data$cruise_number, "_", dive_number, "_", dive_start_date, "_ROVDATA.csv")
output_file_path <- paste0(config_data$output_dir, "/", file_name)

selected_columns <- c("Lat", "Long", "Depth", "Temperature", "Oxygen.ML.L", "Salinity", "Datetime", "Alt")  # Specify the columns you want to select
new_header_names <- c('Latitude','Longitude','Depth','Temperature','oxygen_ml_per_l', 'Salinity','Date','Alt')  # Specify the new header names

# Subset the tibble to select the desired columns
selected_data <- merged_data[, selected_columns]

# Rename the selected columns
colnames(selected_data) <- new_header_names

# Write the selected and renamed data to a CSV file
time_write_csv <- write.csv(selected_data, file=output_file_path, row.names = FALSE)

cli_alert_success("Merged files")
