import os
import sys
import csv
import logging

class test:

    def __init__(self):
        """initialise workflow class instance"""
        self.delimiterIn = ";"
        self.delimiterOut = ";"
        self.batchManifest = "/home/johan/kb/digitalisering/tifftojp2/mh-small-jp2/manifest.csv"
        self.dirOut = "/home/johan/kb/digitalisering/tifftojp2/mh-small-jp2"
        self.noErrors = 0
        self.noWarnings = 0

    def concordanceCheck(self):
        """Cross-check concordance tables against batch manifest"""
        # TODO: code assumes fixed position + order of columns in concordance tables
        # verify if this is correct. If not, use column names.

        logging.info("Checking concordance tables against batch manifest")

        with open(self.batchManifest, 'r', newline='', encoding='utf-8') as fMan:
            reader = csv.reader(fMan, delimiter=self.delimiterOut)
            manifestData = list(reader)

        imagesManifest = []
        rowIndex = 0
        for row in manifestData:
            if rowIndex > 0:
                imagesManifest.append(row[0])
            rowIndex += 1

        concordanceDir = os.path.join(self.dirOut, "Concordantie")
        cTables = os.listdir(concordanceDir)
        for cTable in cTables:
            # First part of file name refers to directory in "Signaturen"
            sigDir = cTable.split("_")[0]
            masterDirPath = os.path.join("Signaturen", sigDir, "Master")
            cTable = os.path.join(concordanceDir, cTable)
            with open(cTable, 'r', newline='', encoding='utf-8') as fCTab:
                reader = csv.reader(fCTab, delimiter=self.delimiterOut)
                cTabData = list(reader)

            rowIndex = 0
            for row in cTabData:
                if rowIndex > 0:
                    # First column: master image
                    imageMaster = row[0]
                    # Add masterDirPath to get corresponding batch manifest value
                    imageMasterFullPath = os.path.join(masterDirPath, imageMaster)
                    # Check against batch manifest
                    if not imageMasterFullPath in imagesManifest:
                        logging.error("image {} not found in batch manifest".format(imageMasterFullPath))
                        self.noErrors += 1

                    # Columns 3 - 6 refer to target images (column 2 refers to access images, which are not in manifest)
                    for i in range(2, 6):
                        imageTarget = row[i]
                        # Directory of this images follows from file name
                        nameComponents = imageTarget.split(".")[0].split("_")
                        targetDir = "{}_{}_{}".format(nameComponents[0], nameComponents[2], nameComponents[3])
                        # Construct full path in corresponding batch manifest value
                        imageTargetFullPath = os.path.join("Targets", targetDir, imageTarget)
                        # Check against batch manifest
                        if not imageTargetFullPath in imagesManifest:
                            logging.error("image {} not found in batch manifest".format(imageTargetFullPath))
                            self.noErrors += 1
                rowIndex += 1



def main():

    # Set up logging
    logging.basicConfig(handlers=[logging.StreamHandler(sys.stdout)],
                                  level=logging.INFO,
                                  format='%(asctime)s - %(levelname)s - %(message)s')

    wf = test()
    wf.concordanceCheck()


if __name__ == "__main__":
    main()
