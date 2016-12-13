<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:mods="http://www.loc.gov/mods/v3"
    xpath-default-namespace="http://www.loc.gov/mods/v3"
    exclude-result-prefixes="xs"
    version="2.0"
    xmlns="http://www.loc.gov/mods/v3">
    
    <!-- splits typeOfResource "Image; Sound; Text" into separate typeOfResource still image, sound recording-nonmusical, and text lines, specific for StoryCorps collection-->
    
    <xsl:template match="@* | node()">
        <xsl:copy>
            <xsl:apply-templates select="@* | node()"/>
        </xsl:copy>
    </xsl:template>
    
    <xsl:template match="typeOfResource">
        <xsl:choose>
            <xsl:when test="matches(., 'Image; Sound; Text', 'i')">
                <typeOfResource>still image</typeOfResource>
                <typeOfResource>sound recording-nonmusical</typeOfResource>
                <typeOfResource>text</typeOfResource>
            </xsl:when>
            <xsl:otherwise>
                <typeOfResource>
                    <xsl:value-of select="."/>
                </typeOfResource>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
    
</xsl:stylesheet>