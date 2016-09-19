# cDM_to_mods
for converting the output of cdm_xporter into mods format (especially for inject into Islandora)

1)  Turn on your python3 virtualenv.  It needs lxml.  Ananconda works well.

2)  The source material, Cached_Cdm_files, must be in a sibling folder to the cDM_to_mods folder.

3)  In the command line, navigate to the cDM_to_mods directory.

4)  `python convert_to_mods.py $alias`

5)  If all goes well, `python post_converstion_cleanup.py $alias`

convert_to_mods.py applies the cDM_to_mods/mappings_file/{alias}.csv to the DublinCore source data, to create a rough mods file.  It the performs xsl transformations named in the cDM_to_mods/alias_xlsts/{alias}.txt file.  The xsl are found in the cDM_to_mods/xsl/ folder.  The final output can be found in cDM_to_mods/output/{alias}_simple/final_format and cDM_to_mods/output/{alias}_compound/final_format.  Seperating simples from compounds facilitates easier uploading into Islandora.  

post_conversion_cleanup.py verifies that all of the objects in the collection were converted into mods files.  It then pulls the binaries from the source_directory into the proper position within the output files.  It then creates a structure file that is necessary for Islandora Batch Upload.  Finally, it checks all the mods for Access Restrictions, and reports those.  Access Restrictions are saved in cDM_to_mods/{}_restrictions.txt  Other information is logged to screen & a seperate log file.
