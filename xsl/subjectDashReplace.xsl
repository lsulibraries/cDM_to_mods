<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
      xmlns:xs="http://www.w3.org/2001/XMLSchema"
      xmlns:mods="http://www.loc.gov/mods/v3"
      xpath-default-namespace="http://www.loc.gov/mods/v3"
      exclude-result-prefixes="xs"
      version="2.0"
      xmlns="http://www.loc.gov/mods/v3">
    
    <!-- replaces space-emDash-space with double dash in subject field, for proper tokenization in subjectSplit, as in LSU_CFF collection
    basic find & replace -->
    
    <xsl:template match="@* | node()">
        <xsl:copy>
            <xsl:apply-templates select="@* | node()"/>
        </xsl:copy>
    </xsl:template>
    
    <xsl:template match="subject/topic">
        <xsl:copy>
            <xsl:copy-of select="@*"/>
            <xsl:value-of select="replace(., ' – ', '--')"/>
        </xsl:copy>
    </xsl:template>
    
</xsl:stylesheet>