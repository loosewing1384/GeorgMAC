<?xml version="1.0" encoding="UTF-8"?>
<!-- Muestra estadísticas para los elementos seg y gap con atributos @cert. -->

<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"   
  xmlns:xs="http://www.w3.org/2001/XMLSchema"   
  xmlns:tei="http://www.tei-c.org/ns/1.0"   
  xmlns:map="http://www.w3.org/2005/xpath-functions/map"   
  xmlns:math="http://www.w3.org/2005/xpath-functions/math"   
  exclude-result-prefixes="xs map tei math"   
  xpath-default-namespace="http://www.tei-c.org/ns/1.0"   
  version="3.0">
  
  <xsl:output method="text" indent="no"/>
  <xsl:strip-space elements="*"/>
  <xsl:template match="text()">
    <xsl:value-of select="replace(., '\s+', ' ')"/>
  </xsl:template>
  
  <!-- Main template -->
  <xsl:template match="/">
    <!-- Convert cert attribute values to numeric values -->
    <xsl:variable name="all-elements" select="//*[self::seg or self::gap][@cert]"/>
    <xsl:variable name="cert-values" as="xs:double*">
      <xsl:for-each select="$all-elements">
        <xsl:choose>
          <xsl:when test="@cert = 'high'">3</xsl:when>
          <xsl:when test="@cert = 'medium'">2</xsl:when>
          <xsl:when test="@cert = 'low'">1</xsl:when>
          <xsl:otherwise>0</xsl:otherwise>
        </xsl:choose>
      </xsl:for-each>
    </xsl:variable>
    
    <!-- Calculate statistics -->
    <xsl:variable name="count" select="count($cert-values)"/>
    <xsl:variable name="sum" select="sum($cert-values)"/>
    <xsl:variable name="average" select="$sum div $count"/>
    
    <xsl:variable name="squared-deviations" as="xs:double*">
      <xsl:for-each select="$cert-values">
        <xsl:value-of select="math:pow(. - $average, 2)"/>
      </xsl:for-each>
    </xsl:variable>
    
    <xsl:variable name="variance" select="sum($squared-deviations) div ($count - 1)"/>
    <xsl:variable name="std-dev" select="math:sqrt($variance)"/>
    
    <!-- Frequency counts -->
    <xsl:variable name="count-high"   select="count($all-elements[@cert = 'high'])"/>
    <xsl:variable name="count-medium" select="count($all-elements[@cert = 'medium'])"/>
    <xsl:variable name="count-low"    select="count($all-elements[@cert = 'low'])"/>
    <xsl:variable name="pct-high"     select="$count-high   div $count * 100"/>
    <xsl:variable name="pct-medium"   select="$count-medium div $count * 100"/>
    <xsl:variable name="pct-low"      select="$count-low    div $count * 100"/>

    <!-- Output results -->
    <xsl:text>Traducción de </xsl:text>
    <xsl:value-of select="/tei:TEI/tei:teiHeader[1]/tei:fileDesc[1]/tei:titleStmt[1]/tei:editor[1]"/>
    <xsl:text>(</xsl:text>
    <xsl:value-of select="/tei:TEI/tei:teiHeader[1]/tei:fileDesc[1]/tei:sourceDesc[1]/tei:biblStruct[1]/tei:monogr[1]/tei:imprint[1]/tei:date[1]"/>
    <xsl:text>)&#xa;&#xa;</xsl:text>
    <xsl:text>Estadísticas para los elementos &lt;seg&gt; y &lt;gap&gt; con atributos @cert:&#xa;&#xa;</xsl:text>
    <xsl:text>Número de elementos: </xsl:text><xsl:value-of select="$count"/><xsl:text>&#xa;</xsl:text>
    <xsl:text>Promedio:            </xsl:text><xsl:value-of select="format-number($average, '0.000')"/><xsl:text>&#xa;</xsl:text>
    <xsl:text>Desviación estándar: </xsl:text><xsl:value-of select="format-number($std-dev, '0.000')"/><xsl:text>&#xa;</xsl:text>
    <xsl:text>Varianza:            </xsl:text><xsl:value-of select="format-number($variance, '0.000')"/><xsl:text>&#xa;&#xa;</xsl:text>
    <xsl:text>Distribución de frecuencias:&#xa;</xsl:text>
    <xsl:text>  high:   </xsl:text><xsl:value-of select="$count-high"/><xsl:text>  (</xsl:text><xsl:value-of select="format-number($pct-high,   '0.0')"/><xsl:text>%)&#xa;</xsl:text>
    <xsl:text>  medium: </xsl:text><xsl:value-of select="$count-medium"/><xsl:text>  (</xsl:text><xsl:value-of select="format-number($pct-medium, '0.0')"/><xsl:text>%)&#xa;</xsl:text>
    <xsl:text>  low:    </xsl:text><xsl:value-of select="$count-low"/><xsl:text>  (</xsl:text><xsl:value-of select="format-number($pct-low,    '0.0')"/><xsl:text>%)&#xa;</xsl:text>
  </xsl:template>
  
</xsl:stylesheet>