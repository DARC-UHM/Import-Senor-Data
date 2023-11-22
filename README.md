# Overview 

This repository contains scripts that prepare ROV sensor data for input into VARS. There are currently two scripts, one for data from Deep Discoverer (Nautilus, NA) and one for data from Hercules, (Okeanos Explorer, EX).

## Nautilus

The script to process data from the Nautilus is called `na_ctd_processor.sh`. This is a bash script that takes a cruise number as an argument, e.g.:

```bash
na_ctd_processor.sh NA138
```

Before running this script, file paths must be specified on lines 10-12 of the script:

```bash
### CONFIGURATION ###
cruise_source_path="/Volumes/maxarray2/varsadditional/$cruise_number"
dive_reports_source="/Volumes/maxarray2/varsadditional/$cruise_number/processed/dive_reports"
output_destination_path="/Users/darc/Desktop/test"
```

`$cruise_number` is the cruise number passed as an argument to the script, so this does not need to be manually changed. The `cruise_source_path` is the path to the cruise directory on the server. The `dive_reports_source` is the path to the `dive_reports` directory on the server (defined separately in case the location of the `dive_reports` folder changes in the future). The `output_destination_path` is the path to the directory where the processed data will be saved.

The script starts by finding a list of all the dives in the cruise. For each dive, it copies the relevant data files to a temporary directory at the output destination path. These include `.CTD.NAV.tsv` files (lat/long, depth, temperature, and salinity) and `.O2S.NAV.tsv` files (oxygen).

Next, the script calls `extract_DAT.sh` to extract altitude data and timestamps from the `.DAT` files. This script finds the `.DAT` files in the source directory that coincide with the start and end times of the dive, extracts the altitude/timestamps from these files, and saves a merged `.DAT` file for the dive in the temporary directory.

The script then calls `NA.R` to merge the three file types into a single formatted `.tsv` file that is saved in the output destination path. This file is then ready to be uploaded to VARS.

Finally, the script deletes the temporary directory.

## Okeanos Explorer

The script to process data from the Okeanos Explorer is called `ex_ctd_processor.sh`. Like the NA script, this is a bash script that takes a cruise number as an argument, e.g.:

```bash
ex_ctd_processor.sh EX2306
```

Before running this script, file paths must be specified on lines 7-9 of the script:

```bash
### CONFIGURATION ###
cruise_source_path="/Volumes/maxarray2/varsadditional/OER2023/$cruise_number"
output_destination_path="/Users/darc/Desktop/test"
```

`$cruise_number` is the cruise number passed as an argument to the script, so this does not need to be manually changed. The `cruise_source_path` is the path to the cruise directory on the server. The `output_destination_path` is the path to the directory where the processed data will be saved. Unlike the NA script, there is no need to specify a path to the `dive_reports` directory. The script expects two directories in the cruise directory: `CTD` and `Tracking`.

Similar to the NA script, the script starts by finding a list of all the dives in the cruise. For each dive, it copies the relevant data files to a temporary directory at the output destination path. For NA, these include `ROVCTD_DERIVE.cnv` files (depth, temperature, oxygen, and salinity) and `RovTrack1Hz.csv` files (lat/long and altitude).

The script then calls `EX.R` to merge the two files into a single formatted `.tsv` file that is saved in the output destination path. This file is then ready to be uploaded to VARS.

Finally, the script deletes the temporary directory.

## Notes

- The scripts are currently set up to run on a Mac. They may need to be modified to run on a PC.
- If the folder structure, file names, or columns in the data files change, the scripts will need to be updated accordingly.
- EX `ROVCTD_DERIVE.cnv` files currently use an interesting timestamp: the first column is the number of seconds since 2000-01-01 00:00:00Z. This is converted to a standard timestamp in the R script.

[//]: # (TODO add notes about expected file structure, file names, and column names)