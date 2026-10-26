#! /usr/bin/env python3

"""Do properties check based on Jplyzer output and Schematron rules
"""

import logging
import xml.etree.ElementTree as ET
from jpylyzer import jpylyzer
from lxml import isoschematron
from lxml import etree


class PropertiesCheck:
    """Properties check class"""

    def __init__(self, schema):

        # Schematron schema used for properties check
        self.schema = schema
        # Number of errors encountered during properties check
        self.noErrors = 0
        # Number of warnings encountered during properties check
        self.noWarnings = 0
        # List with errors
        self.errors = []
        # List with warnings
        self.warnings = []
        # Properties check status
        self.status = "Fail"
        # List with failed Schematron tests
        self.schematronTestsFailed = []
        # List with failed Jpylyzer tests
        self.jpylyzerTestsFailed = []
        # Flag that indicates a paletted image
        self.palettedFlag = False

    def extractSchematron(self, report):
        """Parse output of Schematron validation and extract failed tests"""

        for elem in report.iter():
            if elem.tag == "{http://purl.oclc.org/dsdl/svrl}failed-assert":

                # Extract test definition and text description
                test = elem.get('test')

                for subelem in elem.iter():
                    if subelem.tag == "{http://purl.oclc.org/dsdl/svrl}text":
                        description = (subelem.text)
                self.schematronTestsFailed.append([test, description])

    def extractJpylyzer(self, resultJpylyzer):
        """Parse output of Jpylyzer and extract failed validation tests"""

        validationOutcome = resultJpylyzer.find("isValid").text

        if validationOutcome == "False":

            # Locate test elements

            for element in resultJpylyzer.iter():
                if element.tag == "tests":
                    testsElt = element

            # Iterate over tests element and report names of all
            # tags thatcorrespond to tests that failed

            tests = list(testsElt.iter())

            for j in tests:
                if j.text == "False":
                    self.jpylyzerTestsFailed.append(j.tag)

    def checkProperties(self, JP2):
        """Do properties check on one JP2"""

        # Initialise empty text string for error log output
        ptOutString = ""

        # Run jpylyzer on image and write result to text file
        try:
            resultJpylyzer = jpylyzer.checkOneFile(JP2)
            resultAsXML = ET.tostring(resultJpylyzer, 'UTF-8', 'xml')
            if resultJpylyzer.find('properties/jp2HeaderBox/paletteBox'):
                self.palettedFlag = True

        except Exception:
            msg = "error while running jpylyzer"
            logging.error(msg)
            self.noErrors += 1
            self.errors.append(msg)

        try:
            # Start Schematron magic ...

            schema_doc = etree.parse(self.schema)
            schematron = isoschematron.Schematron(schema_doc,
                                                store_report=True)

            # Reparse jpylyzer XML with lxml since using ET object
            # directly doesn't work
            resJpylyzerLXML = etree.fromstring(resultAsXML)

            # Validate jpylyzer output against schema
            schemaValidationResult = schematron.validate(resJpylyzerLXML)
            report = schematron.validation_report

        except Exception:
            msg = "error while running Schematron"
            logging.error(msg)
            self.noErrors += 1
            self.errors.append(msg)

        # Parse output of Schematron validation and extract
        # info on failed tests
        try:
            self.extractSchematron(report)
            if len(self.schematronTestsFailed) == 0:
                self.status = "pass"
        except Exception:
            msg = "error while parsing Schematron report"
            logging.error(msg)
            self.noErrors += 1
            self.errors.append(msg)

        # Parse jpylyzer XML output and extract info on failed tests
        # in case image is not valid JP2
        try:
            self.extractJpylyzer(resultJpylyzer)
        except Exception:
            msg = "error while parsing jpylyzer output"
            logging.error(msg)
            self.noErrors += 1
            self.errors.append(msg)
