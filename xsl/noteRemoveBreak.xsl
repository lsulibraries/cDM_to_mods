<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
      xmlns:xs="http://www.w3.org/2001/XMLSchema"
      xmlns:mods="http://www.loc.gov/mods/v3"
      xpath-default-namespace="http://www.loc.gov/mods/v3"
      exclude-result-prefixes="xs"
      version="2.0"
      xmlns="http://www.loc.gov/mods/v3">
    
    <!-- removes <br> tags from note element; also various other elements as needed 
    basic find & replace -->
    
    <xsl:template match="@* | node()">
        <xsl:copy>
            <xsl:apply-templates select="@* | node()"/>
        </xsl:copy>
    </xsl:template>
    
    <xsl:template match="note[@type='content']">
        <xsl:copy>
            <xsl:copy-of select="@*"/>
            <xsl:value-of select="replace(., '&lt;br&gt;', '')"/>
        </xsl:copy>
    </xsl:template>
    
    <xsl:template match="abstract">
        <xsl:copy>
            <xsl:copy-of select="@*"/>
            <xsl:value-of select="replace(., '&lt;br&gt;', '')"/>
        </xsl:copy>
    </xsl:template>
    
    <xsl:template match="subject/topic">
        <xsl:copy>
            <xsl:copy-of select="@*"/>
            <xsl:value-of select="replace(., '&lt;br&gt;', '')"/>
        </xsl:copy>
    </xsl:template>
    
    <xsl:template match="titleInfo/title">
        <xsl:copy>
            <xsl:copy-of select="@*"/>
            <xsl:value-of select="replace(., '&lt;br&gt;', '')"/>
        </xsl:copy>
    </xsl:template>
    
</xsl:stylesheet>