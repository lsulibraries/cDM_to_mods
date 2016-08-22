<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:mods="http://www.loc.gov/mods/v3"
    xpath-default-namespace="http://www.loc.gov/mods/v3"
    exclude-result-prefixes="xs"
    version="2.0"
    xmlns="http://www.loc.gov/mods/v3">
    
    <!-- delete physicalDescription/form when values are JPEG200, tiff or tif-->
    
    <xsl:template match="@* | node()">
        <xsl:copy>
            <xsl:apply-templates select="@* | node()"/>
        </xsl:copy>
    </xsl:template>
        
    <xsl:template match="physicalDescription/form">
        <xsl:choose>
            <xsl:when test="matches(., 'JPEG2000')" />
            <xsl:when test="matches(., 'tif')" />
            <xsl:otherwise>
                <form>
                    <xsl:value-of select="."/>
                </form>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
</xsl:stylesheet>