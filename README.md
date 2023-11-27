# Overview 

This repository contains scripts that prepare ROV sensor data for input into VARS. There are currently two scripts, one for data from Deep Discoverer (Nautilus, NA) and one for data from Hercules, (Okeanos Explorer, EX).

## Nautilus

The script to process data from the Nautilus is called `na_ctd_processor.sh`. This is a bash script that takes a cruise number as an argument, e.g.:

```bash
./na_ctd_processor.sh NA138
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
./ex_ctd_processor.sh EX2306
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
- EX `ROVCTD_DERIVE.cnv` files currently use an interesting timestamp: the first column is the number of seconds since 2000-01-01 00:00:00Z. This is converted to a standard timestamp in the R script.
- If the folder structure, file names, or columns in the data files change, the scripts will need to be updated accordingly.

### NA Expected Values

#### Folder structure

```bash
.
└── ${CRUISE_NUMBER}/
    ├── processed/
    │   └── dive_reports/
    │       ├── ${DIVE_NUMBER_1}/
    │       │   └── merged/
    │       │       ├── ${DIVE_NUMBER_1}.CTD.NAV.tsv
    │       │       ├── ${DIVE_NUMBER_1}.O2S.NAV.tsv
    │       │       └── ...
    │       ├── ${DIVE_NUMBER_2}/
    │       │   └── merged/
    │       │       ├── ${DIVE_NUMBER_2}.CTD.NAV.tsv
    │       │       ├── ${DIVE_NUMBER_2}.O2S.NAV.tsv
    │       │       └── ...
    │       └── ...
    └── raw/
        └── nav/
            └── navest/
                ├── YYYYMMDD_HHMM.DAT
                ├── YYYYMMDD_HHMM.DAT
                ├── YYYYMMDD_HHMM.DAT
                └── ...
```

#### File names

**CTD Files (Lat, Long, Depth, Temperature, Salinity)**

Format: `${DIVE_NUMBER}.CTD.NAV.tsv` 

Example: `H1915.CTD.NAV.tsv`

**O2 Files (Oxygen)**

Format: `${DIVE_NUMBER}.O2S.NAV.tsv`

Example: `H1915.O2S.NAV.tsv`

**DAT Files (Altitude)**

Format: `YYYYMMDD_HHMM.DAT`

Example: `20220407_0600.DAT`

#### Column order
`X` indicates a column that is not used.

**CTD.NAV.tsv**
```
Timestamp, Latitude, Longitude, Depth, Temperature, X1, X2, Salinity, X3
```

**O2S.NAV.tsv**
```
Timestamp, X1, X2, X3, Oxygen, X4, X5
```

**.DAT** (Looks for keywords VFR and SOLN_DEADRECK)
```
VFR 2022/04/17 18:00:02.615 13 0 SOLN_DEADRECK -174.606671 30.693783 0.000 2.330 100 0.16 59.80 
```


### EX Expected Values

#### Folder structure

```bash
.
└── ${CRUISE_NUMBER}/
    ├── CTD/
    │   ├── ${DIVE_NUMBER_1}_ROVCTD_DERIVE.cnv
    │   ├── ${DIVE_NUMBER_2}_ROVCTD_DERIVE.cnv
    │   └── ...
    └── Tracking/
        ├── ${DIVE_NUMBER_1}_RovTrack1Hz.csv
        ├── ${DIVE_NUMBER_2}_RovTrack1Hz.csv
        └── ...
```

#### File names

**CTD Files (Temperature, Depth, Salinity, Oxygen)**

Format: `${CRUISE_NUMBER}_${DIVE_NUMBER}_${any other descriptors}.cnv`

Example: `EX2306_DIVE01_20230824_ROVCTD_DERIVE.cnv`

**Tracking Files (Lat, Long, Altitude)**

Format: `${CRUISE_NUMBER}_${DIVE_NUMBER}_${any other descriptors}.csv`

Example: `EX2306_DIVE01_RovTrack1Hz.csv`

#### Column order
`X` indicates a column that is not used.

**CTD**
```
Timestamp, X1, X2, Temperature, X3, X4, X5, X6, X7, Depth, Salinity, X8, OxygenMg/L, X9, X10, X11
```

**Tracking**
```
Date, Time, Unix Time, Depth, Altitude, Lat, Long
```
