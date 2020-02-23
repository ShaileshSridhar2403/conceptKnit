'''
blah blah
'''
import re
import sys
import os
import pickle

class TextToSpeech(object):
    '''
    blah blah
    '''
    approp_punctuations = r'[!?.;,":\[\]\(\)-]'

    def __init__(self, file_path):
        file = open(file_path, "r")
        self.essay = file.read()
        self.essay = self.essay.replace('\n', '')
        self.essay = self.essay.replace('\t', '')
        self.segments = re.split(self.approp_punctuations, self.essay)
        self.punctuation_pos = re.findall(self.approp_punctuations, self.essay)

        # ensure all segments are correct
        for segment in self.segments:
            for char in segment:
                if char != ' ' and char != "'" and (not char.isalnum()):
                    sys.exit("take care of proper punctuations man")


    def convert_to_speech_segments(self, dest_path):
        '''
        blah blah
        '''
        count = 1
        for segment in self.segments:
            os.system('espeak "' + segment + '" -v en-us+f2 -s 30 -g 10 --stdout | ffmpeg -i - -ar 44100 -ac 2 -ab 192k -f mp3 ' + dest_path + str(count).zfill(3) + ".mp3")
            count += 1
        return count

    def serialize_punctuation_positions(self, dest_file='punctuation_pos_pickle'):
        '''
        blah blah
        '''
        print("Screw you")
        print(self.punctuation_pos)
        dbfile = open(dest_file, 'ab')
        pickle.dump(self.punctuation_pos, dbfile)
        dbfile.close()


if __name__ == "__main__":
    TTS = TextToSpeech("texts/how_to_get_startup_ideas")
    # TTS.convert_to_speech_segments('speech_segments_new/')
    TTS.serialize_punctuation_positions()
