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
            <xsl:when test="matches(., 'April 1935')">
                <dateCreated keyDate="yes">1935-04</dateCreated>
            </xsl:when>
            <xsl:when test="matches(., 'April 1937')">
                <dateCreated keyDate="yes">1937-04</dateCreated>
            </xsl:when>
            <xsl:when test="matches(., 'May 1937')">
                <dateCreated keyDate="yes">1937-05</dateCreated>
            </xsl:when>
            <xsl:when test="matches(., 'June 1937')">
                <dateCreated keyDate="yes">1937-06</dateCreated>
            </xsl:when>
            <xsl:when test="matches(., 'July 1937')">
                <dateCreated keyDate="yes">1937-07</dateCreated>
            </xsl:when>
            <xsl:when test="matches(., 'December 1937')">
                <dateCreated keyDate="yes">1937-12</dateCreated>
            </xsl:when>
            <xsl:when test="matches(., 'March 6, 1938')">
                <dateCreated keyDate="yes">1938-03-06</dateCreated>
            </xsl:when>
            <xsl:when test="matches(., 'August 1938')">
                <dateCreated keyDate="yes">1938-08</dateCreated>
            </xsl:when>
            <xsl:when test="matches(., 'April 1939')">
                <dateCreated keyDate="yes">1939-04</dateCreated>
            </xsl:when>
            <xsl:when test="matches(., 'May 1939')">
                <dateCreated keyDate="yes">1939-05</dateCreated>
            </xsl:when>
            <xsl:when test="matches(., 'March 1940')">
                <dateCreated keyDate="yes">1940-03</dateCreated>
            </xsl:when>
            <xsl:when test="matches(., 'December 1941')">
                <dateCreated keyDate="yes">1941-12</dateCreated>
            </xsl:when>
            <xsl:when test="matches(., '1937/1938')">
                <dateCreated keyDate="yes" point="start" qualifier="approximate">1937-12</dateCreated>
                <dateCreated point="end" qualifier="approximate">1938-03</dateCreated>
            </xsl:when>
            <xsl:when test="matches(., 'ca. 1940')">
                <dateCreated keyDate="yes" qualifier="approximate">1940</dateCreated>
            </xsl:when>
            <xsl:when test="matches(., 'May/June 1937')">
                <dateCreated keyDate="yes" point="start" qualifier="approximate">1937-05</dateCreated>
                <dateCreated point="end" qualifier="approximate">1937-06</dateCreated>
            </xsl:when>
            <xsl:when test="matches(., 'Spring 1939')">
                <dateCreated keyDate="yes" point="start" qualifier="approximate">1939-03</dateCreated>
                <dateCreated point="end" qualifier="approximate">1939-06</dateCreated>
            </xsl:when>
            <xsl:otherwise>
                <dateCreated keyDate="yes">
                    <xsl:value-of select="."/>
                </dateCreated>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
</xsl:stylesheet>