<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
      xmlns:xs="http://www.w3.org/2001/XMLSchema"
      xmlns:mods="http://www.loc.gov/mods/v3"
      xpath-default-namespace="http://www.loc.gov/mods/v3"
      exclude-result-prefixes="xs"
      version="2.0"
      xmlns="http://www.loc.gov/mods/v3">
    
    <!-- splits physicalDescription/note @type="medium" into note and extent, splitting on the colon -->
    
    <xsl:template match="@* | node()">
        <xsl:copy>
            <xsl:apply-templates select="@* | node()"/>
        </xsl:copy>
    </xsl:template>
    
    <xsl:variable name="targetText" select="node()/physicalDescription/note[@type='medium']/text()"/>
    <xsl:variable name="myRegEx" select="'([0-9\sa-zA-Z\-()/.]+)\s:\s([0-9\sa-zA-Z,\.]+\.)'"/>
    
    <xsl:template match="physicalDescription/note[@type='medium']">
        <xsl:choose>
            <xsl:when test="matches(., ':')">
                <xsl:analyze-string select="$targetText" regex="{$myRegEx}">
                    <xsl:matching-substring>
                        <extent>
                            <xsl:value-of select="regex-group(1)"/>
                        </extent>
                        <note type="medium">
                            <xsl:value-of select="regex-group(2)"/>
                        </note>
                    </xsl:matching-substring>
                </xsl:analyze-string>
            </xsl:when>
            <xsl:otherwise>
                <note type="medium">
                    <xsl:value-of select="."/>
                </note>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>

</xsl:stylesheet>