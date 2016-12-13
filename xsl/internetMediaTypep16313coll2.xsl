<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
      xmlns:xs="http://www.w3.org/2001/XMLSchema"
      xmlns:mods="http://www.loc.gov/mods/v3"
      xpath-default-namespace="http://www.loc.gov/mods/v3"
      exclude-result-prefixes="xs"
      version="2.0"
      xmlns="http://www.loc.gov/mods/v3">
    
    <!-- splits internetMediaType "JPEG; MP3; PDF" into separate internetMediaType jp2, mp3, and pdf lines, specific for StoryCorps collection-->
    
    <xsl:template match="@* | node()">
        <xsl:copy>
            <xsl:apply-templates select="@* | node()"/>
        </xsl:copy>
    </xsl:template>
    
    <xsl:template match="physicalDescription/internetMediaType">
        <xsl:choose>
            <xsl:when test="matches(., 'JPEG; MP3; PDF', 'i')">
                <internetMediaType>jp2</internetMediaType>
                <internetMediaType>mp3</internetMediaType>
                <internetMediaType>pdf</internetMediaType>
            </xsl:when>
            <xsl:otherwise>
                <internetMediaType>
                    <xsl:value-of select="."/>
                </internetMediaType>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>

</xsl:stylesheet>