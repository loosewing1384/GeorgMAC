<?xml version="1.0" encoding="UTF-8"?>

<!--Esta plantilla produce un .tex que contiene el texto de la traducción, con un corchete debajo que indica con su color (verde, naranja, rojo) la fidelidad de la traducción. -->

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
\title{\itshape\bfseries </xsl:text><xsl:value-of select="/TEI/teiHeader[1]/fileDesc[1]/titleStmt[1]/title[1]"/><xsl:text>}</xsl:text>

<xsl:text>
  \author{Virgilio (tr. </xsl:text>
  <xsl:value-of select="/tei:TEI/tei:teiHeader[1]/tei:fileDesc[1]/tei:titleStmt[1]/tei:editor[1][@role='translator']"/><xsl:text>, </xsl:text>
  <xsl:value-of select="/tei:TEI/tei:teiHeader[1]/tei:fileDesc[1]/tei:sourceDesc[1]/tei:biblStruct[1]/tei:monogr[1]/tei:imprint[1]/tei:date[1]"/>
  <xsl:text>)}</xsl:text>

<xsl:text>
% ===============================================
\begin{document}
\maketitle

\linespread{2.5}\selectfont

</xsl:text>
 
<xsl:apply-templates/>
<xsl:text>
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




<!--<xsl:function name="my:first-corresp-multiple-of-five" as="xs:boolean">
<xsl:param name="corresp-value" as="xs:string"/>
<xsl:sequence select="tokenize($corresp-value, '\s+')[1] cast as xs:integer mod 5 = 0"/>
</xsl:function>-->

  <xsl:function name="my:first-corresp-multiple-of-five">
    <xsl:param name="corresp-value" as="xs:string"/>
    <xsl:variable name="first-value" select="tokenize($corresp-value, '\s+')[1]"/>
    <xsl:if test="$first-value castable as xs:integer and 
      ($first-value cast as xs:integer) mod 5 = 0">
      <xsl:sequence select="$first-value cast as xs:integer"/>
    </xsl:if>
  </xsl:function>
  
  <!--         l template        -->
  <xsl:template match="l">
    <xsl:if test="my:first-corresp-multiple-of-five(@corresp) 
      or @ana='#ln'">
      <xsl:text>\sidepar{</xsl:text>
      <xsl:value-of select="@corresp"/>
      <xsl:text>}</xsl:text>
    </xsl:if>
    <xsl:text>%%%%%% v. </xsl:text>
    <xsl:value-of select="@corresp"/>
    <xsl:text> %%%%%%&#xA;</xsl:text>
    <xsl:apply-templates/>
    <xsl:text>&#xA;&#xA;</xsl:text>
  </xsl:template>
  



  <!--         seg template        -->
  <xsl:template match="seg">
    <xsl:text>\bracebelow[</xsl:text>
    <xsl:choose>
      <xsl:when test="@cert='low'">
        <xsl:text>red]</xsl:text>
      </xsl:when>
      <xsl:when test="@cert='medium'">
        <xsl:text>orange]</xsl:text>
      </xsl:when>
      <xsl:when test="@cert='high'">
        <xsl:text>green]</xsl:text>
      </xsl:when>
    </xsl:choose>
    <xsl:choose>
      <xsl:when test="@ana='#add'">
        <xsl:text>{\textcolor{Crimson}{</xsl:text>
        <xsl:apply-templates/>
        <xsl:text>}}</xsl:text>
      </xsl:when>
      <xsl:otherwise>
        <xsl:text>{</xsl:text>
        <xsl:apply-templates/>
        <xsl:text>}</xsl:text>
      </xsl:otherwise>
    </xsl:choose>
    <xsl:text> </xsl:text>
  </xsl:template>




<xsl:template match="orig[parent::choice]">
<xsl:apply-templates/>
</xsl:template>

<xsl:template match="reg[parent::choice]">
  <!--    do nothing -->
  <!--<xsl:apply-templates/>-->
</xsl:template>

<xsl:template match="gap">
<xsl:text>\circledtext{</xsl:text>
  <xsl:value-of select="@quantity"/>
<xsl:text>}</xsl:text>
</xsl:template>

<xsl:template match="note">
<!--    do nothing -->
<!--<xsl:apply-templates/>-->
</xsl:template>


</xsl:stylesheet>