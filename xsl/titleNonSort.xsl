<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:mods="http://www.loc.gov/mods/v3"
    xpath-default-namespace="http://www.loc.gov/mods/v3"
    exclude-result-prefixes="xs"
    version="2.0"
    xmlns="http://www.loc.gov/mods/v3" >
    
    <!-- If the first word of the title node is "A", "An" or "The" or some special character "'[(... then it wraps it in <nonSort> -->
    
    <xsl:template match="@* | node()">
        <xsl:copy>
            <xsl:apply-templates select="@* | node()"/>
        </xsl:copy>
    </xsl:template>
    
    <xsl:variable name="nonSortArticleRegEx" select="'^(&quot;|''|\[|\(|\.{3})*(An|A|The)?\s(.+)'"/>
    <xsl:variable name="nonSortPuncRegEx" select="'^(&quot;|''|\[|\(|\.{3})(.+)'"/>
    <xsl:variable name="nonSortAQuotRegEx" select="'^(A\s[&quot;])(.+)'"/>  
    <!-- A " -->
    
    <xsl:template match="titleInfo/title">
        <xsl:choose>
            <xsl:when test="matches(., $nonSortAQuotRegEx)">
                <xsl:analyze-string select="." regex="{$nonSortAQuotRegEx}">
                    <xsl:matching-substring>
                        <nonSort>
                            <xsl:value-of select="replace(regex-group(1), '\s+', ' ')"/>
                        </nonSort>
                        <title>
                            <xsl:value-of select="replace(regex-group(2), '\s+', ' ')"/>
                        </title>
                    </xsl:matching-substring>
                </xsl:analyze-string>
            </xsl:when>
            <xsl:when test="matches(., $nonSortArticleRegEx)">
                <xsl:analyze-string select="." regex="{$nonSortArticleRegEx}">
                    <xsl:matching-substring>
                        <nonSort>
                            <xsl:value-of select="replace(regex-group(1), '\s+', ' ')"/>
                            <xsl:value-of select="replace(regex-group(2), '\s+', ' ')"/>
                        </nonSort>
                        <title>
                            <xsl:value-of select="replace(regex-group(3), '\s+', ' ')"/>
                        </title>
                    </xsl:matching-substring>
                </xsl:analyze-string>
            </xsl:when>
            <xsl:when test="matches(., $nonSortPuncRegEx)">
                <xsl:analyze-string select="." regex="{$nonSortPuncRegEx}">
                    <xsl:matching-substring>
                        <nonSort>
                            <xsl:value-of select="replace(regex-group(1), '\s+', ' ')"/>
                        </nonSort>
                        <title>
                            <xsl:value-of select="replace(regex-group(2), '\s+', ' ')"/>
                        </title>
                    </xsl:matching-substring>
                </xsl:analyze-string>
            </xsl:when>
             <xsl:otherwise>
                <title>
                   <xsl:value-of select="." />
                </title>    
            </xsl:otherwise>
        </xsl:choose>

    </xsl:template>
</xsl:stylesheet>