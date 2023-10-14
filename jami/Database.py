# Python packages
import os  # For reading files in a directory
import re  # Regex for interpreting the music21.converter.parse() output

# External libraries
import music21  # For reading MIDI files

# Internal modules
import Music
from MidiError import MidiError
from Logger import Logger

weightedRandom = []

# database that stores all the 4-note patterns
# in the form {[string of 8 digits] : [# of appearances]}
# where key is 4 2-digit numbers 0-11 representing the # of half-steps each note is above the tonic
fourNoteDatabase = {'total': 0}
# database that stores all the 3-note patterns
# in the form {[string of 6 digits] : [# of appearances]}
# where key is 3 2-digit numbers 0-11 representing the # of half-steps each note is above the tonic
threeNoteDatabase = {'total': 0}
# database that stores all the 2-note patterns
# in the form {[string of 4 digits] : [# of appearances]}
# where key is 2 2-digit numbers 0-11 representing the # of half-steps each note is above the tonic
twoNoteDatabase = {'total': 0}
# database that stores all the 2-note harmonies
# in the form {[string of 4 digits] : [# of appearances]}
# where key is 2 2-digit numbers 0-11 representing the # of half-steps each note is above the tonic
harmonicDatabase = {'total': 0}
# database that stores all the 1-note patterns
# in the form {[string of 2 digits] : [# of appearances]}
# where key is 1 2-digit numbers 0-11 representing the # of half-steps each note is above the tonic
oneNoteDatabase = {'total': 0}

this_dir = os.path.dirname(os.path.abspath(__file__))
folder_name = this_dir + '/data'
all_midi_file_names = os.listdir(folder_name)

all_scores = []
harmony_scores = []
for file_name, i in zip(all_midi_file_names, range(len(all_midi_file_names))):
    full_file_name = os.path.join(folder_name, file_name)
    Logger.display_progress('Reading MIDI files', i, len(all_midi_file_names))
    score = music21.converter.parse(full_file_name)
    all_scores.append(score)
    # If the filename matches H[0-9]+.mid, then it's a harmony file
    if re.match(r'H[0-9]+.mid', file_name):
        harmony_scores.append(score)


def storeInDatabase(list, database):
    # list is a list of notes (numbers 0-11) or harmonies
    # database is one of the global databases
    # assumes list has already been converted to semitone form
    # overloaded to work with all datbases in their own way
    # no return
    if database == threeNoteDatabase:
        if len(list) < 3:
            raise MidiError('Incomplete mume!')
        firstNote = 0
        while firstNote + 2 < len(list):
            mume = str(list[firstNote][0]) + str(list[firstNote + 1]
                                                 [0]) + str(list[firstNote + 2][0])
            addPattern(mume, threeNoteDatabase)
            firstNote += 1
            threeNoteDatabase['total'] += 1
    elif database == twoNoteDatabase:
        if len(list) < 2:
            raise MidiError('Incomplete mume!')
        firstNote = 0
        while firstNote + 1 < len(list):
            mume = str(list[firstNote][0]) + str(list[firstNote + 1][0])
            addPattern(mume, twoNoteDatabase)
            firstNote += 1
            twoNoteDatabase['total'] += 1
    elif database == oneNoteDatabase:
        if len(list) < 1:
            raise MidiError('Incomplete mume!')
        firstNote = 0
        while firstNote < len(list):
            mume = str(list[firstNote][0])
            addPattern(mume, oneNoteDatabase)
            oneNoteDatabase['total'] += 1
            firstNote += 1
    elif database == fourNoteDatabase:
        if len(list) < 4:
            raise MidiError('Incomplete mume!')
        firstNote = 0
        while firstNote + 3 < len(list):
            mume = str(list[firstNote][0]) + str(list[firstNote + 1][0]) + \
                str(list[firstNote + 2][0]) + str(list[firstNote + 3][0])
            addPattern(mume, fourNoteDatabase)
            firstNote += 1
            fourNoteDatabase['total'] += 1
    elif database == harmonicDatabase:
        for harmony in list:
            harmony = str(harmony)
            addPattern(harmony, harmonicDatabase)
            harmonicDatabase['total'] += 1
    else:
        raise MidiError('Nonexistent database')


def addPattern(pattern, dictionary):
    # adds a specified pattern to the database specified
    # param 'pattern' is a musical pattern
    if pattern in dictionary:
        dictionary[pattern] += 1
    else:
        dictionary[pattern] = 1


def setupWeightedRandom():
    for i in oneNoteDatabase:
        for j in range(0, oneNoteDatabase[i]):
            if j != 'total':
                weightedRandom.append(i)


def extract_info_from_score(score):
    # 1. Extract time signatures
    time_sigs = [ts for ts in score.recurse().getElementsByClass(
        music21.meter.TimeSignature)]

    unique_time_sigs = list(
        {str(ts): ts for ts in time_sigs}.values())  # Remove duplicates

    # 2. Extract key signatures
    key_sigs = [ks for ks in score.recurse(
    ).getElementsByClass(music21.key.KeySignature)]
    unique_key_sigs = list(
        {str(ks): ks for ks in key_sigs}.values())  # Remove duplicates

    return unique_time_sigs, unique_key_sigs


def extract_note_info(part):
    # Extract key signatures and notes from the part
    key_sigs = [ks for ks in part.recurse(
    ).getElementsByClass(music21.key.KeySignature)]
    time_sigs = [ts for ts in part.recurse(
    ).getElementsByClass(music21.meter.TimeSignature)]

    notes = [n for n in part.recurse().notes]

    note_info = []
    # Default to C Major if no key signature
    current_key = key_sigs[0] if key_sigs else music21.key.KeySignature()
    # Default to 4/4 if no time signature
    current_time_sig = time_sigs[0] if time_sigs else music21.meter.TimeSignature()

    accumulated_beats = 0  # Keep track of accumulated beats

    for note in notes:
        # Check if there's a key change before the note
        for ks in key_sigs:
            if ks.offset <= note.offset:
                current_key = ks
            else:
                break

        # Update accumulated beats for time signature changes
        for ts in time_sigs:
            if ts.offset <= note.offset:
                current_time_sig = ts
                accumulated_beats = ts.offset * current_time_sig.beatCount
            else:
                break
        # TODO: Handle chords
        # If the note is a chord, just take the first note
        if isinstance(note, music21.chord.Chord):
            note = note[0]
            Logger.warn('Chord in file \'',
                        all_midi_file_names[i], '(', i, ')', "\'!")

        # Convert the note to its pitch in the current key
        analyzed_key = current_key.asKey()
        scale_degree = analyzed_key.getScaleDegreeFromPitch(note.pitch)
        pitch_class = note.pitch.pitchClassString
        relative_value = (scale_degree, pitch_class)

        # Total beats into the song
        total_beats = accumulated_beats + note.beat - \
            1  # Subtracting 1 because beat is 1-indexed

        note_info.append((relative_value, total_beats))

    return note_info


def initializeFiles():
    # TODO shouldn't be more than one key signature event so I should check for that
    for score in all_scores:

        score_note_info = {}  # A dictionary to hold note information for each part

        time_sigs, key_sigs = extract_info_from_score(score)
        for part in score.parts:
            # Use part name or id if name is not available
            part_name = part.partName or str(part.id)
            # score_note_info[part_name] = extract_note_info(part)

            # all_time_sigs.extend(time_sigs)
            # all_key_sigs.extend(key_sigs)
            # all_notes.extend(notes)
            # key_signatures =
            part_note_info = extract_note_info(part)
            if len(key_sigs) > 1:
                Logger.warn('More than one key signature in file \'',
                            all_midi_file_names[i], '(', i, ')', "\'!")
            # parts = score.flat.getElementsByClass(music21.stream.Part)
            # time_signatures = score.flat.getElementsByClass(
            #     music21.meter.TimeSignature)
            if len(time_sigs) > 1:
                Logger.warn('More than one time signature in file \'',
                            all_midi_file_names[i], '(', i, ')', "\'!")
            # for part in parts:
                # notes = []
                # for note in part.flat.getElementsByClass(music21.note.Note):
                #     # data = [Music.convertToSemiTone(
                #     #     noteOnMatch.group(2)), noteOnMatch.group(1), 0]
                #     # notes.append(data)
                #     notes.append(note)
                # for _ in part.flat.getElementsByClass(music21.chord.Chord):
                #     Logger.warn('Chord in file \'', all_midi_file_names[i], '(', i, ')', "\'!")

            if len(part_note_info) >= 4:
                notes = []
                for note in part_note_info:
                    notes.append(note[0])
                storeInDatabase(notes, fourNoteDatabase)
                storeInDatabase(notes, threeNoteDatabase)
                storeInDatabase(notes, twoNoteDatabase)
                storeInDatabase(notes, oneNoteDatabase)
            else:
                Logger.warn("Unable to analyze mume in part \'",
                            part_name, "\' in file \'", all_midi_file_names[i], '(', i, ')', "\'!")
            Logger.display_progress(
                'Analyzing mumes', i+1, len(all_midi_file_names))
    setupWeightedRandom()


def storeHarmonies():
    # TODO recognize all harmony combinations when more than 2 notes start simultaniously
    for i in range(len(harmony_scores)):
        harmonyEvents = re.findall(
            r'[.]*midi.NoteOnEvent\(tick=[0-9]+, channel=[0-9]+, data=\[[0-9]+, [1-9][0-9]*]\)\,[\s]*midi.NoteOnEvent\(tick=0, channel=[0-9]+, data=\[[0-9]+, [1-9][0-9]*]\)', harmony_scores[i], re.M)
        harmonies = []
        if len(harmonyEvents) == 0:
            Logger.warn('H', i+1, 'has no harmonies?!?')
        for x in harmonyEvents:
            matchObj = re.match(
                r'midi.NoteOnEvent\(tick=[0-9]+, channel=[0-9]+, data=\[([0-9]+), [1-9][0-9]*]\)\,[\s]*midi.NoteOnEvent\(tick=0, channel=[0-9]+, data=\[([0-9]+), [1-9][0-9]*]\)', x)
            topNote = Music.convertToSemiTone(matchObj.group(1))
            bottomNote = Music.convertToSemiTone(matchObj.group(2))
            harmony1 = str(topNote) + str(bottomNote)
            harmonies.append(harmony1)
            if bottomNote != topNote:
                harmony2 = str(bottomNote) + str(topNote)
                harmonies.append(harmony2)
        storeInDatabase(harmonies, harmonicDatabase)


def store_harmonies_using_music21():
    for score in harmony_scores:
        moments = {}
        time_sigs, key_sigs = extract_info_from_score(score)
        for part in score.parts:
            notes = extract_note_info(part)
            for pitch_info, moment in notes:
                if moment not in moments:
                    moments[moment] = [pitch_info]
                moments[moment].append(pitch_info)
        for moment in moments:
            if len(moments[moment]) > 1:
                storeInDatabase(moments[moment], harmonicDatabase)



# Base code for quicksort taken from http://www.geeksforgeeks.org/iterative-quick-sort/


def partition(arr, low, high):
    i = (low-1)  # index of smaller element
    pivot = arr[high]  # pivot
    for j in range(low, high):
        # If current element is smaller than or
        # equal to pivot
        if arr[j].less_than_or_equal(pivot):
            # increment index of smaller element
            i = i+1
            arr[i], arr[j] = arr[j], arr[i]
    arr[i+1], arr[high] = arr[high], arr[i+1]
    return (i+1)

# The main function that implements QuickSort
# arr[] --> Array to be sorted,
# low  --> Starting index,
# high  --> Ending index

# Function to do Quick sort


def quickSort(arr, low, high):
    if low < high:
        # pi is partitioning index, arr[p] is now
        # at right place
        pi = partition(arr, low, high)
        # Separately sort elements before
        # partition and after partition
        quickSort(arr, low, pi-1)
        quickSort(arr, pi+1, high)


def sort(list):
    quickSort(list, 0, len(list) - 1)
