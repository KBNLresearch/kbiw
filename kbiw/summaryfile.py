#! /usr/bin/env python3
"""Module for writing summary file"""

import os
import xml.etree.ElementTree as ET
from xml.dom import minidom
import logging
from collections import Counter


class SummaryFile:
    """SummaryFile class"""

    def __init__(self, summaryFile, summaryDict, errors, warnings):

        self.summaryFile = summaryFile
        self.summaryDict = summaryDict
        self.noErrors = 0
        self.errors = errors
        self.warnings = warnings

    def addProperty(self, element, tag, text):
        """Append childnode with text to Element"""

        el = ET.SubElement(element, tag)
        el.text = str(text)

    def writeSummaryFile(self):
        """Write summary file """

        # Name space and XSD schema strings
        nsString = 'http://kb.nl/ns/kbiw/v1/'
        xsiNsString = 'http://www.w3.org/2001/XMLSchema-instance'

        # Create root element
        root = ET.Element("kbiw", {'xmlns': nsString,
                                   'xmlns:xsi': xsiNsString})
        # Add child elements
        for key, value in self.summaryDict.items():
            self.addProperty(root, key, value)

        # Generate counts of unique errors and warnings
        errorsUnique = Counter(self.errors).most_common()
        warningsUnique = Counter(self.warnings).most_common()

        errorsElt = ET.Element("errors")
        warningsElt = ET.Element("warnings")

        for error in errorsUnique:
            errorMsg = error[0]
            errorCount = error[1]
            el = ET.SubElement(errorsElt, "error")
            el.text = str(errorMsg)
            el.set("count", str(errorCount))

        for warning in warningsUnique:
            warningMsg = warning[0]
            warningCount = warning[1]
            el = ET.SubElement(warningsElt, "warning")
            el.text = str(warningMsg)
            el.set("count", str(warningCount))

        root.append(errorsElt)
        root.append(warningsElt)

        # Element to string
        xmlOut = ET.tostring(root, 'unicode', 'xml')

        # Make xml pretty
        xmlPretty = minidom.parseString(xmlOut).toprettyxml('    ')

        # Write output
        try:
            with open(self.summaryFile, 'w', newline='', encoding='utf-8') as fSum:
                fSum.write(xmlPretty)
        except Exception:
            logging.error("cannot write summary file to {}".format(self.summaryFile))
            self.noErrors += 1
