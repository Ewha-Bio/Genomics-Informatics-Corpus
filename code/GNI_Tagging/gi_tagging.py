# -*- coding: cp949 -*-
#######################################################################
#
# Genomics & Informatics  Corpus
#
#   - Generate corpus with Genomics & Informatics journal papers
#     (498 papers from 2003 to 2017)
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
#   - nltk (should be installed)
#   - geniatagger (should be installed on Linux or Unix)
#
#######################################################################

import os
import nltk
from nltk import *
from nltk.corpus import *
import string
from nltk.corpus import brown
from geniatagger import GeniaTagger

#######################################################################



corpusDir = ["/GI_TAGGING/"]
corpusRootList = [os.getcwd() + directory for directory in corpusDir]

codec = "utf8"

tagger = GeniaTagger("/usr/local/geniatagger/geniatagger")

train_sents = brown.tagged_sents(categories="learned", tagset="treebank")

t0 = nltk.DefaultTagger("UNK")
t1 = nltk.UnigramTagger(train_sents, backoff = t0)
t2 = nltk.BigramTagger(train_sents, backoff = t1)



# Gennia + Backoff
for corpusRoot in corpusRootList :

    corpusReader = PlaintextCorpusReader(corpusRoot, ".*.txt", encoding = codec)

    outFile = open(corpusRoot + "genia_and_backoff.txt", "w")   
    
    for journal in corpusReader.fileids() :
        print ("******* start " + journal)
        sentList = corpusReader.sents(journal)

        for sent in sentList :
            
            taggedList = t2.tag(sent)
            
            for tag in taggedList :
                if tag[1] == "UNK" :
                    genia_tag_list = tagger.parse(tag[0])
                    for genia_tag in genia_tag_list :
                        if genia_tag[4] == "O" :
                            outFile.write(genia_tag[0] + "/" + genia_tag[2] + "  ")
                        else :
                            new_tag = genia_tag[4].split("-")[1]
                            outFile.write(genia_tag[0] + "/" + new_tag + "  ")
                            
                    
                else :
                    outFile.write(tag[0] + "/" + tag[1] + " ")
            outFile.write("\n\n")
        

        print ("##### end " + journal)

    outFile.close()

# Only GENIA with line
for corpusRoot in corpusRootList :
    corpusReader = PlaintextCorpusReader(corpusRoot, ".*.txt", encoding = codec)
    outFile = open(corpusRoot + "no_backoff_only_genia.txt", "w")   
    
    for journal in corpusReader.fileids()  :
        print ("******* start " + journal)
        inFile = open(corpusRoot + journal, "r")

        for line in inFile :
            taggedList = tagger.parse(line)
            

            for genia_tag in taggedList:

                #('I-protein',)
                if(len(genia_tag) != 5) :
                    print(str(genia_tag))
                    continue
                
                if genia_tag[4] == "O" :
                    outFile.write(genia_tag[0] + "/" + genia_tag[2] + "  ")
                else :
                    new_tag = genia_tag[4].split("-")[1]
                    outFile.write(genia_tag[0] + "/" + new_tag + "  ")

            outFile.write("\n\n")
        inFile.close()        
        print ("##### end " + journal)

    outFile.close()

# Only backoff
for corpusRoot in corpusRootList :

    corpusReader = PlaintextCorpusReader(corpusRoot, ".*.txt", encoding = codec)

    outFile = open(corpusRoot + "no_genia_only_backoff.txt", "w")   
    
    for journal in corpusReader.fileids() :
        print ("******* start " + journal)
        sentList = corpusReader.sents(journal)

        for sent in sentList :
            
            taggedList = t2.tag(sent)
            
            for tag in taggedList :
                outFile.write(tag[0] + "/" + tag[1] + " ")
            outFile.write("\n\n")
        

        print ("##### end " + journal)

    outFile.close()
