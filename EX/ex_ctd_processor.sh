#!/bin/bash
#set -x # for debugging

# brew install ag (ag is the_silver_searcher, faster than grep)
# brew install jq (for reading json config file)

# usage:
# ./ex_ctd_processor.sh <config file path>

config_file=$1

# load pretty colors
txt_bold=$(tput bold)
txt_underline=$(tput sgr 0 1)
txt_success=${txt_bold}$(tput setaf 2)
txt_error=${txt_bold}$(tput setaf 1)
txt_reset=$(tput sgr0)

read_json() {
    local json_file="$1"
    local key="$2"
    jq -r ".$key" "$json_file"
}

# load values from config file
cruise_number=$(read_json "$config_file" "cruise_number")
base_dir=$(read_json "$config_file" "base_dir")
output_dir=$(read_json "$config_file" "output_dir")
temp_ctd_dir=$(read_json "$config_file" "ctd_dir")
temp_tracking_dir=$(read_json "$config_file" "tracking_dir")
temp_ctd_file_names=$(read_json "$config_file" "ctd_file_names")
temp_tracking_file_names=$(read_json "$config_file" "tracking_file_names")

ctd_dir="$(eval echo "$temp_ctd_dir")"
tracking_dir="$(eval echo "$temp_tracking_dir")"

# OUTPUT - WRITE
today=$(date +%Y%m%d)
tmp_output_destination="$output_dir/$cruise_number/$today/tmp"
mkdir -p "$tmp_output_destination"
cd "EX" || exit 1

# Given a cruise number, identify the number of dives in the cruise
dive_count=`(ls "$ctd_dir" | grep "$cruise_number" | wc -l | tr -d " ")`
if((dive_count == 0)); then
  printf "\n${txt_error}No dives matching cruise number $cruise_number found in $base_dir$txt_reset\n\n"
  exit 1
fi

printf "\n${txt_bold}Found $dive_count dives$txt_reset\n"

dives=($(ls "$ctd_dir"| grep .cnv))

## iterate through each of the dives
for((i = 0; i < dive_count; ++i)); do
  num=$((i+1))
  dive=${dives[i]:7:6}
  ctd_file_names="$(eval echo "$temp_ctd_file_names")"
  tracking_file_names="$(eval echo "$temp_tracking_file_names")"

  printf "\n=============================================\n"
  printf "                    ${txt_bold}${dive}${txt_reset}\n"
  printf "                  Dive $num/$dive_count\n"

  # GRAB a COPY of CTD CNV FILES LOCALLY
  ctd_cnv_file=($(ls "$ctd_dir" | grep "$ctd_file_names"))
  ctd_cnv_file_path="${ctd_dir}/${ctd_cnv_file[0]}"  # only expect one file per dive
  if [[ ! -f "$tmp_output_destination/${ctd_cnv_file[0]}" ]]; then
    mkdir -p "$tmp_output_destination/ctd" && cp "$ctd_cnv_file_path" "$tmp_output_destination/ctd"
  else
    echo "Skip copying file over: $ctd_cnv_file_path"
  fi

  nav_csv_file=($(ls "$tracking_dir" | grep "$tracking_file_names"))
  nav_csv_file_path="${tracking_dir}/${nav_csv_file[0]}"  # only expect one file per dive
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
  Rscript EX.R "$config_file" "$dive" "$dive_start_date" "$tmp_output_destination"

done

# CLEANUP
printf "\nRemoving temp files...\n"
rm -rf "${output_dir:?}/${cruise_number:?}"

printf "$txt_success\nCruise complete!\n$txt_reset"
printf "\nMerged csv files saved to ${txt_underline}${output_dir}${txt_reset}\n\n"

open "$output_dir"

exit 0
