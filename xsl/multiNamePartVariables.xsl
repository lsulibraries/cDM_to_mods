<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:mods="http://www.loc.gov/mods/v3"
    xpath-default-namespace="http://www.loc.gov/mods/v3"
    exclude-result-prefixes="xs"
    version="2.0"
    xmlns="http://www.loc.gov/mods/v3" >
    
    <!-- If the namePart is repeated, split them into different contributors -->
    
    <xsl:template match="@* | node()">
        <xsl:copy>
            <xsl:apply-templates select="@* | node()"/>
        </xsl:copy>
    </xsl:template>
    
    <xsl:template match="name">
        <xsl:variable name="roleText" select="role/roleTerm[@type='text']"/>
        <xsl:variable name="roleCode" select="role/roleTerm[@type='code']"/>
        
        <xsl:for-each select="namePart">
            <xsl:element name="name">
            <xsl:attribute name="displayLabel">
                <xsl:value-of select="$roleText"/>
            </xsl:attribute>
                <role>
                    <roleTerm type="text" authority="marcrelator"><xsl:value-of select="$roleText"/></roleTerm>
                    <roleTerm type="code" authority="marcrelator"><xsl:value-of select="$roleCode"/></roleTerm>
                </role>
                <namePart>
                    <xsl:value-of select="."/>
                </namePart>
            </xsl:element>
        </xsl:for-each>
    </xsl:template>
    
</xsl:stylesheet>