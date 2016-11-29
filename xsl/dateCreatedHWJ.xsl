<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:mods="http://www.loc.gov/mods/v3"
    xpath-default-namespace="http://www.loc.gov/mods/v3"
    exclude-result-prefixes="xs"
    version="2.0"
    xmlns="http://www.loc.gov/mods/v3">
    
    <!-- takes various permutations of date formatting in dateCreated and converts them
    YYYY-YYYY breaks into point=start and point=end
    Ca. YYYY gets an attribute qualifier="approximate"
    Ca. YYYY-YYYY gets approximate qualifier and start and end
    Before YYYY and YYYY gets split with point start and point end
    YYYY; YYYY; YYYY captures and splits first and last years - discards the middles
    all others stay the same-->
    
    <xsl:template match="@* | node()">
        <xsl:copy>
            <xsl:apply-templates select="@* | node()"/>
        </xsl:copy>
    </xsl:template>
        
    <xsl:template match="originInfo/dateCreated">
        <xsl:choose>
            <xsl:when test="matches(., 'No date specified')">
                <dateCreated keyDate="yes" point="start" qualifier="inferred">1857</dateCreated>
                <dateCreated point="end" qualifier="inferred">1872</dateCreated>
            </xsl:when>
            <xsl:otherwise>
                <dateCreated keyDate="yes">
                    <xsl:value-of select="."/>
                </dateCreated>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
</xsl:stylesheet>