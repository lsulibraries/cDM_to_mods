import os
import json

alias_transcriptTag = {'p120701coll27': 'Transcript',
                       'p120701coll17': 'Fulltext',
                       'p120701coll9': 'Description',
                       'p16313coll3': 'Text',
                       'p15140coll44': 'Transcript',
                       'p15140coll23': 'Text',
                       'p16313coll19': 'Transcript',
                       'LHP': 'full text',
                       'p15140coll4': 'Summary',
                       'p16313coll93': 'Transcript',
                       'AAW': 'Transcript/Translation',
                       'APC': 'Transcript/Translation',
                       'p15140coll52': 'Description',
                       'LPC': 'Transcript/Translation',
                       'LSU_SCE': 'Transcript',
                       'LSU_NMI': 'Transcript',
                       'p15140coll50': 'Full text',
                       'p16313coll80': 'Transcript',
                       'lapur': 'Transcription',
                       'LSUBK01': 'Full text',
                       'p16313coll91': 'Transcript',
                       'LOYOLA_ETD': 'Notes',
                       'LMNP01': 'Transcript',
                       'TAH': 'Transcription',
                       'p120701coll12': 'Transcription',
                       'p15140coll7': 'Full Text',
                       'p16313coll87': 'Transcript',
                       'p16313coll98': 'Transcript',
                       'p15140coll42': 'Description',
                       'LSUHSC_NCC': 'Excerpted text',
                       'p120701coll26': 'Transcript',
                       'p15140coll49': 'Description',
                       'p16313coll95': 'Transcript',
                       'LSU_CFF': 'Full Text',
                       }

transcript_is_a_sibling_pdf_file = ['p15140coll41', 'p15140coll6', ]


def find_nick_of_name(name, alias):
    with open('/home/francis/Desktop/Transcript/cdm_source_data/pulled_cdm/Cached_Cdm_files_merged_sources/{}/Collection_Fields.json'.format(alias), 'r') as f:
        translation_json = json.load(f)
    for item in translation_json:
        if item['name'] == name:
            return item['nick']
    else:
        print('failed to find the nick for {}'.format(alias))


def is_transcript_same_for_item(filename, new_transcript_text):
    with open(filename, 'r') as f:
        old_transcript_text = f.read()
    return old_transcript_text != new_transcript_text


def make_transcript():
    for root, dirs, files in os.walk('/home/francis/Desktop/Transcript/cdm_source_data/pulled_cdm/'):
        for alias, transcript_tag in alias_transcriptTag.items():
            output_dir = '/home/francis/Desktop/CollectionPointerTranscripts/{}'.format(alias)
            transcript_nick = find_nick_of_name(transcript_tag, alias)
            if alias in root.split('/'):
                os.makedirs(output_dir, exist_ok=True)
                for file in files:
                    filename, ext = os.path.splitext(file)
                    if ext == '.json' and filename.isnumeric():
                        with open(os.path.join(root, file), 'r') as f:
                            pointer_json = json.load(f)
                        try:
                            current_transcript_text = pointer_json[transcript_nick]
                        except KeyError:
                            print('{} {} has no {}'.format(alias, filename, transcript_nick))
                            continue
                        if len(current_transcript_text):
                            output_file = os.path.join(output_dir, '{}.txt'.format(filename))
                            if not os.path.isfile(filename):
                                with open(output_file, 'w') as f:
                                    f.write(pointer_json[transcript_nick])
                            elif not is_transcript_same_for_item(output_file, current_transcript_text):
                                print("{} has different transcripts".format(filename))


if __name__ == '__main__':
    make_transcript()
