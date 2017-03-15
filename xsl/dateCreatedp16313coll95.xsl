<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:mods="http://www.loc.gov/mods/v3"
    xpath-default-namespace="http://www.loc.gov/mods/v3"
    exclude-result-prefixes="xs"
    version="2.0"
    xmlns="http://www.loc.gov/mods/v3">
    
    <!-- dateCreated transforms specifically for p16313coll95 collection, splits comma delimited date values into start and end points -->
    
    <xsl:template match="@* | node()">
        <xsl:copy>
            <xsl:apply-templates select="@* | node()"/>
        </xsl:copy>
    </xsl:template>
    

    <xsl:variable name="commaRegEx" select="'(^[0-9]{4}\-[0-9]{2}\-[0-9]{2}),.*([0-9]{4}\-[0-9]{2}\-[0-9]{2}$)'"/> <!-- YYYY-MM-DD, YYYY-MM-DD -->
    <xsl:template match="originInfo/dateCreated">
        <xsl:choose>
            
           <xsl:when test="matches(., $commaRegEx)">
                <xsl:analyze-string select="." regex="{$commaRegEx}">
                    <xsl:matching-substring>
                        <dateCreated keyDate="yes" point="start">
                            <xsl:value-of select="replace(regex-group(1), '\s+', ' ')"/>
                        </dateCreated>
                        <dateCreated point="end">
                            <xsl:value-of select="replace(regex-group(2), '\s+', ' ')"/>
                        </dateCreated>
                    </xsl:matching-substring>
                </xsl:analyze-string>
            </xsl:when>
            
            <xsl:otherwise>
                <dateCreated keyDate="yes">
                    <xsl:value-of select="."/>
                </dateCreated>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
</xsl:stylesheet>