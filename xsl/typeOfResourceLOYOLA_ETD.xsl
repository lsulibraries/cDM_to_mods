<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:mods="http://www.loc.gov/mods/v3"
    xpath-default-namespace="http://www.loc.gov/mods/v3"
    exclude-result-prefixes="xs"
    version="2.0"
    xmlns="http://www.loc.gov/mods/v3">
    
    <!-- fits typeOfResource to authorized terms specifically for loyno-etd collection -->
    
    <xsl:template match="@* | node()">
        <xsl:copy>
            <xsl:apply-templates select="@* | node()"/>
        </xsl:copy>
    </xsl:template>  
    
    <xsl:template match="typeOfResource">
        <xsl:choose>
            <xsl:when test="matches(., 'Interactive Resource;', 'i')">
                <typeOfResource>moving image</typeOfResource>
            </xsl:when>
            <xsl:when test="matches(., 'Image', 'i')">
                <typeOfResource>still image</typeOfResource>
            </xsl:when>
            <xsl:when test="matches(., 'Text', 'i')">
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