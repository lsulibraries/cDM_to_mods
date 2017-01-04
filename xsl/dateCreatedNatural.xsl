<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:mods="http://www.loc.gov/mods/v3"
    xpath-default-namespace="http://www.loc.gov/mods/v3"
    exclude-result-prefixes="xs"
    version="2.0"
    xmlns="http://www.loc.gov/mods/v3">
    
    <!-- reformats non parsing, natural language dates found in lsu collections -->
    
    <xsl:template match="@* | node()">
        <xsl:copy>
            <xsl:apply-templates select="@* | node()"/>
        </xsl:copy>
    </xsl:template>
        
    <xsl:template match="originInfo/dateCreated">
        <xsl:choose>
            <xsl:when test="matches(., '1906 Feb.')">
                <dateCreated keyDate="yes">1906-02</dateCreated>
            </xsl:when>
            <xsl:when test="matches(., '1927 July 27')">
                <dateCreated keyDate="yes">1927-07-27</dateCreated>
            </xsl:when>
            <xsl:when test="matches(., '1927 Dec. 12')">
                <dateCreated keyDate="yes">1927-12-12</dateCreated>
            </xsl:when>
            <xsl:when test="matches(., '1944 June 15')">
                <dateCreated keyDate="yes">1944-06-15</dateCreated>
            </xsl:when>
            <xsl:when test="matches(., '1948 Dec. 13')">
                <dateCreated keyDate="yes">1948-12-13</dateCreated>
            </xsl:when>
            <xsl:when test="matches(., 'unknown')">
            </xsl:when>
            <xsl:when test="matches(., 'none')">
            </xsl:when>
            <xsl:otherwise>
                <dateCreated keyDate="yes">
                    <xsl:value-of select="."/>
                </dateCreated>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
</xsl:stylesheet>