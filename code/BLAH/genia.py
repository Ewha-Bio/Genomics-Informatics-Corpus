"""
output json format
$ python genia.py json PATH/TO/JSON/INPUT/ PATH/TO/JSON/OUTPUT/

output txt format (original)
$ python genia.py txt PATH/TO/JSON/INPUT/ PATH/TO/TXT/OUTPUT/
"""
import json
from pathlib import Path
from typing import List
import argparse

from tqdm import tqdm
from geniatagger import GeniaTagger
import nltk

GENIA_FP = Path('geniatagger-3.0.2/geniatagger')


def load_tagger(fp: Path):
    """
    load GENIA Tagger
    :param fp: file path of GENIA Tagger
    :return:
    """
    tagger = GeniaTagger(fp)
    return tagger


def test(tagger):
    """
    test GENIA Tagger
    :return:
    """
    text = 'Recombinant MIP-1-alpha induces a dose-dependent inhibition of different strains of HIV-1, HIV-2, and simian immunodeficiency virus (SIV).'
    print(tagger.parse(text))
    return


def get_binded_fps(dir: Path):
    """
    bind same id files
    :param fp: directory of JSON files
    :return:
    """
    binded_fps = {}
    for fp in dir.glob('*.json'):
        _, pmcid, divid, sec = fp.stem.split('-', maxsplit=3)
        binded_fps.setdefault(pmcid, [])
        binded_fps[pmcid].append(fp)
    for k, v in binded_fps.items():
        binded_fps[k] = sorted(binded_fps[k])
    return binded_fps


def _tag2txt(sents: List[str], fp_out: Path, tagger):
    """
    :param sents:
    :param fp_out:
    :param tagger:
    :return:
    """
    lines = []
    for sent in sents:
        lines.append(sent)
        for word in tagger.parse(sent):
            lines.append(str(word))

    with fp_out.open(mode='w') as f:
        f.write('\n'.join(lines))
    return


def tag2txt(fp_in_list: List[Path], fp_out: Path, tagger):
    """
    :param fp_in_list:
    :param fp_out:
    :param tagger:
    :return:
    """
    sents = []
    for fp_in in fp_in_list:
        with fp_in.open() as f:
            data = json.load(f)
        text = data['text'].replace('\n', ' ')
        sents += nltk.sent_tokenize(text)
    _tag2txt(sents, fp_out, tagger)


def _tag2json(sents, fp_in, fp_json, tagger):
    """
    :param sents:
    :param fp_in:
    :param fp_json:
    :param tagger:
    :return:
    """
    _, pmcid, divid, sec = fp_in.stem.split('-', maxsplit=3)
    data = {
        'text': None,
        'sourcedb': 'PMC',
        'sourceid': pmcid,
        'divid': divid,
        'denotations': []
    }

    # tagging by GENIA Tagger
    anns = []
    begin, end = 0, 0
    for sent in sents:
        for word, word2, _, _, tag in tagger.parse(sent):
            end = begin + len(word)
            ann = [
                begin,
                end,
                tag,
                word,
            ]
            begin = end + 1
            anns.append(ann)
        begin = end + 1
    text = ' '.join([w for _, _, _, w in anns])
    data['text'] = text

    # combine B-I terms
    reversed_anns = []
    is_continue = False
    _end = None
    word_list = []
    for begin, end, tag, word in reversed(anns):
        if tag.startswith('O'):
            continue

        word_list.append(word)
        if tag.startswith('I') and not is_continue:
            is_continue = True
            _end = end
        elif tag.startswith('B'):
            if _end is None:
                _end = end

            ner_tag = tag.split('-', maxsplit=1)[-1]
            word = ' '.join(reversed(word_list))
            reversed_anns.append([begin, _end, ner_tag, word])

            is_continue = False
            _end = None
            word_list = []

    # append annotaions to data
    _id = 1
    for begin, end, tag, word in reversed(reversed_anns):
        data['denotations'].append({
            'id': 'T{}'.format(_id),
            'span': {'begin': begin, 'end': end},
            'obj': tag,
            'text': text[begin:end],
        })
        _id += 1

    fp_out = fp_json.parent / '{}-{}.json'.format(fp_json.stem, divid)
    with fp_out.open(mode='w') as f:
        json.dump(data, f, indent=4)


def tag2json(fp_in_list: List[Path], fp_out: Path, tagger):
    """
    :param fp_in_list:
    :param fp_out:
    :param tagger:
    :return:
    """
    for fp_in in fp_in_list:
        with fp_in.open() as f:
            data = json.load(f)
        text = data['text'].replace('\n', ' ')
        _sents = nltk.sent_tokenize(text)
        _tag2json(_sents, fp_in, fp_out, tagger)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('ext', type=str, choices=['json', 'txt'], help='select an extension of output files')
    parser.add_argument('dir_in', type=str, help='select an extension of output files')
    parser.add_argument('dir_out', type=str, help='select an extension of output files')
    args = parser.parse_args()
    ext = args.ext
    dir_in = Path(args.dir_in)
    dir_out = Path(args.dir_out)
    if not dir_out.exists():
        dir_out.mkdir()

    tagger = load_tagger(GENIA_FP)
    binded_fps = get_binded_fps(dir_in)

    for pmcid, fp_in_list in tqdm(binded_fps.items()):
        fp_out = dir_out / 'tagged_{}.{}'.format(pmcid, ext)
        if ext == 'txt':
            tag2txt(fp_in_list, fp_out, tagger)
        elif ext == 'json':
            tag2json(fp_in_list, fp_out, tagger)
