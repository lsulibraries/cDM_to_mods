<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:mods="http://www.loc.gov/mods/v3"
    xpath-default-namespace="http://www.loc.gov/mods/v3"
    exclude-result-prefixes="xs"
    version="2.0"
    xmlns="http://www.loc.gov/mods/v3" >
    
    <!-- when typeOfResource is image, make note type=content into extent -->
    
    <xsl:template match="@* | node()">
        <xsl:copy>
            <xsl:apply-templates select="@* | node()"/>
        </xsl:copy>
    </xsl:template>
    
    <xsl:variable name="resource" select="node()/typeOfResource/text()"/>
    
    <xsl:template match="note[@type='content']">
        <xsl:choose>
            <xsl:when test="matches($resource, 'sound')">
                <note type="performers">
                    <xsl:value-of select="."/>
                </note>
            </xsl:when>
            <xsl:otherwise>
                <!-- remove the note -->
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
    
    <xsl:template match="physicalDescription">
        <xsl:choose>
            <xsl:when test="matches($resource, 'image')">
                <physicalDescription>
                <xsl:apply-templates />
                <extent>
                    <xsl:value-of select="//note[@type='content']"/>
                </extent>
                </physicalDescription>
            </xsl:when>
            <xsl:otherwise>
                <physicalDescription>
                    <xsl:apply-templates />
                </physicalDescription>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
    

    
    

</xsl:stylesheet>