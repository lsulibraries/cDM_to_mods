<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
      xmlns:xs="http://www.w3.org/2001/XMLSchema"
      xmlns:mods="http://www.loc.gov/mods/v3"
      xpath-default-namespace="http://www.loc.gov/mods/v3"
      exclude-result-prefixes="xs"
      version="2.0"
      xmlns="http://www.loc.gov/mods/v3">
    
    <!-- breaks up abstract with extent before semicolon.
    moves the first part to physicalDescripton/extent
    keeps the second part as abstract -->
    
    <xsl:template match="@* | node()">
        <xsl:copy>
            <xsl:apply-templates select="@* | node()"/>
        </xsl:copy>
    </xsl:template>
    
    <xsl:variable name="extentText" select="node()/physicalDescription/extent/text()"/>
    <xsl:variable name="myRegEx" select="'([0-9a-zA-Z\s,]+);\s?([0-9\sa-zA-Z.&quot;]+;\s?([0-9\sa-zA-Z.&quot;]+)'"/>
    
    <xsl:template match="abstract">
        <xsl:choose>
            <xsl:when test="matches(., ';')">
                <xsl:analyze-string select="extentText" regex="{$myRegEx}">
                    <xsl:matching-substring>
                        <abstract>
                            <xsl:value-of select="replace(regex-group(2), '\s+', ' ')"/>
                        </abstract>
                    </xsl:matching-substring>
                </xsl:analyze-string>
            </xsl:when>
            <xsl:otherwise>
                <abstract>
                    <xsl:value-of select="."/>
                </abstract>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
    
    <xsl:template match="physicalDescription">
        <xsl:copy>
            <xsl:apply-templates/>
            <xsl:analyze-string select="$extentText" regex="{$myRegEx}">
                <xsl:matching-substring>
                    <xsl:element name="extent">
                        <xsl:value-of select="replace(regex-group(3), '\s+', ' ')"/>
                    </xsl:element>
                </xsl:matching-substring>
            </xsl:analyze-string>
        </xsl:copy>
    </xsl:template>
</xsl:stylesheet>