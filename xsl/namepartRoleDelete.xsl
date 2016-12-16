<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:mods="http://www.loc.gov/mods/v3"
    xpath-default-namespace="http://www.loc.gov/mods/v3"
    exclude-result-prefixes="xs"
    version="2.0"
    xmlns="http://www.loc.gov/mods/v3" >
    
    <!-- remove role term following comma when it is part of namePart
    for SartainEngravings -->
    
    <xsl:template match="@* | node()">
        <xsl:copy>
            <xsl:apply-templates select="@* | node()"/>
        </xsl:copy>
    </xsl:template>
    
    <xsl:variable name="targetText" select="node()/name[@displayLabel='Engraver']/namePart/text()"/>
    <xsl:variable name="myRegEx" select="'([0-9a-zA-Z\s.&amp;]+),\s([0-9\sa-zA-Z]+)'"/>
    
    <xsl:template match="name[@displayLabel='Engraver']/namePart">
        <xsl:copy>
        <xsl:analyze-string select="$targetText" regex="{$myRegEx}">
            <xsl:matching-substring>
                <xsl:value-of select="regex-group(1)"/>
            </xsl:matching-substring>
        </xsl:analyze-string>
        </xsl:copy>            
    </xsl:template>
  
</xsl:stylesheet>