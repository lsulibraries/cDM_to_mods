<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:mods="http://www.loc.gov/mods/v3"
    xpath-default-namespace="http://www.loc.gov/mods/v3"
    exclude-result-prefixes="xs"
    version="2.0"
    xmlns="http://www.loc.gov/mods/v3">
    
    <!-- YYYY-M-D or YYYY-M-DD or YYYY-MM-D to YYYY-MM-DD 
    or YYYY-M to YYYY-MM 
    or YYYY-M-DD-DD to point="start" YYYY-MM-DD point="end" YYYY-MM-DD -->
    
    <xsl:template match="@* | node()">
        <xsl:copy>
            <xsl:apply-templates select="@* | node()"/>
        </xsl:copy>
    </xsl:template>
    
    <xsl:variable name="YYYYMDregEx" select="'([0-9]{4})-([0-9]{1})-([0-9]{1})$'"/>
    <xsl:variable name="YYYYMMDregEx" select="'([0-9]{4})-([0-9]{2})-([0-9]{1})$'"/>
    <xsl:variable name="YYYYMDDregEx" select="'([0-9]{4})-([0-9]{1})-([0-9]{2})$'"/>
    <xsl:variable name="YYYYMregEx" select="'([0-9]{4})-([0-9]{1})$'"/>
    <xsl:variable name="YYYYMMDDDDRangeregEx" select="'([0-9]{4})-([0-9]{1})-([0-9]{2})-([0-9]{2})$'"/>
    
    <xsl:template match="originInfo/dateCreated">
        <xsl:choose>
            <xsl:when test="matches(., $YYYYMMDregEx)">
                <xsl:analyze-string select="." regex="{$YYYYMMDregEx}">
                    <xsl:matching-substring>
                        <dateCreated keyDate="yes">
                            <xsl:value-of select="replace(regex-group(1), '\s+', ' ')"/>
                            <xsl:text>-</xsl:text>
                            <xsl:value-of select="replace(regex-group(2), '\s+', ' ')"/>
                            <xsl:text>-0</xsl:text>
                            <xsl:value-of select="replace(regex-group(3), '\s+', ' ')"/>
                        </dateCreated>
                    </xsl:matching-substring>
                </xsl:analyze-string>
            </xsl:when>
            <xsl:when test="matches(., $YYYYMDDregEx)">
                <xsl:analyze-string select="." regex="{$YYYYMDDregEx}">
                    <xsl:matching-substring>
                        <dateCreated keyDate="yes">
                            <xsl:value-of select="replace(regex-group(1), '\s+', ' ')"/>
                            <xsl:text>-0</xsl:text>
                            <xsl:value-of select="replace(regex-group(2), '\s+', ' ')"/>
                            <xsl:text>-</xsl:text>
                            <xsl:value-of select="replace(regex-group(3), '\s+', ' ')"/>
                        </dateCreated>
                    </xsl:matching-substring>
                </xsl:analyze-string>
            </xsl:when>
            <xsl:when test="matches(., $YYYYMDregEx)">
                <xsl:analyze-string select="." regex="{$YYYYMDregEx}">
                    <xsl:matching-substring>
                        <dateCreated keyDate="yes">
                            <xsl:value-of select="replace(regex-group(1), '\s+', ' ')"/>
                            <xsl:text>-0</xsl:text>
                            <xsl:value-of select="replace(regex-group(2), '\s+', ' ')"/>
                            <xsl:text>-0</xsl:text>
                            <xsl:value-of select="replace(regex-group(3), '\s+', ' ')"/>
                        </dateCreated>
                    </xsl:matching-substring>
                </xsl:analyze-string>
            </xsl:when>
            <xsl:when test="matches(., $YYYYMregEx)">
                <xsl:analyze-string select="." regex="{$YYYYMregEx}">
                    <xsl:matching-substring>
                        <dateCreated keyDate="yes">
                            <xsl:value-of select="replace(regex-group(1), '\s+', ' ')"/>
                            <xsl:text>-0</xsl:text>
                            <xsl:value-of select="replace(regex-group(2), '\s+', ' ')"/>
                        </dateCreated>
                    </xsl:matching-substring>
                </xsl:analyze-string>
            </xsl:when>
            <xsl:when test="matches(., $YYYYMMDDDDRangeregEx)">
                <xsl:analyze-string select="." regex="{$YYYYMMDDDDRangeregEx}">
                    <xsl:matching-substring>
                        <dateCreated point="start" keyDate="yes">
                            <xsl:value-of select="replace(regex-group(1), '\s+', ' ')"/>
                            <xsl:text>-0</xsl:text>
                            <xsl:value-of select="replace(regex-group(2), '\s+', ' ')"/>
                            <xsl:text>-</xsl:text>
                            <xsl:value-of select="replace(regex-group(3), '\s+', ' ')"/>
                        </dateCreated>
                        <dateCreated point="end">
                            <xsl:value-of select="replace(regex-group(1), '\s+', ' ')"/>
                            <xsl:text>-0</xsl:text>
                            <xsl:value-of select="replace(regex-group(2), '\s+', ' ')"/>
                            <xsl:text>-</xsl:text>
                            <xsl:value-of select="replace(regex-group(4), '\s+', ' ')"/>
                        </dateCreated>
                    </xsl:matching-substring>
                </xsl:analyze-string>
            </xsl:when>
            <xsl:otherwise>
                <xsl:copy>
                    <xsl:apply-templates select="@*|node()" />
                </xsl:copy>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
</xsl:stylesheet>