"""TRANSLATION COMMANDS.

Sources
-------
* My own discord bot (but the code there is also taken from other places)
    https://github.com/Aluerie/AluBot/blob/main/ext/educational/language/translation.py
"""

from __future__ import annotations

from typing import TYPE_CHECKING, NamedTuple, TypedDict

from twitchio.ext import commands

from bot import IrenesCog
from utils import const, errors

if TYPE_CHECKING:
    from aiohttp import ClientSession

    from bot import IrenesBot


# fmt: off
LANGUAGES = {  # there are 109 languages
    "af": "Afrikaans", "sq": "Albanian", "am": "Amharic", "ar": "Arabic", "hy": "Armenian", "az": "Azerbaijani",
    "eu": "Basque", "be": "Belarusian", "bn": "Bengali", "bs": "Bosnian", "bg": "Bulgarian", "ca": "Catalan",
    "ceb": "Cebuano", "ny": "Chichewa", "zh-cn": "Chinese (simplified)", "zh-tw": "Chinese (traditional)",
    "co": "Corsican", "hr": "Croatian", "cs": "Czech", "da": "Danish", "nl": "Dutch", "en": "English",
    "eo": "Esperanto", "et": "Estonian", "tl": "Filipino", "fi": "Finnish", "fr": "French", "fy": "Frisian",
    "gl": "Galician", "ka": "Georgian", "de": "German", "el": "Greek", "gu": "Gujarati", "ht": "Haitian creole",
    "ha": "Hausa", "haw": "Hawaiian", "iw": "Hebrew", "he": "Hebrew", "hi": "Hindi", "hmn": "Hmong", "hu": "Hungarian",
    "is": "Icelandic", "ig": "Igbo", "id": "Indonesian", "ga": "Irish", "it": "Italian", "ja": "Japanese",
    "jw": "Javanese", "kn": "Kannada", "kk": "Kazakh", "km": "Khmer", "ko": "Korean", "ku": "Kurdish (kurmanji)",
    "ky": "Kyrgyz", "lo": "Lao", "la": "Latin", "lv": "Latvian", "lt": "Lithuanian", "lb": "Luxembourgish",
    "mk": "Macedonian", "mg": "Malagasy", "ms": "Malay", "ml": "Malayalam", "mt": "Maltese", "mi": "Maori",
    "mr": "Marathi", "mn": "Mongolian", "my": "Myanmar (burmese)", "ne": "Nepali", "no": "Norwegian", "or": "Odia",
    "ps": "Pashto", "fa": "Persian", "pl": "Polish", "pt": "Portuguese", "pa": "Punjabi", "ro": "Romanian",
    "ru": "Russian", "sm": "Samoan", "gd": "Scots gaelic", "sr": "Serbian", "st": "Sesotho", "sn": "Shona",
    "sd": "Sindhi", "si": "Sinhala", "sk": "Slovak", "sl": "Slovenian", "so": "Somali", "es": "Spanish",
    "su": "Sundanese", "sw": "Swahili", "sv": "Swedish", "tg": "Tajik", "ta": "Tamil", "tt": "Tatar", "te": "Telugu",
    "th": "Thai", "tr": "Turkish", "tk": "Turkmen", "uk": "Ukrainian", "ur": "Urdu", "ug": "Uyghur", "uz": "Uzbek",
    "vi": "Vietnamese", "cy": "Welsh", "xh": "Xhosa", "yi": "Yiddish", "yo": "Yoruba", "zu": "Zulu",
}
# fmt: on


class TranslatedSentence(TypedDict):
    """TranslatedSentence."""

    trans: str
    orig: str


class TranslateResult(NamedTuple):
    """TranslatedResult."""

    original: str
    translated: str
    source_lang: str
    target_lang: str


async def translate(
    text: str,
    *,
    source_lang: str = "auto",
    target_lang: str = "en",
    session: ClientSession,
) -> TranslateResult:
    """Google Translate."""
    query = {
        "dj": "1",
        "dt": ["sp", "t", "ld", "bd"],
        "client": "dict-chrome-ex",  # Needs to be dict-chrome-ex or else you'll get a 403 error.
        "sl": source_lang,
        "tl": target_lang,
        "q": text,
    }

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/104.0.0.0 Safari/537.36"
        )
    }

    async with session.get("https://clients5.google.com/translate_a/single", params=query, headers=headers) as resp:
        if resp.status != 200:
            raise errors.TranslateError(resp.status, text=await resp.text())

        data = await resp.json()
        src = data.get("src", "Unknown")
        sentences: list[TranslatedSentence] = data.get("sentences", [])
        if not sentences:
            msg = "Google translate returned no information"
            raise RuntimeError(msg)

        return TranslateResult(
            original="".join(sentence.get("orig", "") for sentence in sentences),
            translated="".join(sentence.get("trans", "") for sentence in sentences),
            source_lang=LANGUAGES.get(src, src),
            target_lang=LANGUAGES.get(target_lang, "Unknown"),
        )


class TranslationCog(IrenesCog):
    """Translation command cog."""

    @commands.command()
    async def translate(self, ctx: commands.Context, *, text: str) -> None:
        """Translate to English.

        Uses Google Translate. Autodetects source language.
        """
        result = await translate(text, session=self.bot.session)
        answer = f"[{result.source_lang} to {result.target_lang}] {const.STV.ApuBritish} {result.translated}"
        await ctx.send(answer)


def prepare(bot: IrenesBot) -> None:
    """Load IrenesBot extension. Framework of twitchio."""
    bot.add_cog(TranslationCog(bot))
