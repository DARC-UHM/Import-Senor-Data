#!/bin/bash
#set -x # for debugging

# usage:
# ./ex_ctd_processor.sh <cruise_number> <cruise_source_path> <output_destination_path>

# inputs
cruise_number=$1
cruise_source_path=$2
output_destination_path=$3

# IF COLUMNS IN CTD CNV FILE CHANGE, UPDATE IN EX.R (line 28)
#
# CURRENT CTD CNV FILE COLUMNS (IN THIS ORDER):
#
# Timestamp  (this is currently seconds after 2000-01-01 00:00:00)
# prDM
# prDE
# Temperature
# c0S/m
# seaTurbMtr
# sbeox0V
# upoly0
# modError
# Depth
# Salinity
# svCM
# sbeox0Mg/L
# Oxygen.Mg.L
# sbox0Mm/Kg
# flag

# IF COLUMNS IN NAV CSV FILE CHANGE, UPDATE IN EX.R (line 64)
#
# CURRENT NAV CSV FILE COLUMNS (IN THIS ORDER):
#
# DATE
# TIME
# UNIXTIME
# DEPTH
# Alt
# Lat
# Long

# load pretty colors
export txt_bold=$(tput bold)
export txt_underline=$(tput sgr 0 1)
export txt_blue=${txt_bold}$(tput setaf 4)
export txt_success=${txt_bold}$(tput setaf 2)
export txt_warn=${txt_bold}$(tput setaf 3)
export txt_error=${txt_bold}$(tput setaf 1)
export txt_reset=$(tput sgr0)

# OUTPUT - WRITE
today=$(date +%Y%m%d)
tmp_output_destination="$output_destination_path/$cruise_number/$today/tmp"
mkdir -p "$tmp_output_destination"
cd "EX"

# Given a cruise number, identify the number of dives in the cruise
dive_count=`(ls "$cruise_source_path/CTD" | grep .cnv | wc -l | tr -d " ")`
if((dive_count == 0)); then
  printf "\n${txt_error}No dives found in $cruise_source_path$txt_reset\n\n"
  exit 1
fi

printf "\n${txt_bold}Found $dive_count dives$txt_reset\n"

dives=($(ls "$cruise_source_path/CTD"| grep .cnv))

## iterate through each of the dives
for((i = 0; i < dive_count; ++i)); do
  num=$((i+1))
  dive_number=${dives[i]:7:6}

  printf "\n=============================================\n"
  printf "                    ${txt_bold}${dive_number}${txt_reset}\n"
  printf "                  Dive $num/$dive_count\n"

  # GRAB a COPY of CTD CNV FILES LOCALLY
  ctd_cnv_file=($(ls "$cruise_source_path/CTD" | grep ${cruise_number}_${dive_number}_))
  ctd_cnv_file_path="${cruise_source_path}/CTD/${ctd_cnv_file}"
  if [[ ! -f "$tmp_output_destination/$ctd_cnv_file" ]]; then
    mkdir -p "$tmp_output_destination/ctd" && cp "$ctd_cnv_file_path" "$tmp_output_destination/ctd"
  else
    echo "Skip copying file over: $ctd_cnv_file_path"
  fi

  nav_csv_file=($(ls "$cruise_source_path/Tracking" | grep ${cruise_number}_${dive_number}_))
  nav_csv_file_path="${cruise_source_path}/Tracking/${nav_csv_file}"
  if [[ ! -f "$tmp_output_destination/$nav_csv_file_path" ]]; then
    mkdir -p "$tmp_output_destination/nav" && cp "$nav_csv_file_path" "$tmp_output_destination/nav"
  else
    echo "Skip copying file over: $nav_csv_file_path"
  fi

  # GRAB the START DATE of a DIVE
  dive_start_year=$(grep -m 1 "start_time" $ctd_cnv_file_path | awk '{print $6}')
  dive_start_month=$(grep -m 1 "start_time" $ctd_cnv_file_path | awk '{print $4}')
  dive_start_day=$(grep -m 1 "start_time" $ctd_cnv_file_path | awk '{print $5}')
  # convert the month from text to number
  case $dive_start_month in
    Jan) dive_start_month=01;;
    Feb) dive_start_month=02;;
    Mar) dive_start_month=03;;
    Apr) dive_start_month=04;;
    May) dive_start_month=05;;
    Jun) dive_start_month=06;;
    Jul) dive_start_month=07;;
    Aug) dive_start_month=08;;
    Sep) dive_start_month=09;;
    Oct) dive_start_month=10;;
    Nov) dive_start_month=11;;
    Dec) dive_start_month=12;;
  esac
  dive_start_date="${dive_start_year}${dive_start_month}${dive_start_day}"

  # run R script
  printf "\nMerging data...\r"
  Rscript EX.R "$cruise_number" "$dive_number" "$dive_start_date" "$tmp_output_destination" "$output_destination_path" #--vanilla --profile

done

# CLEANUP
printf "\nRemoving temp files...\n"
rm -rf "$output_destination_path/$cruise_number"

printf "$txt_success\nCruise complete!\n$txt_reset"
printf "\nMerged csv files saved to ${txt_underline}${output_destination_path}${txt_reset}\n\n"

open "$output_destination_path"

exit 0
