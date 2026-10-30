<?xml version="1.0" encoding="UTF-8"?>
<!--Produce un .tex con una grilla que contiene, para cada línea (l), un cuadrado de color, que varía con la certeza del segmento-->
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
xmlns:xs="http://www.w3.org/2001/XMLSchema"
xmlns:tei="http://www.tei-c.org/ns/1.0"
xmlns:map="http://www.w3.org/2005/xpath-functions/map"
xmlns:my="http://example.com/mynamespace"
exclude-result-prefixes="xs map tei my" xpath-default-namespace="http://www.tei-c.org/ns/1.0"
version="3.0">

<xsl:output method="text" indent="no"/>

<!-- Strip whitespace from all elements in source document -->
<!--<xsl:strip-space elements="*"/>-->


<xsl:template match="text()">
<xsl:value-of select="replace(., '\s+', ' ')"/>
</xsl:template>

<xsl:template match="/">

<xsl:text>
\input{preamble.tex}
% ===============================================
\begin{document}
</xsl:text>
<xsl:value-of select="/tei:TEI/tei:teiHeader[1]/tei:fileDesc[1]/tei:titleStmt[1]/tei:editor[1][@role='translator']"/>
<xsl:text>(</xsl:text>
  <xsl:value-of select="/tei:TEI/tei:teiHeader[1]/tei:fileDesc[1]/tei:sourceDesc[1]/tei:biblStruct[1]/tei:monogr[1]/tei:imprint[1]/tei:date[1]"/>
<xsl:text>)
</xsl:text>
<xsl:text>
\begin{minipage}[t][\textwidth][t]{0.5\linewidth}
</xsl:text>
<xsl:apply-templates/>
  <xsl:text>
\end{minipage}
\end{document}
% ===============================================
%%% Local Variables:
%%% mode: latex
%%% jinx-languages: "es"
%%% TeX-master: t
%%% End:
</xsl:text>
</xsl:template>

<xsl:template match="teiHeader">
<!--    <xsl:apply-templates/>-->
</xsl:template>

<xsl:template match="head">
<!--    <xsl:apply-templates/>-->
</xsl:template>





  
  <!--         l template        -->
  <xsl:template match="l">
    <xsl:choose>
      <xsl:when test='@cert="low"'>
        <xsl:text>\rectlow{}</xsl:text>      
      </xsl:when>
      <xsl:when test='@cert="medium"'>
        <xsl:text>\rectmed{}</xsl:text>      
      </xsl:when>
      <xsl:when test='@cert="high"'>
        <xsl:text>\recthigh{}</xsl:text>      
      </xsl:when>
      <xsl:otherwise/>
    </xsl:choose>
  </xsl:template>
  





<xsl:template match="note">
<!--    do nothing -->
<!--<xsl:apply-templates/>-->
</xsl:template>


</xsl:stylesheet>