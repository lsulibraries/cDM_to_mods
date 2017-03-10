<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:mods="http://www.loc.gov/mods/v3"
    xpath-default-namespace="http://www.loc.gov/mods/v3"
    exclude-result-prefixes="xs"
    version="2.0"
    xmlns="http://www.loc.gov/mods/v3">
    
    <!-- reformats non parsing dates of digitization formatted as YYYY-YYYY -->
    
    <xsl:template match="@* | node()">
        <xsl:copy>
            <xsl:apply-templates select="@* | node()"/>
        </xsl:copy>
    </xsl:template>

    <xsl:variable name="yearRangeRegEx" select="'([0-9]{4})\s?-\s?([0-9]{4})'"/> <!-- YYYY-YYYY -->

    <xsl:template match="originInfo/dateCaptured">
        <xsl:choose>
            <xsl:when test="matches(., $yearRangeRegEx)">
                <xsl:analyze-string select="." regex="{$yearRangeRegEx}">
                    <xsl:matching-substring>
                        <dateCaptured point="start">
                            <xsl:value-of select="replace(regex-group(1), '\s+', ' ')"/>
                        </dateCaptured>
                        <dateCaptured point="end">
                            <xsl:value-of select="replace(regex-group(2), '\s+', ' ')"/>
                        </dateCaptured>
                    </xsl:matching-substring>
                </xsl:analyze-string>
            </xsl:when>
            <xsl:otherwise>
                <dateCaptured>
                    <xsl:value-of select="."/>
                </dateCaptured>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
    
</xsl:stylesheet>