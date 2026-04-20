<?xml version="1.0" encoding="UTF-8"?>
<!-- Calcula la certeza (high, medium, low) de una línea (l) a partir de los valores de certeza de sus segs componententes. Produce un nuevo documento TEI con el @cert de l correcto. (Los valores ≥ 1.67 y < 2.34 dividen el intervalo [1, 3] en tres tercios iguales.)-->

<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:xs="http://www.w3.org/2001/XMLSchema"
  xmlns:tei="http://www.tei-c.org/ns/1.0"
  xpath-default-namespace="http://www.tei-c.org/ns/1.0"
  exclude-result-prefixes="xs tei"
  version="3.0">
  
  <!-- Use the modern xsl:mode instruction for the identity transform -->
  <xsl:mode on-no-match="shallow-copy"/>
  
  <!-- Template to handle <l> elements -->
  <xsl:template match="l">
    <xsl:copy>
      <!-- Copy all existing attributes -->
      <xsl:apply-templates select="@*"/>
      
      <!-- Get all cert attributes from both seg and gap elements -->
      <xsl:variable name="all-certs" select="(seg|gap)/@cert"/>
      
      <!-- Convert categorical values to numeric weights -->
      <xsl:variable name="weighted-values" select="
        for $cert in $all-certs
        return 
        if ($cert = 'low') then 1
        else if ($cert = 'medium') then 2
        else 3 (: must be 'high' :)
        "/>
      
      <!-- Calculate the weighted average -->
      <xsl:variable name="avg-weight" select="
        if (exists($weighted-values)) 
        then avg($weighted-values)
        else 2 (: default to medium if no values :)
        "/>
      
      <!-- Convert average weight back to categorical value -->
      <xsl:variable name="cert-category" select="
        if ($avg-weight lt 1.67) then 'low'
        else if ($avg-weight lt 2.34) then 'medium'
        else 'high'
        "/>
      
      <!-- Add the calculated cert attribute -->
      <xsl:attribute name="cert" select="$cert-category"/>
      
      <!-- Process all child nodes -->
      <xsl:apply-templates select="node()"/>
    </xsl:copy>
  </xsl:template>
  
</xsl:stylesheet>