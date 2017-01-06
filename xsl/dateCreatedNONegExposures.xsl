<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:mods="http://www.loc.gov/mods/v3"
    xpath-default-namespace="http://www.loc.gov/mods/v3"
    exclude-result-prefixes="xs"
    version="2.0"
    xmlns="http://www.loc.gov/mods/v3">
    
    <!-- reformats non parsing dates for NONegExposures, New Orleans Negatives Exposures and Prints -->
    
    <xsl:template match="@* | node()">
        <xsl:copy>
            <xsl:apply-templates select="@* | node()"/>
        </xsl:copy>
    </xsl:template>
        
    <xsl:template match="originInfo/dateCreated">
        <xsl:choose>
            <xsl:when test="matches(., 'August 29, 1924')">
                <dateCreated keyDate="yes">1924-08-29</dateCreated>
            </xsl:when>
            <xsl:when test="matches(., 'August 24, 1924')">
                <dateCreated keyDate="yes">1924-08-24</dateCreated>
            </xsl:when>
            <xsl:when test="matches(., 'April 1928')">
                <dateCreated keyDate="yes">1928-04</dateCreated>
            </xsl:when>
            <xsl:when test="matches(., 'May 1930')">
                <dateCreated keyDate="yes">1930-05</dateCreated>
            </xsl:when>
            <xsl:otherwise>
                <dateCreated keyDate="yes">
                    <xsl:value-of select="."/>
                </dateCreated>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
</xsl:stylesheet>