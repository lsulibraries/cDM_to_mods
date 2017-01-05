<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:mods="http://www.loc.gov/mods/v3"
    xpath-default-namespace="http://www.loc.gov/mods/v3"
    exclude-result-prefixes="xs"
    version="2.0"
    xmlns="http://www.loc.gov/mods/v3">
    
    <!-- takes various permutations of date formatting in dateCreated and converts them
    YYYY-YYYY breaks into point=start and point=end
    Ca. YYYY gets an attribute qualifier="approximate"
    Ca. YYYY-YYYY gets approximate qualifier and start and end
    Before YYYY and YYYY gets split with point start and point end
    YYYY; YYYY; YYYY captures and splits first and last years - discards the middles
    all others stay the same-->
    
    <xsl:template match="@* | node()">
        <xsl:copy>
            <xsl:apply-templates select="@* | node()"/>
        </xsl:copy>
    </xsl:template>
    
    <xsl:variable name="yearRangeRegEx" select="'([0-9]{4})\s?-\s?([0-9]{4})'"/> <!-- YYYY-YYYY or Ca. YYYY-YYYY or [Ca. YYYY-YYYY]-->
    <xsl:variable name="inferredYearRangeRegEx" select="'\[([0-9]{4})-([0-9]{4})\]'"/> <!-- [YYYY-YYYY] -->
    <xsl:variable name="caRegEx" select="'^\[?[cC](irc)?[aA]?\.?\s?([0-9]{4})\]?$'"/> <!-- Ca. YYYY or [Ca. YYYY] or Ca YYYY or Circa YYYY -->
    <xsl:variable name="caDecadeRegEx" select="'[cC]a.\s?([0-9]{3})(0s|-)'"/> <!-- [Ca. YYYYs] or Ca. YYYYs or Ca. YYY- -->
    <xsl:variable name="caEndRegEx" select="'([0-9]{4})\s[cC]a\.'"/> <!-- YYYY ca. --> 
    <xsl:variable name="betweenRegEx" select="'^[bB]etween\s([0-9]{4})(\sand\s|-)([0-9]{4})'"/> <!-- Between YYYY and YYYY -->
    <xsl:variable name="approxBetweenRegEx" select="'\[[bB]etween\s([0-9]{4})(\sand\s|-)([0-9]{4})\]'"/> <!-- [Between YYYY and YYYY] or [Between YYYY-YYYY] -->
    <xsl:variable name="semicolonRegEx" select="'(^[0-9]{4});.*([0-9]{4}$)'"/> <!-- YYYY; YYYY (not captured); YYYY -->
    <xsl:variable name="semicolonYYMMDDRegEx" select="'(^[0-9]{4}\-[0-9]{2}\-[0-9]{2});.*([0-9]{4}\-[0-9]{2}\-[0-9]{2}$)'"/> <!-- YYYY-MM-DD; YYYY-MM-DD (not captured); YYYY-MM-DD -->
    <xsl:variable name="inferredRegEx" select="'\[([0-9]{4})\]'"/> <!-- [YYYY] -->
    <xsl:variable name="inferredYYMMDDRegEx" select="'\[([0-9]{4}\-[0-9]{2}(\-[0-9]{2})?)\]'"/> <!-- [YYYY-MM] or [YYYY-MM-DD] -->
    <xsl:variable name="orRegEx" select="'([0-9]{4})\s(or|and)\s([0-9]{4})'"/> <!-- YYYY or YYYY OR YYYY and YYYY OR with brackets-->
    <xsl:variable name="orYYYYMMDDRegEx" select="'([0-9]{4}\-[0-9]{2}(\-[0-9]{2})?)\s(or|and)\s([0-9]{4}\-[0-9]{2}(\-[0-9]{2})?)'"/> <!-- YYYY-MM-DD or YYYY-MM-DD OR YYYY-MM-DD and YYYY-MM-DD OR with brackets-->
    <xsl:variable name="historicalRegEx" select="'([0-9]{4})\s\(historical\)|([0-9]{4}-[0-9]{2}-[0-9]{2})\s\(historical\)'"/> <!-- YYYY (historical) -->
    <xsl:variable name="decadeRegEx" select="'^([0-9]{3})-$'"/> <!-- YYY- -->
    <xsl:variable name="decadeSsRegEx" select="'^([0-9]{3})(0s|-)'"/> <!-- YYY0s -->
    <xsl:variable name="decadeQuestionableRegEx" select="'^([0-9]{3})-?\(?\?\)?'"/> <!-- YYY? or YYY-? -->
    <xsl:variable name="centuryRegEx" select="'([0-9]{2})th\s[cC]entury'"/> <!-- YYth century -->
    <xsl:variable name="priorRegEx" select="'[Pp]rior\sto\s([0-9]{4})|[Bb]efore\s([0-9]{4})'"/> <!-- prior to YYYY or before YYYY -->
    <xsl:variable name="questionableRegEx" select="'([0-9]{4})\(?\?\)?'"/> <!-- YYYY? or YYYY(?) -->
    <xsl:variable name="questionableRangeRegEx" select="'([0-9]{4})\(?\?\)?\s?-\s?([0-9]{4})\(?\?\)?'"/> <!-- YYYY?-YYYY? or YYYY? - YYYY? -->
       
    <xsl:template match="originInfo/dateCreated">
        <xsl:choose>
            <xsl:when test="matches(., $yearRangeRegEx) and not(matches(., 'Ca.'))">
                <xsl:analyze-string select="." regex="{$yearRangeRegEx}">
                    <xsl:matching-substring>
                        <dateCreated point="start" keyDate="yes">
                            <xsl:value-of select="replace(regex-group(1), '\s+', ' ')"/>
                        </dateCreated>
                        <dateCreated point="end">
                            <xsl:value-of select="replace(regex-group(2), '\s+', ' ')"/>
                        </dateCreated>
                    </xsl:matching-substring>
                </xsl:analyze-string>
            </xsl:when>
            <xsl:when test="matches(., $inferredYearRangeRegEx) and not(matches(., 'Ca.'))">
                <xsl:analyze-string select="." regex="{$inferredYearRangeRegEx}">
                    <xsl:matching-substring>
                        <dateCreated point="start" keyDate="yes" qualifier="inferred">
                            <xsl:value-of select="replace(regex-group(1), '\s+', ' ')"/>
                        </dateCreated>
                        <dateCreated point="end" qualifier="inferred">
                            <xsl:value-of select="replace(regex-group(2), '\s+', ' ')"/>
                        </dateCreated>
                    </xsl:matching-substring>
                </xsl:analyze-string>
            </xsl:when>
            <xsl:when test="matches(., $questionableRegEx) and not(matches(., '-'))">
                <xsl:analyze-string select="." regex="{$questionableRegEx}">
                    <xsl:matching-substring>
                        <dateCreated keyDate="yes" qualifier="questionable">
                            <xsl:value-of select="replace(regex-group(1), '\s+', ' ')"/>
                        </dateCreated>
                    </xsl:matching-substring>
                </xsl:analyze-string>
            </xsl:when>
            <xsl:when test="matches(., $questionableRangeRegEx)">
                <xsl:analyze-string select="." regex="{$questionableRangeRegEx}">
                    <xsl:matching-substring>
                        <dateCreated point="start" keyDate="yes" qualifier="questionable">
                            <xsl:value-of select="replace(regex-group(1), '\s+', ' ')"/>
                        </dateCreated>
                        <dateCreated point="end" qualifier="questionable">
                            <xsl:value-of select="replace(regex-group(2), '\s+', ' ')"/>
                        </dateCreated>
                    </xsl:matching-substring>
                </xsl:analyze-string>
            </xsl:when>
            <xsl:when test="matches(., $caRegEx) and not(matches(., '-'))">
                <xsl:analyze-string select="." regex="{$caRegEx}">
                    <xsl:matching-substring>
                        <dateCreated keyDate="yes" qualifier="approximate">
                            <xsl:value-of select="replace(regex-group(2), '\s+', ' ')"/>
                        </dateCreated>
                    </xsl:matching-substring>
                </xsl:analyze-string>
            </xsl:when>
            <xsl:when test="matches(., $caEndRegEx) and not(matches(., '-'))">
                <xsl:analyze-string select="." regex="{$caEndRegEx}">
                    <xsl:matching-substring>
                        <dateCreated keyDate="yes" qualifier="approximate">
                            <xsl:value-of select="replace(regex-group(1), '\s+', ' ')"/>
                        </dateCreated>
                    </xsl:matching-substring>
                </xsl:analyze-string>
            </xsl:when>
            <xsl:when test="matches(., $yearRangeRegEx) and matches(., 'Ca.')">
                <xsl:analyze-string select="." regex="{$yearRangeRegEx}">
                    <xsl:matching-substring>
                        <dateCreated point="start" keyDate="yes" qualifier="approximate">
                            <xsl:value-of select="replace(regex-group(1), '\s+', ' ')"/>
                        </dateCreated>
                        <dateCreated point="end" qualifier="approximate">
                            <xsl:value-of select="replace(regex-group(2), '\s+', ' ')"/>
                        </dateCreated>
                    </xsl:matching-substring>
                </xsl:analyze-string>
            </xsl:when>
            <xsl:when test="matches(., $caDecadeRegEx)">
                <xsl:analyze-string select="." regex="{$caDecadeRegEx}">
                    <xsl:matching-substring>
                        <dateCreated point="start" keyDate="yes" qualifier="approximate">
                            <xsl:value-of select="replace(regex-group(1), '\s+', ' ')"/>
                            <xsl:text>0</xsl:text>
                        </dateCreated>
                        <dateCreated point="end" qualifier="approximate">
                            <xsl:value-of select="replace(regex-group(1), '\s+', ' ')"/>
                            <xsl:text>9</xsl:text>
                        </dateCreated>
                    </xsl:matching-substring>
                </xsl:analyze-string>
            </xsl:when>
            <xsl:when test="matches(., $decadeSsRegEx)">
                <xsl:analyze-string select="." regex="{$decadeSsRegEx}">
                    <xsl:matching-substring>
                        <dateCreated point="start" keyDate="yes">
                            <xsl:value-of select="replace(regex-group(1), '\s+', ' ')"/>
                            <xsl:text>0</xsl:text>
                        </dateCreated>
                        <dateCreated point="end">
                            <xsl:value-of select="replace(regex-group(1), '\s+', ' ')"/>
                            <xsl:text>9</xsl:text>
                        </dateCreated>
                    </xsl:matching-substring>
                </xsl:analyze-string>
            </xsl:when>
            <xsl:when test="matches(., $betweenRegEx)">
                <xsl:analyze-string select="." regex="{$betweenRegEx}">
                    <xsl:matching-substring>
                        <dateCreated point="start" keyDate="yes">
                            <xsl:value-of select="replace(regex-group(1), '\s+', ' ')"/>
                        </dateCreated>
                        <dateCreated point="end">
                            <xsl:value-of select="replace(regex-group(3), '\s+', ' ')"/>
                        </dateCreated>
                    </xsl:matching-substring>
                </xsl:analyze-string>
            </xsl:when>
            <xsl:when test="matches(., $approxBetweenRegEx)">
                <xsl:analyze-string select="." regex="{$approxBetweenRegEx}">
                    <xsl:matching-substring>
                        <dateCreated point="start" keyDate="yes" qualifier="approximate">
                            <xsl:value-of select="replace(regex-group(1), '\s+', ' ')"/>
                        </dateCreated>
                        <dateCreated point="end" qualifier="approximate">
                            <xsl:value-of select="replace(regex-group(3), '\s+', ' ')"/>
                        </dateCreated>
                    </xsl:matching-substring>
                </xsl:analyze-string>
            </xsl:when>
            <xsl:when test="matches(., $semicolonRegEx)">
                <xsl:analyze-string select="." regex="{$semicolonRegEx}">
                    <xsl:matching-substring>
                        <dateCreated point="start" keyDate="yes">
                            <xsl:value-of select="replace(regex-group(1), '\s+', ' ')"/>
                        </dateCreated>
                        <dateCreated point="end">
                            <xsl:value-of select="replace(regex-group(2), '\s+', ' ')"/>
                        </dateCreated>
                    </xsl:matching-substring>
                </xsl:analyze-string>
            </xsl:when>
            <xsl:when test="matches(., $semicolonYYMMDDRegEx)">
                <xsl:analyze-string select="." regex="{$semicolonYYMMDDRegEx}">
                    <xsl:matching-substring>
                        <dateCreated point="start" keyDate="yes">
                            <xsl:value-of select="replace(regex-group(1), '\s+', ' ')"/>
                        </dateCreated>
                        <dateCreated point="end">
                            <xsl:value-of select="replace(regex-group(2), '\s+', ' ')"/>
                        </dateCreated>
                    </xsl:matching-substring>
                </xsl:analyze-string>
            </xsl:when>
            <xsl:when test="matches(., $inferredRegEx) and not(matches(., '-'))">
                <xsl:analyze-string select="." regex="{$inferredRegEx}">
                    <xsl:matching-substring>
                        <dateCreated keyDate="yes" qualifier="inferred">
                            <xsl:value-of select="replace(regex-group(1), '\s+', ' ')"/>
                        </dateCreated>
                    </xsl:matching-substring>
                </xsl:analyze-string>
            </xsl:when>
            <xsl:when test="matches(., $inferredYYMMDDRegEx)">
                <xsl:analyze-string select="." regex="{$inferredYYMMDDRegEx}">
                    <xsl:matching-substring>
                        <dateCreated keyDate="yes" qualifier="inferred">
                            <xsl:value-of select="replace(regex-group(1), '\s+', ' ')"/>
                        </dateCreated>
                    </xsl:matching-substring>
                </xsl:analyze-string>
            </xsl:when>
            <xsl:when test="matches(., $orRegEx)">
                <xsl:analyze-string select="." regex="{$orRegEx}">
                    <xsl:matching-substring>
                        <dateCreated point="start" keyDate="yes" qualifier="inferred">
                            <xsl:value-of select="replace(regex-group(1), '\s+', ' ')"/>
                        </dateCreated>
                        <dateCreated point="end" qualifier="inferred">
                            <xsl:value-of select="replace(regex-group(3), '\s+', ' ')"/>
                        </dateCreated>
                    </xsl:matching-substring>
                </xsl:analyze-string>
            </xsl:when>
            <xsl:when test="matches(., $orYYYYMMDDRegEx)">
                <xsl:analyze-string select="." regex="{$orYYYYMMDDRegEx}">
                    <xsl:matching-substring>
                        <dateCreated point="start" keyDate="yes" qualifier="inferred">
                            <xsl:value-of select="replace(regex-group(1), '\s+', ' ')"/>
                        </dateCreated>
                        <dateCreated point="end" qualifier="inferred">
                            <xsl:value-of select="replace(regex-group(4), '\s+', ' ')"/>
                        </dateCreated>
                    </xsl:matching-substring>
                </xsl:analyze-string>
            </xsl:when>
            <xsl:when test="matches(., $historicalRegEx)">
                <xsl:analyze-string select="." regex="{$historicalRegEx}">
                    <xsl:matching-substring>
                        <dateCreated keyDate="yes">
                            <xsl:value-of select="replace(regex-group(1), '\s+', ' ')"/>
                        </dateCreated>
                    </xsl:matching-substring>
                </xsl:analyze-string>
            </xsl:when>
            <xsl:when test="matches(., $decadeRegEx)">
                <xsl:analyze-string select="." regex="{$decadeRegEx}">
                    <xsl:matching-substring>
                        <dateCreated point="start" keyDate="yes" qualifier="inferred">
                            <xsl:value-of select="replace(regex-group(1), '\s+', ' ')"/>
                            <xsl:text>0</xsl:text>
                        </dateCreated>
                        <dateCreated point="end" qualifier="inferred">
                            <xsl:value-of select="replace(regex-group(1), '\s+', ' ')"/>
                            <xsl:text>9</xsl:text>
                        </dateCreated>
                    </xsl:matching-substring>
                </xsl:analyze-string>
            </xsl:when>
            <xsl:when test="matches(., $decadeQuestionableRegEx)">
                <xsl:analyze-string select="." regex="{$decadeQuestionableRegEx}">
                    <xsl:matching-substring>
                        <dateCreated point="start" keyDate="yes" qualifier="questionable">
                            <xsl:value-of select="replace(regex-group(1), '\s+', ' ')"/>
                            <xsl:text>0</xsl:text>
                        </dateCreated>
                        <dateCreated point="end" qualifier="questionable">
                            <xsl:value-of select="replace(regex-group(1), '\s+', ' ')"/>
                            <xsl:text>9</xsl:text>
                        </dateCreated>
                    </xsl:matching-substring>
                </xsl:analyze-string>
            </xsl:when>
            <xsl:when test="matches(., $priorRegEx)">
                <xsl:analyze-string select="." regex="{$priorRegEx}">
                    <xsl:matching-substring>
                        <dateCreated keyDate="yes" point="end">
                            <xsl:value-of select="replace(regex-group(1), '\s+', ' ')"/>
                            <xsl:value-of select="replace(regex-group(2), '\s+', ' ')"/>
                        </dateCreated>
                    </xsl:matching-substring>
                </xsl:analyze-string>
            </xsl:when>
            <xsl:when test="matches(., 'early 20th century', 'i')">
                <dateCreated point="start" keyDate="yes" qualifier="approximate">1901</dateCreated>
                <dateCreated point="end" qualifier="approximate">1939</dateCreated>
            </xsl:when>
            <xsl:when test="matches(., 'late 20th century', 'i')">
                <dateCreated point="start" keyDate="yes" qualifier="approximate">1960</dateCreated>
                <dateCreated point="end" qualifier="approximate">2000</dateCreated>
            </xsl:when>
            <xsl:when test="matches(., 'mid-20th century', 'i')">
                <dateCreated point="start" keyDate="yes" qualifier="approximate">1930</dateCreated>
                <dateCreated point="end" qualifier="approximate">1969</dateCreated>
            </xsl:when>
            <xsl:when test="matches(., '20th century', 'i') and matches(., '19th')">
                <dateCreated point="start" keyDate="yes" qualifier="approximate">1801</dateCreated>
                <dateCreated point="end" qualifier="approximate">2000</dateCreated>
            </xsl:when>
            <xsl:when test="matches(., '20th century', 'i') and not (matches(., '19th'))">
                <dateCreated point="start" keyDate="yes" qualifier="approximate">1901</dateCreated>
                <dateCreated point="end" qualifier="approximate">2000</dateCreated>
            </xsl:when>
            <xsl:when test="matches(., 'mid-19th century', 'i')">
                <dateCreated point="start" keyDate="yes" qualifier="approximate">1830</dateCreated>
                <dateCreated point="end" qualifier="approximate">1869</dateCreated>
            </xsl:when>
            <xsl:when test="matches(., 'late 19th century', 'i')">
                <dateCreated point="start" keyDate="yes" qualifier="approximate">1860</dateCreated>
                <dateCreated point="end" qualifier="approximate">1900</dateCreated>
            </xsl:when>
            <xsl:when test="matches(., '19th century', 'i')">
                <dateCreated point="start" keyDate="yes" qualifier="approximate">1801</dateCreated>
                <dateCreated point="end" qualifier="approximate">1900</dateCreated>
            </xsl:when>
            <xsl:when test="matches(., '18th century', 'i')">
                <dateCreated point="start" keyDate="yes" qualifier="approximate">1701</dateCreated>
                <dateCreated point="end" qualifier="approximate">1800</dateCreated>
            </xsl:when>
            <xsl:when test="matches(., '17th century', 'i')">
                <dateCreated point="start" keyDate="yes" qualifier="approximate">1601</dateCreated>
                <dateCreated point="end" qualifier="approximate">1700</dateCreated>
            </xsl:when>
            <xsl:when test="matches(., '16th century', 'i')">
                <dateCreated point="start" keyDate="yes" qualifier="approximate">1501</dateCreated>
                <dateCreated point="end" qualifier="approximate">1600</dateCreated>
            </xsl:when>
            <xsl:when test="matches(., '15th century', 'i')">
                <dateCreated point="start" keyDate="yes" qualifier="approximate">1401</dateCreated>
                <dateCreated point="end" qualifier="approximate">1500</dateCreated>
            </xsl:when>
            <xsl:when test="matches(., '14th century', 'i')">
                <dateCreated point="start" keyDate="yes" qualifier="approximate">1301</dateCreated>
                <dateCreated point="end" qualifier="approximate">1400</dateCreated>
            </xsl:when>
            <xsl:when test="matches(., 'no date', 'i')">
                <!-- delete node by doing nothing on the match -->
            </xsl:when>
            <xsl:when test="matches(., 'Uncertain', 'i')">
                <!-- delete node by doing nothing on the match -->
            </xsl:when>
            <xsl:otherwise>
                <dateCreated keyDate="yes">
                    <xsl:value-of select="."/>
                </dateCreated>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
</xsl:stylesheet>