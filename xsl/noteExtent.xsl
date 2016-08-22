<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
      xmlns:xs="http://www.w3.org/2001/XMLSchema"
      xmlns:mods="http://www.loc.gov/mods/v3"
      xpath-default-namespace="http://www.loc.gov/mods/v3"
      exclude-result-prefixes="xs"
      version="2.0"
      xmlns="http://www.loc.gov/mods/v3">
    
    <!-- breaks up content note with extent before semicolon.
    uses the first part to create a physicalDescripton/extent
    keeps the second part as content note
    for BRS -->
    
    <xsl:template match="@* | node()">
        <xsl:copy>
            <xsl:apply-templates select="@* | node()"/>
        </xsl:copy>
    </xsl:template>
    
    <xsl:variable name="noteText" select="node()/note[@type='content']/text()"/>
    <xsl:variable name="myRegEx" select="'(.+);\s?(.+)'"/>
    
    <xsl:template match="note[@type='content']">
        <xsl:choose>
            <xsl:when test="matches(., ';')">
                <xsl:analyze-string select="$noteText" regex="{$myRegEx}">
                    <xsl:matching-substring>
                        <note type="content">
                            <xsl:value-of select="replace(regex-group(2), '\s+', ' ')"/>
                        </note>
                        <physicalDescription>
                            <extent>
                                <xsl:value-of select="replace(regex-group(1), '\s+', ' ')"/>
                            </extent>
                        </physicalDescription>
                    </xsl:matching-substring>
                </xsl:analyze-string>
            </xsl:when>
            <xsl:otherwise>
                <note type="content">
                    <xsl:value-of select="."/>
                </note>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
    
</xsl:stylesheet>