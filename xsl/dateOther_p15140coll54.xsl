<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:mods="http://www.loc.gov/mods/v3"
    xpath-default-namespace="http://www.loc.gov/mods/v3"
    exclude-result-prefixes="xs"
    version="2.0"
    xmlns="http://www.loc.gov/mods/v3" >
    
    <!-- Remove parenthetical natural language dates from dateOther field in p15140coll54 -->
    
    <xsl:template match="@* | node()">
        <xsl:copy>
            <xsl:apply-templates select="@* | node()"/>
        </xsl:copy>
    </xsl:template>
    
    <xsl:variable name="targetText" select="//originInfo/dateOther/text()"/>
    <xsl:variable name="myRegEx" select="'([0-9\-]+)\s\(([a-zA-Z0-9\s,\.]+\))'"/>
    
    <xsl:template match="originInfo/dateOther">
        <xsl:choose>
            <xsl:when test="matches(., '\(')">
                <xsl:analyze-string select="$targetText" regex="{$myRegEx}">
                    <xsl:matching-substring>
                        <dateOther>
                            <xsl:value-of select="regex-group(1)"/>
                        </dateOther>
                    </xsl:matching-substring>
                </xsl:analyze-string>
            </xsl:when>
            <xsl:otherwise>
                <dateOther>
                    <xsl:value-of select="."/>
                </dateOther>
            </xsl:otherwise>
        </xsl:choose>
        
    </xsl:template>
    
</xsl:stylesheet>