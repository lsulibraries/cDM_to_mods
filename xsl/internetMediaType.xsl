<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
      xmlns:xs="http://www.w3.org/2001/XMLSchema"
      xmlns:mods="http://www.loc.gov/mods/v3"
      xpath-default-namespace="http://www.loc.gov/mods/v3"
      exclude-result-prefixes="xs"
      version="2.0"
      xmlns="http://www.loc.gov/mods/v3">
    
    <!-- splits internetMediaType "mp4: 16mm film" into internetMediaType and note, or lowercase PDF, specific for Loyola Athletic collection-->
    
    <xsl:template match="@* | node()">
        <xsl:copy>
            <xsl:apply-templates select="@* | node()"/>
        </xsl:copy>
    </xsl:template>
    
    <xsl:variable name="targetText" select="node()/physicalDescription/internetMediaType/text()"/>
    <xsl:variable name="myRegEx" select="'([0-9a-zA-Z\s,]+);\s?([0-9\sa-zA-Z.&quot;]+)'"/>
    
    <xsl:template match="physicalDescription/internetMediaType">
        <xsl:choose>
            <xsl:when test="matches(., 'mp4; 16mm film', 'i')">
                <internetMediaType>mp4</internetMediaType>
                <note type="content">16mm film</note>
            </xsl:when>
            <xsl:when test="matches(., 'pdf; jpeg', 'i')">
                <internetMediaType>pdf</internetMediaType>
                <internetMediaType>jp2</internetMediaType>
            </xsl:when>
            <xsl:when test="matches(., 'JPEG2000', 'i')">
                <internetMediaType>jp2</internetMediaType>
            </xsl:when>
            <xsl:when test="matches(., 'jpeg', 'i')">
                <internetMediaType>jp2</internetMediaType>
            </xsl:when>
            <xsl:when test="matches(., 'jpg', 'i')">
                <internetMediaType>jp2</internetMediaType>
            </xsl:when>
            <xsl:when test="matches(., 'JPEG 2000', 'i')">
                <internetMediaType>jp2</internetMediaType>
            </xsl:when>
            <xsl:when test="matches(., 'MrSid', 'i')">
                <internetMediaType>jp2</internetMediaType>
            </xsl:when>
            <xsl:when test="matches(., 'gif', 'i')">
                <internetMediaType>jp2</internetMediaType>
            </xsl:when>
            <xsl:when test="matches(., 'tiff', 'i')">
                <internetMediaType>jp2</internetMediaType>
            </xsl:when>
            <xsl:when test="matches(., 'tif', 'i')">
                <internetMediaType>jp2</internetMediaType>
            </xsl:when>
            <xsl:when test="matches(., 'audio', 'i')">
                <internetMediaType>mp3</internetMediaType>
            </xsl:when>
            <xsl:when test="matches(., 'pdf', 'i')">
                <internetMediaType>pdf</internetMediaType>
            </xsl:when>
            <xsl:when test="matches(., 'text', 'i')">
                <internetMediaType>pdf</internetMediaType>
            </xsl:when>
            <xsl:when test="matches(., 'M4v', 'i')">
                <internetMediaType>mp4</internetMediaType>
            </xsl:when>
            <xsl:when test="matches(., 'Mov', 'i')">
                <internetMediaType>mp4</internetMediaType>
            </xsl:when>
            <xsl:when test="matches(., 'WMV', 'i')">
                <internetMediaType>mp4</internetMediaType>
            </xsl:when>
            <xsl:otherwise>
                <internetMediaType>
                    <xsl:value-of select="."/>
                </internetMediaType>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>

</xsl:stylesheet>