<?xml version="1.0" encoding="UTF-8"?>
<!--
This file was generated by Altova MapForce 2015r4

YOU SHOULD NOT MODIFY THIS FILE, BECAUSE IT WILL BE
OVERWRITTEN WHEN YOU RE-RUN CODE GENERATION.

Refer to the Altova MapForce Documentation for further details.
http://www.altova.com/mapforce
-->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:agt="http://www.altova.com/Mapforce/agt" xmlns:xs="http://www.w3.org/2001/XMLSchema" exclude-result-prefixes="agt xs">
	<xsl:output method="xml" encoding="UTF-8" indent="yes"/>
	<xsl:template name="agt:MapToGeneric_Windstorm_CanLoc_A_var66_create_rec">
		<xsl:param name="var65_current"/>
		<rec>
			<xsl:variable name="var1_ACCNTNUM">
				<xsl:if test="$var65_current/@ACCNTNUM">
					<xsl:value-of select="'1'"/>
				</xsl:if>
			</xsl:variable>
			<xsl:attribute name="ACCNTNUM">
				<xsl:choose>
					<xsl:when test="string(boolean(string($var1_ACCNTNUM))) != 'false'">
						<xsl:value-of select="string($var65_current/@ACCNTNUM)"/>
					</xsl:when>
					<xsl:otherwise>
						<xsl:value-of select="string('0')"/>
					</xsl:otherwise>
				</xsl:choose>
			</xsl:attribute>
			<xsl:variable name="var2_LOCNUM">
				<xsl:if test="$var65_current/@LOCNUM">
					<xsl:value-of select="'1'"/>
				</xsl:if>
			</xsl:variable>
			<xsl:attribute name="LOCNUM">
				<xsl:choose>
					<xsl:when test="string(boolean(string($var2_LOCNUM))) != 'false'">
						<xsl:value-of select="string($var65_current/@LOCNUM)"/>
					</xsl:when>
					<xsl:otherwise>
						<xsl:value-of select="string('0')"/>
					</xsl:otherwise>
				</xsl:choose>
			</xsl:attribute>
			<xsl:variable name="var3_POSTALCODE">
				<xsl:if test="$var65_current/@POSTALCODE">
					<xsl:value-of select="'1'"/>
				</xsl:if>
			</xsl:variable>
			<xsl:attribute name="POSTALCODE">
				<xsl:choose>
					<xsl:when test="string(boolean(string($var3_POSTALCODE))) != 'false'">
						<xsl:value-of select="string($var65_current/@POSTALCODE)"/>
					</xsl:when>
					<xsl:otherwise>
						<xsl:value-of select="string('0')"/>
					</xsl:otherwise>
				</xsl:choose>
			</xsl:attribute>
			<xsl:variable name="var4_COUNTY">
				<xsl:if test="$var65_current/@COUNTY">
					<xsl:value-of select="'1'"/>
				</xsl:if>
			</xsl:variable>
			<xsl:attribute name="COUNTY">
				<xsl:choose>
					<xsl:when test="string(boolean(string($var4_COUNTY))) != 'false'">
						<xsl:value-of select="string($var65_current/@COUNTY)"/>
					</xsl:when>
					<xsl:otherwise>
						<xsl:value-of select="string('0')"/>
					</xsl:otherwise>
				</xsl:choose>
			</xsl:attribute>
			<xsl:variable name="var5_COUNTYCODE">
				<xsl:if test="$var65_current/@COUNTYCODE">
					<xsl:value-of select="'1'"/>
				</xsl:if>
			</xsl:variable>
			<xsl:attribute name="COUNTYCODE">
				<xsl:choose>
					<xsl:when test="string(boolean(string($var5_COUNTYCODE))) != 'false'">
						<xsl:value-of select="string($var65_current/@COUNTYCODE)"/>
					</xsl:when>
					<xsl:otherwise>
						<xsl:value-of select="string('0')"/>
					</xsl:otherwise>
				</xsl:choose>
			</xsl:attribute>
			<xsl:variable name="var6_CRESTA">
				<xsl:if test="$var65_current/@CRESTA">
					<xsl:value-of select="'1'"/>
				</xsl:if>
			</xsl:variable>
			<xsl:attribute name="CRESTA">
				<xsl:choose>
					<xsl:when test="string(boolean(string($var6_CRESTA))) != 'false'">
						<xsl:value-of select="string($var65_current/@CRESTA)"/>
					</xsl:when>
					<xsl:otherwise>
						<xsl:value-of select="string('0')"/>
					</xsl:otherwise>
				</xsl:choose>
			</xsl:attribute>
			<xsl:variable name="var7_CITY">
				<xsl:if test="$var65_current/@CITY">
					<xsl:value-of select="'1'"/>
				</xsl:if>
			</xsl:variable>
			<xsl:attribute name="CITY">
				<xsl:choose>
					<xsl:when test="string(boolean(string($var7_CITY))) != 'false'">
						<xsl:value-of select="string($var65_current/@CITY)"/>
					</xsl:when>
					<xsl:otherwise>
						<xsl:value-of select="string('0')"/>
					</xsl:otherwise>
				</xsl:choose>
			</xsl:attribute>
			<xsl:variable name="var8_CITYCODE">
				<xsl:if test="$var65_current/@CITYCODE">
					<xsl:value-of select="'1'"/>
				</xsl:if>
			</xsl:variable>
			<xsl:attribute name="CITYCODE">
				<xsl:choose>
					<xsl:when test="string(boolean(string($var8_CITYCODE))) != 'false'">
						<xsl:value-of select="string($var65_current/@CITYCODE)"/>
					</xsl:when>
					<xsl:otherwise>
						<xsl:value-of select="string('0')"/>
					</xsl:otherwise>
				</xsl:choose>
			</xsl:attribute>
			<xsl:variable name="var9_STATE">
				<xsl:if test="$var65_current/@STATE">
					<xsl:value-of select="'1'"/>
				</xsl:if>
			</xsl:variable>
			<xsl:attribute name="STATE">
				<xsl:choose>
					<xsl:when test="string(boolean(string($var9_STATE))) != 'false'">
						<xsl:value-of select="string($var65_current/@STATE)"/>
					</xsl:when>
					<xsl:otherwise>
						<xsl:value-of select="string('0')"/>
					</xsl:otherwise>
				</xsl:choose>
			</xsl:attribute>
			<xsl:variable name="var10_STATECODE">
				<xsl:if test="$var65_current/@STATECODE">
					<xsl:value-of select="'1'"/>
				</xsl:if>
			</xsl:variable>
			<xsl:attribute name="STATECODE">
				<xsl:choose>
					<xsl:when test="string(boolean(string($var10_STATECODE))) != 'false'">
						<xsl:value-of select="string($var65_current/@STATECODE)"/>
					</xsl:when>
					<xsl:otherwise>
						<xsl:value-of select="string('0')"/>
					</xsl:otherwise>
				</xsl:choose>
			</xsl:attribute>
			<xsl:variable name="var11_ADDRMATCH">
				<xsl:if test="$var65_current/@ADDRMATCH">
					<xsl:value-of select="'1'"/>
				</xsl:if>
			</xsl:variable>
			<xsl:attribute name="ADDRMATCH">
				<xsl:choose>
					<xsl:when test="string(boolean(string($var11_ADDRMATCH))) != 'false'">
						<xsl:value-of select="string($var65_current/@ADDRMATCH)"/>
					</xsl:when>
					<xsl:otherwise>
						<xsl:value-of select="string('0')"/>
					</xsl:otherwise>
				</xsl:choose>
			</xsl:attribute>
			<xsl:variable name="var12_COUNTRY">
				<xsl:if test="$var65_current/@COUNTRY">
					<xsl:value-of select="'1'"/>
				</xsl:if>
			</xsl:variable>
			<xsl:attribute name="COUNTRY">
				<xsl:choose>
					<xsl:when test="string(boolean(string($var12_COUNTRY))) != 'false'">
						<xsl:value-of select="string($var65_current/@COUNTRY)"/>
					</xsl:when>
					<xsl:otherwise>
						<xsl:value-of select="string('0')"/>
					</xsl:otherwise>
				</xsl:choose>
			</xsl:attribute>
			<xsl:variable name="var13_COUNTRYGEOID">
				<xsl:if test="$var65_current/@COUNTRYGEOID">
					<xsl:value-of select="'1'"/>
				</xsl:if>
			</xsl:variable>
			<xsl:attribute name="COUNTRYGEOID">
				<xsl:choose>
					<xsl:when test="string(boolean(string($var13_COUNTRYGEOID))) != 'false'">
						<xsl:value-of select="string($var65_current/@COUNTRYGEOID)"/>
					</xsl:when>
					<xsl:otherwise>
						<xsl:value-of select="string('0')"/>
					</xsl:otherwise>
				</xsl:choose>
			</xsl:attribute>
			<xsl:variable name="var14_CNTRYSCHEME">
				<xsl:if test="$var65_current/@CNTRYSCHEME">
					<xsl:value-of select="'1'"/>
				</xsl:if>
			</xsl:variable>
			<xsl:attribute name="CNTRYSCHEME">
				<xsl:choose>
					<xsl:when test="string(boolean(string($var14_CNTRYSCHEME))) != 'false'">
						<xsl:value-of select="string($var65_current/@CNTRYSCHEME)"/>
					</xsl:when>
					<xsl:otherwise>
						<xsl:value-of select="string('0')"/>
					</xsl:otherwise>
				</xsl:choose>
			</xsl:attribute>
			<xsl:variable name="var15_CNTRYCODE">
				<xsl:if test="$var65_current/@CNTRYCODE">
					<xsl:value-of select="'1'"/>
				</xsl:if>
			</xsl:variable>
			<xsl:attribute name="CNTRYCODE">
				<xsl:choose>
					<xsl:when test="string(boolean(string($var15_CNTRYCODE))) != 'false'">
						<xsl:value-of select="string($var65_current/@CNTRYCODE)"/>
					</xsl:when>
					<xsl:otherwise>
						<xsl:value-of select="string('0')"/>
					</xsl:otherwise>
				</xsl:choose>
			</xsl:attribute>
			<xsl:variable name="var16_LATITUDE">
				<xsl:if test="$var65_current/@LATITUDE">
					<xsl:value-of select="'1'"/>
				</xsl:if>
			</xsl:variable>
			<xsl:attribute name="LATITUDE">
				<xsl:choose>
					<xsl:when test="string(boolean(string($var16_LATITUDE))) != 'false'">
						<xsl:value-of select="string($var65_current/@LATITUDE)"/>
					</xsl:when>
					<xsl:otherwise>
						<xsl:value-of select="string('0')"/>
					</xsl:otherwise>
				</xsl:choose>
			</xsl:attribute>
			<xsl:variable name="var17_LONGITUDE">
				<xsl:if test="$var65_current/@LONGITUDE">
					<xsl:value-of select="'1'"/>
				</xsl:if>
			</xsl:variable>
			<xsl:attribute name="LONGITUDE">
				<xsl:choose>
					<xsl:when test="string(boolean(string($var17_LONGITUDE))) != 'false'">
						<xsl:value-of select="string($var65_current/@LONGITUDE)"/>
					</xsl:when>
					<xsl:otherwise>
						<xsl:value-of select="string('0')"/>
					</xsl:otherwise>
				</xsl:choose>
			</xsl:attribute>
			<xsl:variable name="var18_BLDGSCHEME">
				<xsl:if test="$var65_current/@BLDGSCHEME">
					<xsl:value-of select="'1'"/>
				</xsl:if>
			</xsl:variable>
			<xsl:attribute name="BLDGSCHEME">
				<xsl:choose>
					<xsl:when test="string(boolean(string($var18_BLDGSCHEME))) != 'false'">
						<xsl:value-of select="string($var65_current/@BLDGSCHEME)"/>
					</xsl:when>
					<xsl:otherwise>
						<xsl:value-of select="string('0')"/>
					</xsl:otherwise>
				</xsl:choose>
			</xsl:attribute>
			<xsl:variable name="var19_BLDGCLASS">
				<xsl:if test="$var65_current/@BLDGCLASS">
					<xsl:value-of select="'1'"/>
				</xsl:if>
			</xsl:variable>
			<xsl:attribute name="BLDGCLASS">
				<xsl:choose>
					<xsl:when test="string(boolean(string($var19_BLDGCLASS))) != 'false'">
						<xsl:value-of select="string($var65_current/@BLDGCLASS)"/>
					</xsl:when>
					<xsl:otherwise>
						<xsl:value-of select="string('0')"/>
					</xsl:otherwise>
				</xsl:choose>
			</xsl:attribute>
			<xsl:variable name="var20_OCCSCHEME">
				<xsl:if test="$var65_current/@OCCSCHEME">
					<xsl:value-of select="'1'"/>
				</xsl:if>
			</xsl:variable>
			<xsl:attribute name="OCCSCHEME">
				<xsl:choose>
					<xsl:when test="string(boolean(string($var20_OCCSCHEME))) != 'false'">
						<xsl:value-of select="string($var65_current/@OCCSCHEME)"/>
					</xsl:when>
					<xsl:otherwise>
						<xsl:value-of select="string('0')"/>
					</xsl:otherwise>
				</xsl:choose>
			</xsl:attribute>
			<xsl:variable name="var21_OCCTYPE">
				<xsl:if test="$var65_current/@OCCTYPE">
					<xsl:value-of select="'1'"/>
				</xsl:if>
			</xsl:variable>
			<xsl:attribute name="OCCTYPE">
				<xsl:choose>
					<xsl:when test="string(boolean(string($var21_OCCTYPE))) != 'false'">
						<xsl:value-of select="string($var65_current/@OCCTYPE)"/>
					</xsl:when>
					<xsl:otherwise>
						<xsl:value-of select="string('0')"/>
					</xsl:otherwise>
				</xsl:choose>
			</xsl:attribute>
			<xsl:variable name="var22_YEARBUILT">
				<xsl:if test="$var65_current/@YEARBUILT">
					<xsl:value-of select="'1'"/>
				</xsl:if>
			</xsl:variable>
			<xsl:attribute name="YEARBUILT">
				<xsl:choose>
					<xsl:when test="string(boolean(string($var22_YEARBUILT))) != 'false'">
						<xsl:value-of select="string($var65_current/@YEARBUILT)"/>
					</xsl:when>
					<xsl:otherwise>
						<xsl:value-of select="'12/31/9999'"/>
					</xsl:otherwise>
				</xsl:choose>
			</xsl:attribute>
			<xsl:variable name="var23_YEARUPGRAD">
				<xsl:if test="$var65_current/@YEARUPGRAD">
					<xsl:value-of select="'1'"/>
				</xsl:if>
			</xsl:variable>
			<xsl:attribute name="YEARUPGRAD">
				<xsl:choose>
					<xsl:when test="string(boolean(string($var23_YEARUPGRAD))) != 'false'">
						<xsl:value-of select="string($var65_current/@YEARUPGRAD)"/>
					</xsl:when>
					<xsl:otherwise>
						<xsl:value-of select="'12/31/9999'"/>
					</xsl:otherwise>
				</xsl:choose>
			</xsl:attribute>
			<xsl:variable name="var24_NUMSTORIES">
				<xsl:if test="$var65_current/@NUMSTORIES">
					<xsl:value-of select="'1'"/>
				</xsl:if>
			</xsl:variable>
			<xsl:attribute name="NUMSTORIES">
				<xsl:choose>
					<xsl:when test="string(boolean(string($var24_NUMSTORIES))) != 'false'">
						<xsl:value-of select="string($var65_current/@NUMSTORIES)"/>
					</xsl:when>
					<xsl:otherwise>
						<xsl:value-of select="string('0')"/>
					</xsl:otherwise>
				</xsl:choose>
			</xsl:attribute>
			<xsl:variable name="var25_NUMBLDGS">
				<xsl:if test="$var65_current/@NUMBLDGS">
					<xsl:value-of select="'1'"/>
				</xsl:if>
			</xsl:variable>
			<xsl:attribute name="NUMBLDGS">
				<xsl:choose>
					<xsl:when test="string(boolean(string($var25_NUMBLDGS))) != 'false'">
						<xsl:value-of select="string($var65_current/@NUMBLDGS)"/>
					</xsl:when>
					<xsl:otherwise>
						<xsl:value-of select="'1'"/>
					</xsl:otherwise>
				</xsl:choose>
			</xsl:attribute>
			<xsl:variable name="var26_WSCVVAL">
				<xsl:if test="$var65_current/@WSCV1VAL">
					<xsl:value-of select="'1'"/>
				</xsl:if>
			</xsl:variable>
			<xsl:attribute name="WSCV1VAL">
				<xsl:choose>
					<xsl:when test="string(boolean(string($var26_WSCVVAL))) != 'false'">
						<xsl:value-of select="string($var65_current/@WSCV1VAL)"/>
					</xsl:when>
					<xsl:otherwise>
						<xsl:value-of select="string('0')"/>
					</xsl:otherwise>
				</xsl:choose>
			</xsl:attribute>
			<xsl:variable name="var27_WSCVVAL">
				<xsl:if test="$var65_current/@WSCV2VAL">
					<xsl:value-of select="'1'"/>
				</xsl:if>
			</xsl:variable>
			<xsl:attribute name="WSCV2VAL">
				<xsl:choose>
					<xsl:when test="string(boolean(string($var27_WSCVVAL))) != 'false'">
						<xsl:value-of select="string($var65_current/@WSCV2VAL)"/>
					</xsl:when>
					<xsl:otherwise>
						<xsl:value-of select="string('0')"/>
					</xsl:otherwise>
				</xsl:choose>
			</xsl:attribute>
			<xsl:variable name="var28_WSCVVAL">
				<xsl:if test="$var65_current/@WSCV3VAL">
					<xsl:value-of select="'1'"/>
				</xsl:if>
			</xsl:variable>
			<xsl:attribute name="WSCV3VAL">
				<xsl:choose>
					<xsl:when test="string(boolean(string($var28_WSCVVAL))) != 'false'">
						<xsl:value-of select="string($var65_current/@WSCV3VAL)"/>
					</xsl:when>
					<xsl:otherwise>
						<xsl:value-of select="string('0')"/>
					</xsl:otherwise>
				</xsl:choose>
			</xsl:attribute>
			<xsl:variable name="var29_WSCVVAL">
				<xsl:if test="$var65_current/@WSCV4VAL">
					<xsl:value-of select="'1'"/>
				</xsl:if>
			</xsl:variable>
			<xsl:attribute name="WSCV4VAL">
				<xsl:choose>
					<xsl:when test="string(boolean(string($var29_WSCVVAL))) != 'false'">
						<xsl:value-of select="string($var65_current/@WSCV4VAL)"/>
					</xsl:when>
					<xsl:otherwise>
						<xsl:value-of select="string('0')"/>
					</xsl:otherwise>
				</xsl:choose>
			</xsl:attribute>
			<xsl:variable name="var30_WSCVVAL">
				<xsl:if test="$var65_current/@WSCV5VAL">
					<xsl:value-of select="'1'"/>
				</xsl:if>
			</xsl:variable>
			<xsl:attribute name="WSCV5VAL">
				<xsl:choose>
					<xsl:when test="string(boolean(string($var30_WSCVVAL))) != 'false'">
						<xsl:value-of select="string($var65_current/@WSCV5VAL)"/>
					</xsl:when>
					<xsl:otherwise>
						<xsl:value-of select="string('0')"/>
					</xsl:otherwise>
				</xsl:choose>
			</xsl:attribute>
			<xsl:variable name="var31_WSCVVAL">
				<xsl:if test="$var65_current/@WSCV6VAL">
					<xsl:value-of select="'1'"/>
				</xsl:if>
			</xsl:variable>
			<xsl:attribute name="WSCV6VAL">
				<xsl:choose>
					<xsl:when test="string(boolean(string($var31_WSCVVAL))) != 'false'">
						<xsl:value-of select="string($var65_current/@WSCV6VAL)"/>
					</xsl:when>
					<xsl:otherwise>
						<xsl:value-of select="string('0')"/>
					</xsl:otherwise>
				</xsl:choose>
			</xsl:attribute>
			<xsl:variable name="var32_WSCVVAL">
				<xsl:if test="$var65_current/@WSCV7VAL">
					<xsl:value-of select="'1'"/>
				</xsl:if>
			</xsl:variable>
			<xsl:attribute name="WSCV7VAL">
				<xsl:choose>
					<xsl:when test="string(boolean(string($var32_WSCVVAL))) != 'false'">
						<xsl:value-of select="string($var65_current/@WSCV7VAL)"/>
					</xsl:when>
					<xsl:otherwise>
						<xsl:value-of select="string('0')"/>
					</xsl:otherwise>
				</xsl:choose>
			</xsl:attribute>
			<xsl:variable name="var33_WSCVVAL">
				<xsl:if test="$var65_current/@WSCV8VAL">
					<xsl:value-of select="'1'"/>
				</xsl:if>
			</xsl:variable>
			<xsl:attribute name="WSCV8VAL">
				<xsl:choose>
					<xsl:when test="string(boolean(string($var33_WSCVVAL))) != 'false'">
						<xsl:value-of select="string($var65_current/@WSCV8VAL)"/>
					</xsl:when>
					<xsl:otherwise>
						<xsl:value-of select="string('0')"/>
					</xsl:otherwise>
				</xsl:choose>
			</xsl:attribute>
			<xsl:variable name="var34_WSCVVAL">
				<xsl:if test="$var65_current/@WSCV9VAL">
					<xsl:value-of select="'1'"/>
				</xsl:if>
			</xsl:variable>
			<xsl:attribute name="WSCV9VAL">
				<xsl:choose>
					<xsl:when test="string(boolean(string($var34_WSCVVAL))) != 'false'">
						<xsl:value-of select="string($var65_current/@WSCV9VAL)"/>
					</xsl:when>
					<xsl:otherwise>
						<xsl:value-of select="string('0')"/>
					</xsl:otherwise>
				</xsl:choose>
			</xsl:attribute>
			<xsl:variable name="var35_WSCVVAL">
				<xsl:if test="$var65_current/@WSCV10VAL">
					<xsl:value-of select="'1'"/>
				</xsl:if>
			</xsl:variable>
			<xsl:attribute name="WSCV10VAL">
				<xsl:choose>
					<xsl:when test="string(boolean(string($var35_WSCVVAL))) != 'false'">
						<xsl:value-of select="string($var65_current/@WSCV10VAL)"/>
					</xsl:when>
					<xsl:otherwise>
						<xsl:value-of select="string('0')"/>
					</xsl:otherwise>
				</xsl:choose>
			</xsl:attribute>
			<xsl:variable name="var36_WSCVLIMIT">
				<xsl:if test="$var65_current/@WSCV1LIMIT">
					<xsl:value-of select="'1'"/>
				</xsl:if>
			</xsl:variable>
			<xsl:attribute name="WSCV1LIMIT">
				<xsl:choose>
					<xsl:when test="string(boolean(string($var36_WSCVLIMIT))) != 'false'">
						<xsl:value-of select="string($var65_current/@WSCV1LIMIT)"/>
					</xsl:when>
					<xsl:otherwise>
						<xsl:value-of select="string('0')"/>
					</xsl:otherwise>
				</xsl:choose>
			</xsl:attribute>
			<xsl:variable name="var37_WSCVLIMIT">
				<xsl:if test="$var65_current/@WSCV2LIMIT">
					<xsl:value-of select="'1'"/>
				</xsl:if>
			</xsl:variable>
			<xsl:attribute name="WSCV2LIMIT">
				<xsl:choose>
					<xsl:when test="string(boolean(string($var37_WSCVLIMIT))) != 'false'">
						<xsl:value-of select="string($var65_current/@WSCV2LIMIT)"/>
					</xsl:when>
					<xsl:otherwise>
						<xsl:value-of select="string('0')"/>
					</xsl:otherwise>
				</xsl:choose>
			</xsl:attribute>
			<xsl:variable name="var38_WSCVLIMIT">
				<xsl:if test="$var65_current/@WSCV3LIMIT">
					<xsl:value-of select="'1'"/>
				</xsl:if>
			</xsl:variable>
			<xsl:attribute name="WSCV3LIMIT">
				<xsl:choose>
					<xsl:when test="string(boolean(string($var38_WSCVLIMIT))) != 'false'">
						<xsl:value-of select="string($var65_current/@WSCV3LIMIT)"/>
					</xsl:when>
					<xsl:otherwise>
						<xsl:value-of select="string('0')"/>
					</xsl:otherwise>
				</xsl:choose>
			</xsl:attribute>
			<xsl:variable name="var39_WSCVLIMIT">
				<xsl:if test="$var65_current/@WSCV4LIMIT">
					<xsl:value-of select="'1'"/>
				</xsl:if>
			</xsl:variable>
			<xsl:attribute name="WSCV4LIMIT">
				<xsl:choose>
					<xsl:when test="string(boolean(string($var39_WSCVLIMIT))) != 'false'">
						<xsl:value-of select="string($var65_current/@WSCV4LIMIT)"/>
					</xsl:when>
					<xsl:otherwise>
						<xsl:value-of select="string('0')"/>
					</xsl:otherwise>
				</xsl:choose>
			</xsl:attribute>
			<xsl:variable name="var40_WSCVLIMIT">
				<xsl:if test="$var65_current/@WSCV5LIMIT">
					<xsl:value-of select="'1'"/>
				</xsl:if>
			</xsl:variable>
			<xsl:attribute name="WSCV5LIMIT">
				<xsl:choose>
					<xsl:when test="string(boolean(string($var40_WSCVLIMIT))) != 'false'">
						<xsl:value-of select="string($var65_current/@WSCV5LIMIT)"/>
					</xsl:when>
					<xsl:otherwise>
						<xsl:value-of select="string('0')"/>
					</xsl:otherwise>
				</xsl:choose>
			</xsl:attribute>
			<xsl:variable name="var41_WSCVLIMIT">
				<xsl:if test="$var65_current/@WSCV6LIMIT">
					<xsl:value-of select="'1'"/>
				</xsl:if>
			</xsl:variable>
			<xsl:attribute name="WSCV6LIMIT">
				<xsl:choose>
					<xsl:when test="string(boolean(string($var41_WSCVLIMIT))) != 'false'">
						<xsl:value-of select="string($var65_current/@WSCV6LIMIT)"/>
					</xsl:when>
					<xsl:otherwise>
						<xsl:value-of select="string('0')"/>
					</xsl:otherwise>
				</xsl:choose>
			</xsl:attribute>
			<xsl:variable name="var42_WSCVLIMIT">
				<xsl:if test="$var65_current/@WSCV7LIMIT">
					<xsl:value-of select="'1'"/>
				</xsl:if>
			</xsl:variable>
			<xsl:attribute name="WSCV7LIMIT">
				<xsl:choose>
					<xsl:when test="string(boolean(string($var42_WSCVLIMIT))) != 'false'">
						<xsl:value-of select="string($var65_current/@WSCV7LIMIT)"/>
					</xsl:when>
					<xsl:otherwise>
						<xsl:value-of select="string('0')"/>
					</xsl:otherwise>
				</xsl:choose>
			</xsl:attribute>
			<xsl:variable name="var43_WSCVLIMIT">
				<xsl:if test="$var65_current/@WSCV8LIMIT">
					<xsl:value-of select="'1'"/>
				</xsl:if>
			</xsl:variable>
			<xsl:attribute name="WSCV8LIMIT">
				<xsl:choose>
					<xsl:when test="string(boolean(string($var43_WSCVLIMIT))) != 'false'">
						<xsl:value-of select="string($var65_current/@WSCV8LIMIT)"/>
					</xsl:when>
					<xsl:otherwise>
						<xsl:value-of select="string('0')"/>
					</xsl:otherwise>
				</xsl:choose>
			</xsl:attribute>
			<xsl:variable name="var44_WSCVLIMIT">
				<xsl:if test="$var65_current/@WSCV9LIMIT">
					<xsl:value-of select="'1'"/>
				</xsl:if>
			</xsl:variable>
			<xsl:attribute name="WSCV9LIMIT">
				<xsl:choose>
					<xsl:when test="string(boolean(string($var44_WSCVLIMIT))) != 'false'">
						<xsl:value-of select="string($var65_current/@WSCV9LIMIT)"/>
					</xsl:when>
					<xsl:otherwise>
						<xsl:value-of select="string('0')"/>
					</xsl:otherwise>
				</xsl:choose>
			</xsl:attribute>
			<xsl:variable name="var45_WSCVLMT">
				<xsl:if test="$var65_current/@WSCV10LMT">
					<xsl:value-of select="'1'"/>
				</xsl:if>
			</xsl:variable>
			<xsl:attribute name="WSCV10LMT">
				<xsl:choose>
					<xsl:when test="string(boolean(string($var45_WSCVLMT))) != 'false'">
						<xsl:value-of select="string($var65_current/@WSCV10LMT)"/>
					</xsl:when>
					<xsl:otherwise>
						<xsl:value-of select="string('0')"/>
					</xsl:otherwise>
				</xsl:choose>
			</xsl:attribute>
			<xsl:variable name="var46_WSCVDED">
				<xsl:if test="$var65_current/@WSCV1DED">
					<xsl:value-of select="'1'"/>
				</xsl:if>
			</xsl:variable>
			<xsl:attribute name="WSCV1DED">
				<xsl:choose>
					<xsl:when test="string(boolean(string($var46_WSCVDED))) != 'false'">
						<xsl:value-of select="string($var65_current/@WSCV1DED)"/>
					</xsl:when>
					<xsl:otherwise>
						<xsl:value-of select="string('0')"/>
					</xsl:otherwise>
				</xsl:choose>
			</xsl:attribute>
			<xsl:variable name="var47_WSCVDED">
				<xsl:if test="$var65_current/@WSCV2DED">
					<xsl:value-of select="'1'"/>
				</xsl:if>
			</xsl:variable>
			<xsl:attribute name="WSCV2DED">
				<xsl:choose>
					<xsl:when test="string(boolean(string($var47_WSCVDED))) != 'false'">
						<xsl:value-of select="string($var65_current/@WSCV2DED)"/>
					</xsl:when>
					<xsl:otherwise>
						<xsl:value-of select="string('0')"/>
					</xsl:otherwise>
				</xsl:choose>
			</xsl:attribute>
			<xsl:variable name="var48_WSCVDED">
				<xsl:if test="$var65_current/@WSCV3DED">
					<xsl:value-of select="'1'"/>
				</xsl:if>
			</xsl:variable>
			<xsl:attribute name="WSCV3DED">
				<xsl:choose>
					<xsl:when test="string(boolean(string($var48_WSCVDED))) != 'false'">
						<xsl:value-of select="string($var65_current/@WSCV3DED)"/>
					</xsl:when>
					<xsl:otherwise>
						<xsl:value-of select="string('0')"/>
					</xsl:otherwise>
				</xsl:choose>
			</xsl:attribute>
			<xsl:variable name="var49_WSCVDED">
				<xsl:if test="$var65_current/@WSCV4DED">
					<xsl:value-of select="'1'"/>
				</xsl:if>
			</xsl:variable>
			<xsl:attribute name="WSCV4DED">
				<xsl:choose>
					<xsl:when test="string(boolean(string($var49_WSCVDED))) != 'false'">
						<xsl:value-of select="string($var65_current/@WSCV4DED)"/>
					</xsl:when>
					<xsl:otherwise>
						<xsl:value-of select="string('0')"/>
					</xsl:otherwise>
				</xsl:choose>
			</xsl:attribute>
			<xsl:variable name="var50_WSCVDED">
				<xsl:if test="$var65_current/@WSCV5DED">
					<xsl:value-of select="'1'"/>
				</xsl:if>
			</xsl:variable>
			<xsl:attribute name="WSCV5DED">
				<xsl:choose>
					<xsl:when test="string(boolean(string($var50_WSCVDED))) != 'false'">
						<xsl:value-of select="string($var65_current/@WSCV5DED)"/>
					</xsl:when>
					<xsl:otherwise>
						<xsl:value-of select="string('0')"/>
					</xsl:otherwise>
				</xsl:choose>
			</xsl:attribute>
			<xsl:variable name="var51_WSCVDED">
				<xsl:if test="$var65_current/@WSCV6DED">
					<xsl:value-of select="'1'"/>
				</xsl:if>
			</xsl:variable>
			<xsl:attribute name="WSCV6DED">
				<xsl:choose>
					<xsl:when test="string(boolean(string($var51_WSCVDED))) != 'false'">
						<xsl:value-of select="string($var65_current/@WSCV6DED)"/>
					</xsl:when>
					<xsl:otherwise>
						<xsl:value-of select="string('0')"/>
					</xsl:otherwise>
				</xsl:choose>
			</xsl:attribute>
			<xsl:variable name="var52_WSCVDED">
				<xsl:if test="$var65_current/@WSCV7DED">
					<xsl:value-of select="'1'"/>
				</xsl:if>
			</xsl:variable>
			<xsl:attribute name="WSCV7DED">
				<xsl:choose>
					<xsl:when test="string(boolean(string($var52_WSCVDED))) != 'false'">
						<xsl:value-of select="string($var65_current/@WSCV7DED)"/>
					</xsl:when>
					<xsl:otherwise>
						<xsl:value-of select="string('0')"/>
					</xsl:otherwise>
				</xsl:choose>
			</xsl:attribute>
			<xsl:variable name="var53_WSCVDED">
				<xsl:if test="$var65_current/@WSCV8DED">
					<xsl:value-of select="'1'"/>
				</xsl:if>
			</xsl:variable>
			<xsl:attribute name="WSCV8DED">
				<xsl:choose>
					<xsl:when test="string(boolean(string($var53_WSCVDED))) != 'false'">
						<xsl:value-of select="string($var65_current/@WSCV8DED)"/>
					</xsl:when>
					<xsl:otherwise>
						<xsl:value-of select="string('0')"/>
					</xsl:otherwise>
				</xsl:choose>
			</xsl:attribute>
			<xsl:variable name="var54_WSCVDED">
				<xsl:if test="$var65_current/@WSCV9DED">
					<xsl:value-of select="'1'"/>
				</xsl:if>
			</xsl:variable>
			<xsl:attribute name="WSCV9DED">
				<xsl:choose>
					<xsl:when test="string(boolean(string($var54_WSCVDED))) != 'false'">
						<xsl:value-of select="string($var65_current/@WSCV9DED)"/>
					</xsl:when>
					<xsl:otherwise>
						<xsl:value-of select="string('0')"/>
					</xsl:otherwise>
				</xsl:choose>
			</xsl:attribute>
			<xsl:variable name="var55_WSCVDED">
				<xsl:if test="$var65_current/@WSCV10DED">
					<xsl:value-of select="'1'"/>
				</xsl:if>
			</xsl:variable>
			<xsl:attribute name="WSCV10DED">
				<xsl:choose>
					<xsl:when test="string(boolean(string($var55_WSCVDED))) != 'false'">
						<xsl:value-of select="string($var65_current/@WSCV10DED)"/>
					</xsl:when>
					<xsl:otherwise>
						<xsl:value-of select="string('0')"/>
					</xsl:otherwise>
				</xsl:choose>
			</xsl:attribute>
			<xsl:variable name="var56_WSSITELIM">
				<xsl:if test="$var65_current/@WSSITELIM">
					<xsl:value-of select="'1'"/>
				</xsl:if>
			</xsl:variable>
			<xsl:attribute name="WSSITELIM">
				<xsl:choose>
					<xsl:when test="string(boolean(string($var56_WSSITELIM))) != 'false'">
						<xsl:value-of select="string($var65_current/@WSSITELIM)"/>
					</xsl:when>
					<xsl:otherwise>
						<xsl:value-of select="string('0')"/>
					</xsl:otherwise>
				</xsl:choose>
			</xsl:attribute>
			<xsl:variable name="var57_WSSITEDED">
				<xsl:if test="$var65_current/@WSSITEDED">
					<xsl:value-of select="'1'"/>
				</xsl:if>
			</xsl:variable>
			<xsl:attribute name="WSSITEDED">
				<xsl:choose>
					<xsl:when test="string(boolean(string($var57_WSSITEDED))) != 'false'">
						<xsl:value-of select="string($var65_current/@WSSITEDED)"/>
					</xsl:when>
					<xsl:otherwise>
						<xsl:value-of select="string('0')"/>
					</xsl:otherwise>
				</xsl:choose>
			</xsl:attribute>
			<xsl:variable name="var58_WSCOMBINEDLIM">
				<xsl:if test="$var65_current/@WSCOMBINEDLIM">
					<xsl:value-of select="'1'"/>
				</xsl:if>
			</xsl:variable>
			<xsl:attribute name="WSCOMBINEDLIM">
				<xsl:choose>
					<xsl:when test="string(boolean(string($var58_WSCOMBINEDLIM))) != 'false'">
						<xsl:value-of select="string($var65_current/@WSCOMBINEDLIM)"/>
					</xsl:when>
					<xsl:otherwise>
						<xsl:value-of select="string('0')"/>
					</xsl:otherwise>
				</xsl:choose>
			</xsl:attribute>
			<xsl:variable name="var59_WSCOMBINEDDED">
				<xsl:if test="$var65_current/@WSCOMBINEDDED">
					<xsl:value-of select="'1'"/>
				</xsl:if>
			</xsl:variable>
			<xsl:attribute name="WSCOMBINEDDED">
				<xsl:choose>
					<xsl:when test="string(boolean(string($var59_WSCOMBINEDDED))) != 'false'">
						<xsl:value-of select="string($var65_current/@WSCOMBINEDDED)"/>
					</xsl:when>
					<xsl:otherwise>
						<xsl:value-of select="string('0')"/>
					</xsl:otherwise>
				</xsl:choose>
			</xsl:attribute>
			<xsl:variable name="var60_CONDTYPE">
				<xsl:if test="$var65_current/@COND1TYPE">
					<xsl:value-of select="'1'"/>
				</xsl:if>
			</xsl:variable>
			<xsl:attribute name="COND1TYPE">
				<xsl:choose>
					<xsl:when test="string(boolean(string($var60_CONDTYPE))) != 'false'">
						<xsl:value-of select="string($var65_current/@COND1TYPE)"/>
					</xsl:when>
					<xsl:otherwise>
						<xsl:value-of select="string('0')"/>
					</xsl:otherwise>
				</xsl:choose>
			</xsl:attribute>
			<xsl:variable name="var61_CONDNAME">
				<xsl:if test="$var65_current/@COND1NAME">
					<xsl:value-of select="'1'"/>
				</xsl:if>
			</xsl:variable>
			<xsl:attribute name="COND1NAME">
				<xsl:choose>
					<xsl:when test="string(boolean(string($var61_CONDNAME))) != 'false'">
						<xsl:value-of select="string($var65_current/@COND1NAME)"/>
					</xsl:when>
					<xsl:otherwise>
						<xsl:value-of select="string('0')"/>
					</xsl:otherwise>
				</xsl:choose>
			</xsl:attribute>
			<xsl:variable name="var62_CONDDEDUCTIBLE">
				<xsl:if test="$var65_current/@COND1DEDUCTIBLE">
					<xsl:value-of select="'1'"/>
				</xsl:if>
			</xsl:variable>
			<xsl:attribute name="COND1DEDUCTIBLE">
				<xsl:choose>
					<xsl:when test="string(boolean(string($var62_CONDDEDUCTIBLE))) != 'false'">
						<xsl:value-of select="string($var65_current/@COND1DEDUCTIBLE)"/>
					</xsl:when>
					<xsl:otherwise>
						<xsl:value-of select="string('0')"/>
					</xsl:otherwise>
				</xsl:choose>
			</xsl:attribute>
			<xsl:variable name="var63_CONDLIMIT">
				<xsl:if test="$var65_current/@COND1LIMIT">
					<xsl:value-of select="'1'"/>
				</xsl:if>
			</xsl:variable>
			<xsl:attribute name="COND1LIMIT">
				<xsl:choose>
					<xsl:when test="string(boolean(string($var63_CONDLIMIT))) != 'false'">
						<xsl:value-of select="string($var65_current/@COND1LIMIT)"/>
					</xsl:when>
					<xsl:otherwise>
						<xsl:value-of select="string('0')"/>
					</xsl:otherwise>
				</xsl:choose>
			</xsl:attribute>
			<xsl:variable name="var64_ROOFGEOM">
				<xsl:if test="$var65_current/@ROOFGEOM">
					<xsl:value-of select="'1'"/>
				</xsl:if>
			</xsl:variable>
			<xsl:attribute name="ROOFGEOM">
				<xsl:choose>
					<xsl:when test="string(boolean(string($var64_ROOFGEOM))) != 'false'">
						<xsl:value-of select="string($var65_current/@ROOFGEOM)"/>
					</xsl:when>
					<xsl:otherwise>
						<xsl:value-of select="string('0')"/>
					</xsl:otherwise>
				</xsl:choose>
			</xsl:attribute>
		</rec>
	</xsl:template>
	<xsl:template name="agt:MapToGeneric_Windstorm_CanLoc_A_var68_resultof_map">
		<xsl:param name="var67_current"/>
		<xsl:for-each select="$var67_current/rec">
			<xsl:call-template name="agt:MapToGeneric_Windstorm_CanLoc_A_var66_create_rec">
				<xsl:with-param name="var65_current" select="."/>
			</xsl:call-template>
		</xsl:for-each>
	</xsl:template>
	<xsl:template match="/">
		<root>
			<xsl:attribute name="xsi:noNamespaceSchemaLocation" namespace="http://www.w3.org/2001/XMLSchema-instance">C:/Users/Administrator/Desktop/git/cookiecutter-OasisModel/OasisPiWind/flamingo/generic_model/ValidationFiles/Generic_Windstorm_CanLoc_A.xsd</xsl:attribute>
			<xsl:for-each select="root">
				<xsl:call-template name="agt:MapToGeneric_Windstorm_CanLoc_A_var68_resultof_map">
					<xsl:with-param name="var67_current" select="."/>
				</xsl:call-template>
			</xsl:for-each>
		</root>
	</xsl:template>
</xsl:stylesheet>
