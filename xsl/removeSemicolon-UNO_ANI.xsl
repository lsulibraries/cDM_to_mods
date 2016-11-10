<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:mods="http://www.loc.gov/mods/v3"
    xpath-default-namespace="http://www.loc.gov/mods/v3"
    exclude-result-prefixes="xs"
    version="2.0"
    xmlns="http://www.loc.gov/mods/v3" >
    
    <!-- Removes the semicolon from namePart, dateIssued, and recordCreationDate if it's the last character -->
    
    <xsl:template match="@* | node()">
        <xsl:copy>
            <xsl:apply-templates select="@* | node()"/>
        </xsl:copy>
    </xsl:template>
    
    <xsl:template match="dateIssued[substring(., string-length()) = ';']">
        <dateIssued keydate="yes">
        <xsl:value-of select="substring(., 1, string-length(.) -1)"/> 
        </dateIssued>
    </xsl:template>
    
    <xsl:template match="recordCreationDate[substring(., string-length()) = ';']">
        <recordCreationDate>
            <xsl:value-of select="substring(., 1, string-length(.) -1)"/> 
        </recordCreationDate>
    </xsl:template>
    
    <xsl:template match="namePart[substring(., string-length()) = ';']">
        <namePart>
            <xsl:value-of select="substring(., 1, string-length(.) -1)"/> 
        </namePart>
    </xsl:template>

</xsl:stylesheet>