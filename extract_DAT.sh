#!/bin/sh

dive_number=$1
cruise_source_path=$2
tmp_folder=$3
output_destination_path=$4

function ProgressBar {
    let _progress=(${1}*100/${2}*100)/100
    let _done=(${_progress}*4)/10
    let _left=40-$_done
    _fill=$(printf "%${_done}s")
    _empty=$(printf "%${_left}s")

printf "\rExtracting DAT files...\n"
printf "${txt_blue}[${_fill// /#}${_empty// /-}] ${_progress}%%${txt_reset}\033[A\033[K"

}

if (( $# != 4 )); then
  echo "Illegal number of parameters"
  echo "Usage: ./extract_DAT.sh <dive_number> <cruise_source_path> <tmp_folder> <output_destination_path>"
  exit 1
fi
if [ ! -d "$cruise_source_path" ]; then
  printf "${txt_error}\nERROR: $cruise_source_path does not exist${txt_reset}\n"
  exit 1
fi
if [ ! -d "$tmp_folder" ]; then
  printf "${txt_error}\nERROR: $tmp_folder does not exist\n"
  exit 1
fi

dat_path="$cruise_source_path/raw/nav/navest"
dat_files="${tmp_folder}/DAT_files.txt"

if file "${dat_path}" | grep -q empty; then
  printf "${txt_error}\nERROR: No DAT files found in ${dat_path}${txt_reset}\n"
  exit 1
else
  find ${dat_path} -name "*.DAT" > ${dat_files}
fi
ctd_nav_tsv="$tmp_folder/ctd_nav/$dive_number.CTD.NAV.tsv"
o2s_nav_tsv="$tmp_folder/o2s_nav/$dive_number.O2S.NAV.tsv"

if [ ! -f "$ctd_nav_tsv" ]; then
  printf "${txt_error}\nERROR: $ctd_nav_tsv does not exist\n"
  exit 1
fi
if [ ! -f "$o2s_nav_tsv" ]; then
  printf "${txt_error}\nERROR: $o2s_nav_tsv does not exist\n"
  exit 1
fi
CTD_NAV_start_dive_time=$(head -1 "$ctd_nav_tsv" | cut -f1 -s)  #2019-08-30T06:45:17
O2S_NAV_start_dive_time=$(head -1 "$o2s_nav_tsv" | cut -f1 -s)  #2019-08-30T06:45:19

tmp_file="${tmp_folder}/${dive_number}_processed.DAT"
mkdir -p "${tmp_folder}/dat"
output_file="${tmp_folder}/dat/${dive_number}.DAT"

# check if CTD.NAV file is empty
if [ ! -s "$ctd_nav_tsv" ]; then
  printf "${txt_error}\nERROR: $ctd_nav_tsv is empty${txt_reset}\n"
  exit 1
fi

# check if O2S.NAV file is empty
if [ ! -s "$o2s_nav_tsv" ]; then
  printf "${txt_error}\nERROR: $o2s_nav_tsv is empty${txt_reset}\n"
  exit 1
fi

# Lexicographic (greater than, less than) comparison.
if [ "$CTD_NAV_start_dive_time" \< "$O2S_NAV_start_dive_time" ]; then
  start_dive_time=$CTD_NAV_start_dive_time
elif [ "$O2S_NAV_start_dive_time" \> "$CTD_NAV_start_dive_time" ]; then
  start_dive_time=$O2S_NAV_start_dive_time
else
  start_dive_time=$CTD_NAV_start_dive_time
fi
if [ "$start_dive_time" == "" ]; then
  printf "${txt_error}\nERROR: No start dive time found\n"
  exit 1
fi

CTD_NAV_end_dive_time=$(tail -1 "$ctd_nav_tsv" | cut -f1 -s) # 2019-08-31T06:43:44
O2S_NAV_end_dive_time=$(tail -1 "$o2s_nav_tsv" | cut -f1 -s) # 2019-08-31T06:43:44
# Lexicographic (greater than, less than) comparison.
if [ "$CTD_NAV_end_dive_time" \< "$O2S_NAV_end_dive_time" ]; then
  end_dive_time=$CTD_NAV_end_dive_time
elif [ "$CTD_NAV_end_dive_time" \> "$O2S_NAV_end_dive_time" ]; then
  end_dive_time=$CTD_NAV_end_dive_time
else
  end_dive_time=$CTD_NAV_end_dive_time
fi
if [ "$end_dive_time" == "" ]; then
  printf "${txt_error}\nERROR: No end dive time found in $ctd_nav_tsv or $o2s_nav_tsv\n"
  exit 1
fi

start_dive_unix_timestamp=$(date -j -f "%Y-%m-%dT%H:%M:%S" "$start_dive_time" "+%s")
start_dive_datetime_slash_formatted=$(date -j -f "%Y-%m-%dT%H:%M:%S" $start_dive_time "+%Y/%m/%d %H:%M:%S")
day_before_start_dive_unix_timestamp=$(date -j -v-1d -f "%Y-%m-%dT%H:%M:%S" "$start_dive_time" "+%s")

end_dive_unix_timestamp=$(date -j -f "%Y-%m-%dT%H:%M:%S" $end_dive_time "+%s")
end_dive_datetime_slash_formatted=$(date -j -f "%Y-%m-%dT%H:%M:%S" $end_dive_time "+%Y/%m/%d %H:%M:%S") #2019/08/31 06:43:44

matching_timestamps=()

format="%Y%m%d_%H%M.DAT"
while IFS= read -r line; do
  file_name=$(basename "$line")

	dat_file_unix_timestamp=$(date -j -f $format "$file_name" "+%s")

  if [[ $dat_file_unix_timestamp -ge $day_before_start_dive_unix_timestamp  && $dat_file_unix_timestamp -le $end_dive_unix_timestamp  ]]; then
    matching_timestamps+=($line)
  fi

done < "$dat_files"

# Sort the array in ascending order
sorted_array=($(printf '%s\n' "${matching_timestamps[@]}" | sort -n))
array_length="${#sorted_array[@]}"
i=0

#deduplicate ms timestamps
for line in "${sorted_array[@]}"; do
  ProgressBar $((++i)) $array_length
  search_string="VFR.*SOLN_DEADRECK.*"
  ag --nonumbers "${search_string}" $line | awk -F ' ' '{print $2, $3, $10}' | awk -F"." '!seen[$1]++' >> "${output_file}"
done

printf "\r\033[K${txt_success}✔${txt_reset} Extracted DAT files.\n\033[K\r"
