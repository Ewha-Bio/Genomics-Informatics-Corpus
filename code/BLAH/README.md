# Prepare the GENIA Tagger
- Download [geniatagger-3.0.2.tar.gz](http://www.nactem.ac.uk/GENIA/tagger/)
- Extract the tar file
- Compile the GENIA Tagger
    - `cd geniatagger-3.0.2/`
    - `make`

# Tag
- pipenv install
- pipenv shell
- python genia.py PATH/TO/JSON/INPUT/ PATH/TO/JSON/OUTPUT/
- tar -czvf tagged_json.tgz PATH/TO/JSON/OUTPUT/

# Upload
- upload tgz file on PubAnnotation