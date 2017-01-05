<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:mods="http://www.loc.gov/mods/v3"
    xpath-default-namespace="http://www.loc.gov/mods/v3"
    exclude-result-prefixes="xs"
    version="2.0"
    xmlns="http://www.loc.gov/mods/v3">
    
    <!-- reformats non parsing dates for CWD, Caroline Wogan Durieux -->
    
    <xsl:template match="@* | node()">
        <xsl:copy>
            <xsl:apply-templates select="@* | node()"/>
        </xsl:copy>
    </xsl:template>
        
    <xsl:template match="originInfo/dateCreated">
        <xsl:choose>
            <xsl:when test="matches(., 'CA. 1960-65')">
                <dateCreated keyDate="yes" qualifier='approximate' point='start'>1960</dateCreated>
                <dateCreated qualifier='approximate' point='end'>1965</dateCreated>
            </xsl:when>
            <xsl:when test="matches(., 'ca. 1955-56', 'i')">
                <dateCreated keyDate="yes" qualifier='approximate' point='start'>1955</dateCreated>
                <dateCreated qualifier='approximate' point='end'>1956</dateCreated>
            </xsl:when>
            <xsl:when test="matches(., 'ca. 1955-62')">
                <dateCreated keyDate="yes" qualifier='approximate' point='start'>1955</dateCreated>
                <dateCreated qualifier='approximate' point='end'>1962</dateCreated>
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
    
    <xsl:template match="originInfo/dateCaptured">
        <xsl:choose>
            <xsl:when test="matches(., 'NA')">
            </xsl:when>            
            <xsl:otherwise>
                <dateCaptured>
                    <xsl:value-of select="."/>
                </dateCaptured>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
</xsl:stylesheet>