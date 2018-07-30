# -*- coding: cp949 -*-
######################################################################
#
# Genomics & Informatics Journal Paper Download Util
#
#   - Download all Genomics & Informatic journal papers in pdf format
#     (Class : GIPDFDownloader)
#
#   - Convert downloaded pdf papers into txt format
#     (Class : GIPDFtoTXTConverter)
#
#   - Classify converted txt papers by year
#     (Class : GIYearClassifier)
#
# So-Yeon, Oh
# Major in Compurter Science & Engineering
# The Graduate School of Ewha Womans University
#
#######################################################################



#######################################################################
#
# Import Modules
#  
#   - os (python default)
#   - requests (should be installed)
#   - pdfminer.six (should be installed on latest python 3 version)
#   - io (python default)
#   - nltk (should be installed)
#
#######################################################################

import os
import requests

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO

from nltk.corpus import PlaintextCorpusReader

#######################################################################



#######################################################################
#
# Function : _makeDirectory
# [should be kept in private (should not be accessed in public)]
#
#   - Makes directory with name 'dirname' in current working directory
#     when the directory does not exist.
#
#   - Return the full path of the directory 'dirnmame'
#
#######################################################################

def _makeDirectory(rootdir, dirname) :
    directory = rootdir + '/' + dirname + '/'
    if not os.path.isdir(directory) :
        os.mkdir(directory)
    return directory



#######################################################################
#
# Class : GIPDFDownloader
#
#   - Download all Genomics & Informatic journal papers in pdf format
#     (499 journal papers from 2003 to 2017 )
#
#
#   [Private Methods]
#
#   _buildGIFileNames()
#
#
#   [Public Methods]
#
#   downloadGIPDF()
#
#######################################################################

class GIPDFDownloader :

    rootURL = "https://genominfo.org/upload/pdf/"
    filenameTypes = []
    

    def __init__ (self, dirname) :
        self.workspace = _makeDirectory(os.getcwd(), dirname)
    
    
    # [should be kept in private (should not be accessed in public)]
    # Build possible GI file names
    def _buildGIFileNames(self) :
        print ("Build File Names for GI in 2003 to 2011")
        # file name stucture from 2003 to 2011 : gni-(0~9)-()-()
        self.filenameTypes.append(('gni-' + str(vol) + '-' + str(no) + '-' + str(page) + '.pdf' for vol in range(1, 10) for no in range(1, 5) for page in range(1, 400)))
        print ("Build File Names for GI in 2012 to 2016")
        # file name structure from 2012 to 2016 : gni-(10~14)-()
        self.filenameTypes.append(('gni-' + str(vol) + '-' + str(page) + '.pdf' for vol in range(10, 16) for page in range(1, 400)))
        print ("Build File Names for GI in 2017")
        # file name structure from 2017 : gi-2017-(15)-()-()
        self.filenameTypes.append(('gi-2017-' + str(vol) + '-' + str(no) + '-' + str(page) + '.pdf' for vol in range(15, 16) for no in range(1, 5) for page in range(1, 400)))
        print ("Complete Building File Names!")

    # [can be accessed in public]
    # Download all GI files when its URL exists
    def downloadGIPDF (self) :

        self._buildGIFileNames()
        
        for filenames in self.filenameTypes :
            for filename in filenames :
                try :
                    r = requests.get(self.rootURL + filename)
                    if r.status_code != 404 :
                        print (filename  + " exists!")
                        print ("Downloading " + filename + " with requests")
                        r = requests.get(self.rootURL + filename)
                        with open(self.workspace + filename, "wb") as code:
                            code.write(r.content)
                    else :
                        print ("Finding existing files...")
                except ConnectionError as e1 :
                    print ("No Response...")
                    continue
                except requests.exceptions.SSLError as e2 :
                    print ("Max Retry...")
                    continue



####################################################################
#
# Class : GIPDFtoTXTConverter
#
#   - Convert downloaded pdf papers into txt format
#
#
#   [Private Methods]
#
#   _getPDFContents(filepath)
#
#
#   [Public Methods]
#
#   convert()
#
#######################################################################

class GIPDFtoTXTConverter :
    
    journalNeedsOCR = []
    journalTXT = []
    
    def __init__ (self, pdfdir, txtdir, codec) :
        self.pdfDirectory = _makeDirectory(os.getcwd(), pdfdir)
        self.txtDirectory = _makeDirectory(os.getcwd(), txtdir)
        self.codec = codec

    # [should be kept in private (should not be accessed in public)]
    # Get txt string from the pdf file
    def _getPDFContents (self, filepath) :
        resourceManager = PDFResourceManager()
        string = StringIO()
        laParams = LAParams()
        converter = TextConverter(resourceManager, string, codec = self.codec, laparams = laParams)
        inFile = open(filepath, "rb")
        interpreter = PDFPageInterpreter(resourceManager, converter)
        password = ''
        maxPages = 0
        caching = True
        pageNums = set()

        for page in PDFPage.get_pages(inFile, pageNums, maxpages = maxPages, password = password, caching = caching, check_extractable = True) :
            interpreter.process_page(page)

        inFile.close()
        converter.close()
        fileText = string.getvalue()
        string.close()

        return fileText

    
    # [can be accessed in public]
    # Convert all pdf files into txt files
    def convert (self) :
        inFileList = os.listdir(self.pdfDirectory)
        print ("Current Path : " + self.pdfDirectory)

        for inFile in inFileList :
            print ("Convert " + inFile + " into txt file.")
            contents = self._getPDFContents(self.pdfDirectory + inFile)
            print (inFile + " : " + str(len(contents)))

            if len(contents) < 100 :
                self.journalNeedsOCR += [inFile]
            else :
                self.journalTXT += [inFile]

            outFile = open(self.txtDirectory + inFile[:-4] + ".txt", "wb")
            outFile.write(contents.encode())
            outFile.close()


        print ("Need OCR : " + str(self.journalNeedsOCR))
        print ("Convert " + str(len(self.journalTXT)) + " pdf journals into text files.")



##################################################################
#
# Class : GIYearClassifier
#
#   - Classify converted txt papers by year
#
#
#   [Private Methods]
#
#   _writeFileInYearDir(year, journal)
#   _extractYearByDOI(doiurl, journal, line)
#   _extractYearByMonth(journal, word)
#
#
#   [Public Methods]
#
#   classifyByYear()
#
#######################################################################

class GIYearClassifier :

    # DOI URL parts
    # To extract year from papers accepted from 2012 to 2017, we need a DOI URL of each paper, because it contains year.
    doiURLTypes = [
        
        'http://dx.doi.org/10.5808/GI.', # DOI URL part from 2012 to 2015
        'https://doi.org/10.5808/GI.' # DOI URL part from 2016 to 2017

        ]

    # Month Strings appear in paper from 2003 to 2011
    # To extract year from papers accepted from 2003 to 2011, we need to extract month first.
    dictMonth = [

        'january', 'february', 'march', 'april', 'may', 'june',
        'july', 'august', 'september', 'october', 'november', 'december', 'oecember'

        ]

    yearDirectoryList = []
    
    def __init__ (self, txtdir, resultdir, codec) :
        self.txtDirectory = _makeDirectory(os.getcwd(), txtdir)
        self.resultDirectory = _makeDirectory(os.getcwd(), resultdir)
        self.codec = codec

    # [should be kept in private (should not be accessed in public)]
    def _writeFileInYearDir(self, year, journal) :
        yearDirectory = _makeDirectory(self.resultDirectory, 'GI_YEAR_' + year)
        print (yearDirectory)

        if not (yearDirectory in self.yearDirectoryList) :
            self.yearDirectoryList.append(yearDirectory)

        inFile = open(self.txtDirectory + journal, 'rb')
        outFile = open(yearDirectory + journal, 'wb')

        for content in inFile :
            outFile.write(content)

        inFile.close()
        outFile.close()
    
    # [should be kept in private (should not be accessed in public)]
    def _extractYearByDOI (self, doiurl, journal, line) :
        splitPart = line.split(doiurl)
        year = splitPart[1].split('.')[0]
        self._writeFileInYearDir(year, journal)

    # [should be kept in private (should not be accessed in public)]
    def _extractYearByMonth (self, journal, word) :
        year = word
        self._writeFileInYearDir(year, journal)

    # [can be accessed in public]
    def classifyByYear(self) :
        corpusReader = PlaintextCorpusReader(self.txtDirectory, ".*.txt", encoding = self.codec)

        for journal in corpusReader.fileids() :
            print ("Start " + journal)

            sentList = corpusReader.sents(journal)

            for sent in sentList :
                getMonth = False
                getDOI = False

                line = ''.join(sent)

                if self.doiURLTypes[0] in line :
                    getDOI = True
                    self._extractYearByDOI(self.doiURLTypes[0], journal, line)
                    break
                elif self.doiURLTypes[1] in line :
                    getDOI = True
                    self._extractYearByDOI(self.doiURLTypes[1], journal, line)
                    break

                for word in sent :
                    if getMonth :
                        self._extractYearByMonth(journal, word)
                        break

                    if word.lower() in self.dictMonth :
                        getMonth = True

                if getMonth :
                    getMonth = False
                    break
                elif getDOI :
                    getDOI = False
                    break

            print ("End " + journal)

        print (str(self.yearDirectoryList))

