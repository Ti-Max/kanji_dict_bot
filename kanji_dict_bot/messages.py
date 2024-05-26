from inspect import cleandoc
import re

from anki.notes import Note

from anki_deck_reader import read_field


def span_to_underline(html: str) -> str:
    return (html.replace("<span", "<u")).replace("span>", "u>")


def split_radicals(radicals: str) -> str:
    out = ""
    for r in radicals.split(", "):
        out += f"<code>{r}</code>"

    return out


def radical_message(note: Note):
    radical = read_field(note, "Radical")
    if radical == "":
        parsed_radical = "{Not UTF-8}"
    else:
        parsed_radical = radical

    return cleandoc(
        f""" \
        🖊️ Radical: <code>{parsed_radical}</code>

        🔤 Name: <b>{read_field(note, "Radical_Name")}</b>

        🧠 Mnemonics:
        <i>{span_to_underline(read_field(note, "Radical_Meaning"))}</i>
        """
    )


def kanji_message(note: Note):
    return cleandoc(
        f""" \
        🖊️ Kanji: <code>{read_field(note, "Kanji")}</code>

        🔤 Meaning: <b>{read_field(note, "Kanji_Meaning")}</b>

        🧩 Radicals: <b>{split_radicals(read_field(note, "Radicals"))} ({read_field(note, "Radicals_Names")})</b>

        🧠 Mnemonics:
        <i>
        {span_to_underline(read_field(note, "Meaning_Mnemonic"))}

        {span_to_underline(read_field(note, "Meaning_Info"))}
        </i>
        """
    )


def remove_html(message: str):
    clean = re.compile("<.*?>")
    return re.sub(clean, "", message)
