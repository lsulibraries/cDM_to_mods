<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:mods="http://www.loc.gov/mods/v3"
    xpath-default-namespace="http://www.loc.gov/mods/v3"
    exclude-result-prefixes="xs"
    version="2.0"
    xmlns="http://www.loc.gov/mods/v3">
    
    <!-- reformats non parsing dates for p15140coll18, Hermann Moyse coll -->
    
    <xsl:template match="@* | node()">
        <xsl:copy>
            <xsl:apply-templates select="@* | node()"/>
        </xsl:copy>
    </xsl:template>
        
    <xsl:template match="originInfo/dateCreated">
        <xsl:choose>
            <xsl:when test="matches(., 'circa 1917 spring')">
                <dateCreated keyDate="yes" qualifier="approximate" point="start">1917-03</dateCreated>
                <dateCreated qualifier="approximate" point="end">1917-06</dateCreated>
            </xsl:when>
            <xsl:when test="matches(., 'circa 1917 May')">
                <dateCreated keyDate="yes" qualifier="approximate">1917-05</dateCreated>
            </xsl:when>
            <xsl:when test="matches(., 'circa 1917 Aug.')">
                <dateCreated keyDate="yes" qualifier="approximate">1917-08</dateCreated>
            </xsl:when>
            <xsl:when test="matches(., '1918 circa Jan. 10-24')">
                <dateCreated keyDate="yes" qualifier="approximate" point="start">1918-01-10</dateCreated>
                <dateCreated qualifier="approximate" point="end">1918-01-24</dateCreated>
            </xsl:when>
            <xsl:when test="matches(., '1919 circa Mar.')">
                <dateCreated keyDate="yes" qualifier="approximate">1919-03</dateCreated>
            </xsl:when>
            <xsl:when test="matches(., '1919 circa Oct.')">
                <dateCreated keyDate="yes" qualifier="approximate">1919-10</dateCreated>
            </xsl:when>
            <xsl:otherwise>
                <dateCreated keyDate="yes">
                    <xsl:value-of select="."/>
                </dateCreated>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
</xsl:stylesheet>