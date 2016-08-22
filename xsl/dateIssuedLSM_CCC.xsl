<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:mods="http://www.loc.gov/mods/v3"
    xpath-default-namespace="http://www.loc.gov/mods/v3"
    exclude-result-prefixes="xs"
    version="2.0"
    xmlns="http://www.loc.gov/mods/v3">
    
    <!-- dateIssued transforms specifically for LSM_CCC collection -->
    
    <xsl:template match="@* | node()">
        <xsl:copy>
            <xsl:apply-templates select="@* | node()"/>
        </xsl:copy>
    </xsl:template>
    

    <xsl:variable name="yearForYearRegEx" select="'([0-9]{4})\s\(for\s([0-9]{4})'"/>
    <xsl:variable name="caRangeRegEx" select="'[cC]a.\s?([0-9]{2})([0-9]{2})-([0-9]{2})'"/> <!-- [Ca. YYYYs] or Ca. YYYYs or Ca. YYY- -->
    <xsl:template match="originInfo/dateIssued">
        <xsl:choose>
            
            <xsl:when test="matches(., $yearForYearRegEx)">
                <xsl:analyze-string select="." regex="{$yearForYearRegEx}">
                    <xsl:matching-substring>
                        <dateCreated>
                            <xsl:value-of select="replace(regex-group(1), '\s+', ' ')"/>
                        </dateCreated>
                        <dateIssued keyDate="yes">
                            <xsl:value-of select="replace(regex-group(2), '\s+', ' ')"/>
                        </dateIssued>
                    </xsl:matching-substring>
                </xsl:analyze-string>
            </xsl:when>
            <xsl:when test="matches(., $caRangeRegEx)">
                <xsl:analyze-string select="." regex="{$caRangeRegEx}">
                    <xsl:matching-substring>
                        <dateIssued point="start" keyDate="yes" qualifier="approximate">
                            <xsl:value-of select="replace(regex-group(1), '\s+', ' ')"/>
                            <xsl:value-of select="replace(regex-group(2), '\s+', ' ')"/>
                        </dateIssued>
                        <dateIssued point="end" qualifier="approximate">
                            <xsl:value-of select="replace(regex-group(1), '\s+', ' ')"/>
                            <xsl:value-of select="replace(regex-group(3), '\s+', ' ')"/>
                        </dateIssued>
                    </xsl:matching-substring>
                </xsl:analyze-string>
            </xsl:when>
            
            <xsl:otherwise>
                <dateIssued keyDate="yes">
                    <xsl:value-of select="."/>
                </dateIssued>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
</xsl:stylesheet>