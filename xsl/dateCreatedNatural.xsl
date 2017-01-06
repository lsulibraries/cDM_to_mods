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
            <xsl:when test="matches(., '2003 April 4-7')">
                <dateCreated keyDate="yes" point="start">2003-04-04</dateCreated>
                <dateCreated point="end">2003-04-07</dateCreated>
            </xsl:when>
            <xsl:when test="matches(., '2005 March 22-23')">
                <dateCreated keyDate="yes" point="start">2005-03-22</dateCreated>
                <dateCreated point="end">2005-03-23</dateCreated>
            </xsl:when>
            <xsl:otherwise>
                <dateCreated keyDate="yes">
                    <xsl:value-of select="."/>
                </dateCreated>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
</xsl:stylesheet>