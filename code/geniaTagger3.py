import os
import sys
import nltk
from nltk import *

from geniatagger import GeniaTagger
from nltk.corpus import swadesh
from nltk.corpus import conll2000
#test_sents = conll2000.chunked_sents('test.txt', chunk_types=['NP'])
#train_sents = conll2000.chunked_sents('train.txt', chunk_types=['NP'])

import nltk
import ssl
import pdfplumber,os
from decimal import *


try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

#nltk.download()

url = "https://genominfo.org/upload/pdf/"
filenames = ["gni-1-1-55.pdf", "gni-1-1-40.pdf", "gni-2-1-1.pdf"]
GIJournals =['gni-8-1-41.pdf', 'gni-8-1-50.pdf', 'gni-8-1-58.pdf', 'gni-8-2-63.pdf', 'gni-8-2-70.pdf', 'gni-8-2-76.pdf', 'gni-8-2-81.pdf', 'gni-8-2-86.pdf', 'gni-8-2-90.pdf', 'gni-8-2-94.pdf', 'gni-8-2-97.pdf', 'gni-8-3-101.pdf', 'gni-8-3-103.pdf', 'gni-8-3-108.pdf', 'gni-8-3-116.pdf', 'gni-8-3-122.pdf', 'gni-8-3-131.pdf', 'gni-8-3-138.pdf', 'gni-8-3-142.pdf', 'gni-8-3-150.pdf', 'gni-8-3-159.pdf', 'gni-8-4-165.pdf', 'gni-8-4-170.pdf', 'gni-8-4-177.pdf', 'gni-8-4-185.pdf', 'gni-8-4-194.pdf', 'gni-8-4-201.pdf', 'gni-8-4-206.pdf', 'gni-8-4-212.pdf', 'gni-9-1-1.pdf', 'gni-9-1-5.pdf', 'gni-9-1-12.pdf', 'gni-9-1-19.pdf', 'gni-9-1-28.pdf', 'gni-9-1-37.pdf', 'gni-9-1-39.pdf', 'gni-9-2-45.pdf', 'gni-9-2-52.pdf', 'gni-9-2-59.pdf', 'gni-9-2-64.pdf', 'gni-9-2-69.pdf', 'gni-9-2-74.pdf', 'gni-9-2-79.pdf', 'gni-9-2-85.pdf', 'gni-9-2-89.pdf', 'gni-9-3-93.pdf', 'gni-9-3-102.pdf', 'gni-9-3-114.pdf', 'gni-9-3-121.pdf', 'gni-9-3-127.pdf', 'gni-9-3-134.pdf', 'gni-9-3-136.pdf', 'gni-9-3-138.pdf', 'gni-9-4-143.pdf', 'gni-9-4-152.pdf', 'gni-9-4-173.pdf', 'gni-9-4-181.pdf', 'gni-9-4-189.pdf', 'gni-9-4-194.pdf', 'gni-9-4-197.pdf', 'gni-15-3-81.pdf']

executable_path = os.path.join(".", "geniatagger-3.0.2", "geniatagger")
#tagger = GeniaTagger(executable_path)


tagger = GeniaTagger(os.getcwd()+'/Downloads/geniatagger-3.0.2/geniatagger', ['-nt'])
text = "Recombinant MIP-1-alpha induces a dose-dependent inhibition of different strains of \
        HIV-1, HIV-2, and simian immunodeficiency virus (SIV)."

#for word, base_form, pos_tag, chunk, named_entity in tagger.tag(text):
#    print("{:20}{:20}{:10}{:10}{:10}".format(word, base_form, pos_tag, chunk, named_entity))

#print(tagger.parse('This is a pen.'))
#print(tagger.parse(text))



def extract_title_main(file_name):
    title = ""
    subtitle = ""
    strapline = ""
    sub_strapline = ""
    main_text = ""
    check_list = ["0","1","2","3","4","5","6","7","8","9",","]
    with pdfplumber.open(os.getcwd()+ '/GICorpus2/'+file_name) as pdf:
    #총 페이지 수
        total_pages = pdf.pages
        for page in total_pages:
            total_char = page.chars
            charsize = len(total_char)
            for ch in range(charsize):
                #폰트크기가 Decimal로 저장되어 있기 때문에 int로 변환 필요
                temp = int(Decimal(total_char[ch].get("size")))
                
                if temp == 23: #제목
                    title = title + total_char[ch].get("text")

                elif temp == 16: #소제목
                    strapline = strapline+ total_char[ch].get("text")
                    if int(Decimal(total_char[ch+1].get("size"))) < 16:
                        strapline = strapline + "\t" 

                elif temp  == 11: #소소제목
                    sub_strapline = sub_strapline + total_char[ch].get("text")
                   
                    
                else : #본문 (> , < , , , 등등 폰트크기 10 아닌거 포함)
                    # 기울임체 제거 
                    if total_char[ch].get("upright") == False:
                        continue

                    # 줄바꿈 - 는 스킵   
                    if total_char[ch].get("text") == "-":
                        if( int(Decimal(total_char[ch].get("x0"))) >220) and (int(Decimal(total_char[ch].get("x1"))) >220):
                               continue

                    main_text = main_text + total_char[ch].get("text")
                     # . 뒤에 띄어쓰기가 없으면 문장 구분 못하는 문제 발견 --> . 나오면 뒤에 공백 추가
                     # 숫자, , 나올 때 제외함.
                    #인덱스에러 발생해서 추가 (ch + 1 때문..)
                    if ch< charsize -2:
                        if (total_char[ch].get("text")==".") and not (total_char[ch+1].get("text") in check_list):
                            main_text = main_text + " "
                        
    title = title + "."
    
    f = open(os.getcwd()+"/GICorpus2/" + file_name[0:-4]+".txt", "w")
    f.write(title)
    f.write("\n\n")
    f.write(main_text)
    f.close()
    
    

def main():
    giCorpus = {}
    corpus_root = os.getcwd() + "/GICorpus2"
    for pdflist in GIJournals:
        extract_title_main(pdflist)
    
    
    filelists = nltk.corpus.PlaintextCorpusReader(corpus_root, '.*\.txt', encoding='utf-8')
   # filelists = nltk.corpus.PlaintextCorpusReader(corpus_root, 'gni-9-4-143.txt', encoding='utf-8')

    #wnl = nltk.WordNetLemmatizer()
    print(filelists.fileids())
    for file in filelists.fileids():
        #wordlist = filelists.words(file)
        f = open(os.getcwd()+"/GI_tag/tagged_" + file, "w")
        rawText = filelists.raw(file)
        sent_text = nltk.sent_tokenize(rawText)
        print("Printing size of  " + file + " original wordlist: " + str(len(sent_text)))
        for sentence in sent_text:
            #print (sentence)
            #sentence = sentence.replace("-\n","")
            #sentence = sentence.replace("\n", "")
            #sentence = sentence.replace("- ","")
            #sentence = sentence.replace("- \n\n","")
            #sentence = sentence.replace("- \n\n\n","")
            print("Printing size of  Sentence: " + str(len(sentence)))
           # print(sentence)
            f.write(sentence + "\n")
            for word in tagger.parse(sentence):
                #print(word)
                f.write(str(word) + "\n")
        f.close()
      

    
main()
