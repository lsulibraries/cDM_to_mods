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
    
    <xsl:template match="typeOfResource">
        <xsl:choose>
            <xsl:when test="matches(., 'video', 'i')">
                <typeOfResource>moving image</typeOfResource>
                <physicalDescription><internetMediaType>mp4</internetMediaType></physicalDescription>
            </xsl:when>
            <xsl:when test="matches(., 'videos', 'i')">
                <typeOfResource>still image</typeOfResource>
                <physicalDescription><internetMediaType>jp2</internetMediaType></physicalDescription>
            </xsl:when>
            <xsl:when test="matches(., 'pdf', 'i')">
                <typeOfResource>text</typeOfResource>
                <physicalDescription><internetMediaType>pdf</internetMediaType></physicalDescription>
            </xsl:when>
            <xsl:otherwise>
                <typeOfResource>
                    <xsl:value-of select="."/>
                </typeOfResource>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>

 </xsl:stylesheet>