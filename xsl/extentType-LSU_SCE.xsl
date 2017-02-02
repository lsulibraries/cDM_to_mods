<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
      xmlns:xs="http://www.w3.org/2001/XMLSchema"
      xmlns:mods="http://www.loc.gov/mods/v3"
      xpath-default-namespace="http://www.loc.gov/mods/v3"
      exclude-result-prefixes="xs"
      version="2.0"
      xmlns="http://www.loc.gov/mods/v3">
    
    <!-- if value is image, photograph, or text, put into typeofresource and translate as appropriate; 
        otherwise value should be medium note -->
    
    <xsl:template match="@* | node()">
        <xsl:copy>
            <xsl:apply-templates select="@* | node()"/>
        </xsl:copy>
    </xsl:template>
    
    <xsl:template match="physicalDescription/note[@type='medium']">
        <xsl:choose>
            <xsl:when test="matches(., 'Image')">
                <typeOfResource>still image</typeOfResource>
            </xsl:when>
            <xsl:when test="matches(., 'Photograph')">
                <typeOfResource>still image</typeOfResource>
            </xsl:when>
            <xsl:when test="matches(., 'Text')">
                <typeOfResource>text</typeOfResource>
            </xsl:when>
            <xsl:otherwise>
                <physicalDescription>
                    <note type='medium'>
                        <xsl:value-of select="."/>
                    </note>
                </physicalDescription>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>

 </xsl:stylesheet>