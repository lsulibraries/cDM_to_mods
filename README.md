# How to:

for converting the output of cdm_xporter/scrape_cdm.py into mods format (especially for ingest into Islandora)
  
  1a) Windows:  Check if Anaconda is your default python, by typing in a command prompt: `python`.  It should read `python3 Anaconda ...`.  Then type `exit()` to exit python.
        
  1b) Linux/Mac:  Turn on your python3 virtualenv.  It needs lxml.
 
  2) Have a copy of the Cached_Cdm_files (the output of cdm_xporter/scrape_cdm.py) on your computer.  -this /Cached_Cdm_files needs only metadata.
  
  3) In the command line, navigate into the cDM_to_mods directory.
  
  4) `python convert_to_mods.py {alias} {path/to/Cached_Cdm_files}
        -this /Cached_Cdm_files needs only metadata.
  
  5) `python post_converstion_cleanup.py {alias} {path/to/U_drive/Cached_Cdm_files}`
        -this /Cached_Cdm_files needs metadata+binaries

## Scripts

convert_to_mods.py:
  - applies the cDM_to_mods/mappings_file/{alias}.csv to the Cached_Cdm_files data to create a rough mods file.
  - performs xsl transformations named in the cDM_to_mods/alias_xlsts/{alias}.txt file to refine the mods.
  - attempts to convert dates into the standard format
  - validates each mods record against a local copy of the mods schema.
  - compares the count of xmls to the reported number of items in TotalRecs.xml
  - complains loudly if anything fails.

The xsl scripts are found in the cDM_to_mods/xsl/ folder.
The final output can be found in cDM_to_mods/output/{alias}_simple/final_format and cDM_to_mods/output/{alias}_compound/final_format.  Seperating simples from compounds facilitates easier uploading into Islandora.  

post_conversion_cleanup.py:
  - verifies that each object in the collection was converted into a mod file.  
  - pulls the binaries from the source_directory into the proper position within the output files.
  - complains if there is not a {.jp2, .mp3, .mp4, .pdf} for each mods.
  - creates a structure file, which is necessary for Islandora Compound Batch Upload.  
  - checks all the mods for access restrictions, and reports those to cDM_to_mods/{alias}_restrictions.txt  
