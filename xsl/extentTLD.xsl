<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
      xmlns:xs="http://www.w3.org/2001/XMLSchema"
      xmlns:mods="http://www.loc.gov/mods/v3"
      xpath-default-namespace="http://www.loc.gov/mods/v3"
      exclude-result-prefixes="xs"
      version="2.0"
      xmlns="http://www.loc.gov/mods/v3">
    
    <!-- removes all content except that following second semicolon 
        in physicalDescription/extent, specifically for lsu-tld -->
    
    <xsl:template match="@* | node()">
        <xsl:copy>
            <xsl:apply-templates select="@* | node()"/>
        </xsl:copy>
    </xsl:template>
    
    <xsl:variable name="extentText" select="node()/physicalDescription/extent/text()"/>
    <xsl:variable name="myRegEx" select="'([0-9a-zA-Z\s,]+);\s?([0-9a-zA-Z\s,]+);\s?([0-9\sa-zA-Z.&quot;]+)'"/>
    
    <xsl:template match="physicalDescription">
        <xsl:copy>
            <xsl:analyze-string select="$extentText" regex="{$myRegEx}">
                <xsl:matching-substring>
                    <xsl:element name="extent">
                        <xsl:value-of select="replace(regex-group(3), '\s+', ' ')"/>
                    </xsl:element>
                    <internetMediaType>jp2</internetMediaType>
                </xsl:matching-substring>
            </xsl:analyze-string>
        </xsl:copy>
    </xsl:template>
</xsl:stylesheet>