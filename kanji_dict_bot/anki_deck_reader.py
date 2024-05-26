from typing import Literal, TypeAlias
from anki.collection import Collection
from pprint import pprint as pp
from anki.notes import Note
from termcolor import cprint

RadicalNoteFields: TypeAlias = Literal[
    "Radical_Name", "Radical", "Radical_Meaning", "Radical_Icon", "sort_id"
]

KanjiNoteFields: TypeAlias = Literal[
    "Kanji",
    "Kanji_Meaning",
    "Reading_On",
    "Reading_Kun",
    "Radicals",
    "Radicals_Icons",
    "Radicals_Names",
    "Radicals_Icons_Names",
    "Meaning_Mnemonic",
    "Meaning_Info",
    "Reading_Mnemonic",
    "Reading_Info",
    "sort_id",
]

VocabNoteFields: TypeAlias = Literal[
    "Vocab",
    "Vocab_Meaning",
    "Reading",
    "Speech_Type",
    "Context_jp",
    "Context_en",
    "Context_jp_2",
    "Context_en_2",
    "Context_jp_3",
    "Context_en_3",
    "Meaning_Exp",
    "Reading_Exp",
    "Kanji",
    "Kanji_Name",
    "Audio_b",
    "Audio_g",
    "sort_id",
]


def log_cards_count(col: Collection):
    radicals_count = len(col.find_notes('"deck:WaniKani Ultimate::-Radicals"'))
    kanji_count = len(col.find_notes('"deck:WaniKani Ultimate::Kanjis"'))
    vocab_count = len(col.find_notes('"deck:WaniKani Ultimate::Vocabulary"'))

    print(f"Total radicals: {radicals_count}")
    print(f"Total kanjis: {kanji_count}")
    print(f"Total vocabs: {vocab_count}")


def read_field(
    note: Note, field: RadicalNoteFields | KanjiNoteFields | VocabNoteFields
) -> str:
    return note.values()[note.keys().index(field)]


def search_radical(radical_name: str, radical: str):
    # search syntax is the same as in in the search box when you click on browse
    # it is a good idea to test queries in the anki app first
    # https://docs.ankiweb.net/searching.html
    if radical == "":
        search_results = col.find_notes(
            f'"deck:WaniKani Ultimate::-Radicals" "Radical_Name:{radical_name}"'
        )
    else:
        search_results = col.find_notes(
            f'"deck:WaniKani Ultimate::-Radicals" "Radical_Name:{radical_name}" OR Radical:{radical}'
        )

    if len(search_results) > 0:
        note = col.get_note(search_results[0])
        return note
    else:
        cprint(f"Radical '{radical_name}' was not found in Radicals deck", "yellow")
        return None


def search_kanji(kanji: str):
    # search syntax is the same as in in the search box when you click on browse
    # it is a good idea to test queries in the anki app first
    # https://docs.ankiweb.net/searching.html
    search_results = col.find_notes(f'"deck:WaniKani Ultimate::Kanjis" "Kanji:{kanji}"')

    if len(search_results) > 0:
        note = col.get_note(search_results[0])
        return note
    else:
        cprint(f"Kanji '{kanji}' was not found in Kanji deck", "yellow")
        return None


col = Collection("res/collection.anki2")
log_cards_count(col)
