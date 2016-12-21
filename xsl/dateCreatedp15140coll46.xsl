<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:mods="http://www.loc.gov/mods/v3"
    xpath-default-namespace="http://www.loc.gov/mods/v3"
    exclude-result-prefixes="xs"
    version="2.0"
    xmlns="http://www.loc.gov/mods/v3">
    
    <!-- reformats non parsing dates for p15140coll46, fonville winans collection -->
    
    <xsl:template match="@* | node()">
        <xsl:copy>
            <xsl:apply-templates select="@* | node()"/>
        </xsl:copy>
    </xsl:template>
        
    <xsl:template match="originInfo/dateCreated">
        <xsl:choose>
            <xsl:when test="matches(., '1947 February 10')">
                <dateCreated keyDate="yes">1947-02-10</dateCreated>
            </xsl:when>
            <xsl:when test="matches(., '1947 March 03')">
                <dateCreated keyDate="yes">1947-03-03</dateCreated>
            </xsl:when>
            <xsl:when test="matches(., '1947 March 14')">
                <dateCreated keyDate="yes">1947-03-14</dateCreated>
            </xsl:when>
            <xsl:when test="matches(., '1948 February 10')">
                <dateCreated keyDate="yes">1948-02-10</dateCreated>
            </xsl:when>
            <xsl:when test="matches(., '1948 March 03')">
                <dateCreated keyDate="yes">1948-03-03</dateCreated>
            </xsl:when>
            <xsl:when test="matches(., '1948 March 14')">
                <dateCreated keyDate="yes">1948-03-14</dateCreated>
            </xsl:when>            
            <xsl:otherwise>
                <dateCreated keyDate="yes">
                    <xsl:value-of select="."/>
                </dateCreated>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
</xsl:stylesheet>