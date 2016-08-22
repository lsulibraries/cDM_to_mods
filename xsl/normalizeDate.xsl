<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:mods="http://www.loc.gov/mods/v3"
    xpath-default-namespace="http://www.loc.gov/mods/v3"
    exclude-result-prefixes="xs"
    version="2.0"
    xmlns="http://www.loc.gov/mods/v3">
    
    <!-- normalizes date of MM/DD/YYYY to become YYYY-MM-DD 
    only in originInfo/dateCaptured and recordInfo/recordCreationDate -->
    
    <xsl:template match="@* | node()">
        <xsl:copy>
            <xsl:apply-templates select="@* | node()"/>
        </xsl:copy>
    </xsl:template>
    
    <xsl:variable name="dateRegEx" select="'([0-9]{1,2})/([0-9]{1,2})/([0-9]{4})'"/> <!-- MM-DD-YYYY -->
    
    <xsl:template match="originInfo/dateCaptured">
        <xsl:choose>
            <xsl:when test="matches(., $dateRegEx)">
                <xsl:analyze-string select="." regex="{$dateRegEx}">
                    <xsl:matching-substring>
                        <dateCaptured>
                            <xsl:value-of select="replace(regex-group(3), '\s+', ' ')"/>
                            <xsl:text>-</xsl:text>
                            <xsl:if test="string-length(regex-group(1))=1">
                                <xsl:text>0</xsl:text>
                            </xsl:if>
                            <xsl:value-of select="replace(regex-group(1), '\s+', ' ')"/>
                            <xsl:text>-</xsl:text>
                            <xsl:if test="string-length(regex-group(2))=1">
                                <xsl:text>0</xsl:text>
                            </xsl:if>
                            <xsl:value-of select="replace(regex-group(2), '\s+', ' ')"/>
                        </dateCaptured>
                       </xsl:matching-substring>
                </xsl:analyze-string>
            </xsl:when>
            <xsl:otherwise>
                <dateCaptured>
                    <xsl:value-of select="."/>
                </dateCaptured>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
    
    <xsl:template match="recordInfo/recordCreationDate">
        <xsl:choose>
            <xsl:when test="matches(., $dateRegEx)">
                <xsl:analyze-string select="." regex="{$dateRegEx}">
                    <xsl:matching-substring>
                        <recordCreationDate>
                            <xsl:value-of select="replace(regex-group(3), '\s+', ' ')"/>
                            <xsl:text>-</xsl:text>
                            <xsl:if test="string-length(regex-group(1))=1">
                                <xsl:text>0</xsl:text>
                            </xsl:if>
                            <xsl:value-of select="replace(regex-group(1), '\s+', ' ')"/>
                            <xsl:text>-</xsl:text>
                            <xsl:if test="string-length(regex-group(2))=1">
                                <xsl:text>0</xsl:text>
                            </xsl:if>
                            <xsl:value-of select="replace(regex-group(2), '\s+', ' ')"/>
                        </recordCreationDate>
                    </xsl:matching-substring>
                </xsl:analyze-string>
            </xsl:when>
            <xsl:otherwise>
                <recordCreationDate>
                    <xsl:value-of select="."/>
                </recordCreationDate>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
</xsl:stylesheet>