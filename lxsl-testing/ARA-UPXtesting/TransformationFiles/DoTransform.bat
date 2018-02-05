@echo off

RaptorXML xslt --xslt-version=1 --input="CanLocARA_B.xml" --output="ModelLocARA.xml" --xml-validation-error-as-warning=true %* "MappingMapToModelLocARA.xslt"
IF ERRORLEVEL 1 EXIT/B %ERRORLEVEL%
