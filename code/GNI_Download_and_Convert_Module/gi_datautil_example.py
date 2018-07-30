# -*- coding: cp949 -*-
######################################################################
#
# Genomics & Informatics Journal Paper Download Util Usage Example
#
#
# So-Yeon, Oh
# Major in Compurter Science & Engineering
# The Graduate School of Ewha Womans University
#
#######################################################################

import gi_datautil
from gi_datautil import GIPDFDownloader
from gi_datautil import GIPDFtoTXTConverter
from gi_datautil import GIYearClassifier


# download all journal papers in pdf
downloader = GIPDFDownloader('_GI_PDF')
downloader.downloadGIPDF()

# convert downloaded pdf files into txt format
converter = GIPDFtoTXTConverter("_GI_PDF", "_GI_TXT_UTF8", "utf8")
converter.convert()

# classify all converted txt files by year
yclassifier = GIYearClassifier("_GI_TXT_UTF8", "_GI_YEAR_UTF8", "utf8")
yclassifier.classifyByYear()

