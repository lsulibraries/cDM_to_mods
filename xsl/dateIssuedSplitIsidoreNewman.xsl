<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:mods="http://www.loc.gov/mods/v3"
    xpath-default-namespace="http://www.loc.gov/mods/v3"
    exclude-result-prefixes="xs"
    version="2.0"
    xmlns="http://www.loc.gov/mods/v3">
    
    <!-- tokenizes dateIssued on semicolon -->
    
    <xsl:template match="@* | node()">
        <xsl:copy>
            <xsl:apply-templates select="@* | node()"/>
        </xsl:copy>
    </xsl:template>
    
   
    <xsl:template match="originInfo/dateIssued">          
        <xsl:for-each select="tokenize(., ';')">
          <xsl:choose>
            <xsl:when test="position()=1">
                <xsl:element name="dateIssued">
                    <xsl:attribute name="keyDate">yes</xsl:attribute>
                    <xsl:value-of select="replace(replace(concat(upper-case(substring(.,1,1)),substring(.,2)), '^\s+|\s+$', ''),'\.$','')"/>         
                </xsl:element>
            </xsl:when>
            <xsl:otherwise>
                <xsl:element name="dateIssued">
                    <xsl:value-of select="replace(replace(concat(upper-case(substring(.,1,1)),substring(.,2)), '^\s+|\s+$', ''),'\.$','')"/>         
                </xsl:element>
            </xsl:otherwise>
          </xsl:choose>
        </xsl:for-each>
     </xsl:template>
</xsl:stylesheet>