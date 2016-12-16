<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
      xmlns:xs="http://www.w3.org/2001/XMLSchema"
      xmlns:mods="http://www.loc.gov/mods/v3"
      xpath-default-namespace="http://www.loc.gov/mods/v3"
      exclude-result-prefixes="xs"
      version="2.0"
      xmlns="http://www.loc.gov/mods/v3">
    
    <!-- splits physicalDescription/note @type="medium" for Tensas collection -->
    
    <xsl:template match="@* | node()">
        <xsl:copy>
            <xsl:apply-templates select="@* | node()"/>
        </xsl:copy>
    </xsl:template>
    
    <xsl:template match="physicalDescription/note[@type='medium']">
        <xsl:choose>
            <xsl:when test="matches(., 'Resin-coated paper prints&lt;br&gt;4.00&quot; x 5.00&quot;', 'i')">
                <note type="medium">Resin-coated paper prints</note>
                <extent>4.00&quot; x 5.00&quot;</extent>
            </xsl:when>
            <xsl:when test="matches(., 'Pencil on paper; 67 cm. x 76 cm.', 'i')">
                <note type="medium">Pencil on paper</note>
                <extent>67 cm. x 76 cm.</extent>
            </xsl:when>
            <xsl:when test="matches(., 'Digital photographs&lt;br&gt;1251 ppi X 1602 ppi', 'i')">
                <note type="medium">Digital photographs</note>
            </xsl:when>
            <xsl:otherwise>
                <note type="medium">
                    <xsl:value-of select="."/>
                </note>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>

</xsl:stylesheet>