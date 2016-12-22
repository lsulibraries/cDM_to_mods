# How to:

for converting the output of cdm_xporter/scrape_cdm.py into mods format (especially for ingest into Islandora)
  
  1a) Windows:  Check if Anaconda is your default python, by typing in a command prompt: `python --version`.  It should read `python3 Anaconda ...`.  Install dependencies, using Powershell as an Administrator, `pip install py-trello`
        
  1b) Linux/Mac:  Turn on your python3 virtualenv.  It needs lxml.  Also run in you virtualenv `pip install py-trello`.
 
  2) Have the folder Cached_Cdm_files (the output of cdm_xporter/scrape_cdm.py) on your computer (or network).
  
  3) In the command line, navigate into the cDM_to_mods directory.
  
  4) Have a file `trello_keys.json` in this cDM_to_mods folder.  This file is not synced to git for security reasons.  The contents of this file is `{"api_key":"something","api_secret":"something","token":"something"}` where your api_key, etc are found from https://trello.com/app-key .
  
  4) `python convert_to_mods.py {alias} {path/to/Cached_Cdm_files}`
        -this /Cached_Cdm_files needs only metadata.
  
  5) `python post_converstion_cleanup.py {alias} {path/to/U_drive/Cached_Cdm_files}`
        -this /Cached_Cdm_files needs metadata+binaries

## Scripts

convert_to_mods.py:
  - applies the cDM_to_mods/mappings_file/{alias}.csv to the Cached_Cdm_files data to create a rough mods file.
  - performs xsl transformations named in the cDM_to_mods/alias_xlsts/{alias}.txt file to refine the mods.
  - attempts to convert dates into the standard format
  - validates each mods record against the mods schema at loc.gov.
  - compares the count of xmls to the reported number of items in TotalRecs.xml
  - complains loudly if anything fails.

The xsl scripts are found in the cDM_to_mods/xsl/ folder.
The final output can be found in cDM_to_mods/output/{alias}_simple/final_format and cDM_to_mods/output/{alias}_compound/final_format.  Seperating simples from compounds facilitates easier uploading into Islandora.  

post_conversion_cleanup.py:
  - verifies that each object in the collection was converted into a mod file.  
  - pulls the binaries from the source_directory into the proper position within the output files.
  - complains if there is not exactly one {.jp2, .mp3, .mp4, .pdf} for each mods.
  - creates a structure file, which is necessary for Islandora Compound Batch Upload.  
  - checks all the mods for access restrictions, and reports those to cDM_to_mods/{alias}\_restrictions.txt  
  - packages the items into zips as required by Islandora Batch importer
  - moves the zip files to the shared network drive (U/Upload_to_Islandora)
  - posts the log onto the matching Trello card & moves the card to the column 'Whole Collection Packaged at U'
