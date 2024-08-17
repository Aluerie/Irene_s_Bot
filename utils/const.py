from enum import IntEnum, StrEnum

# ruff: noqa: N815

ERROR_ROLE_MENTION = "<@&1116171071528374394>"


class ID(IntEnum):
    Irene = 180499648
    Bot = 519438249


class Name(StrEnum):
    Irene = "irene_adler__"


class DisplayName(StrEnum):
    Irene = "Irene_Adler__"


class Global(StrEnum):
    """Global emotes enabled everywhere"""

    # BTTV
    monkaS = "monkaS"

    # FFZ
    # None?..

    # STV
    EZ = "EZ"


class BTTV(StrEnum):
    """BTTV emotes enabled at @Irene channel"""

    peepoHey = "peepoHey"
    PogU = "PogU"
    Smoge = "Smoge"
    weirdChamp = "weirdChamp"


class FFZ(StrEnum):
    """FFZ emotes enabled at @Irene channel"""

    Weirdge = "Weirdge"
    monkaGIGA = "monkaGIGA"
    monkaGIGAGUN = "monkaGIGAGUN"
    monkaH = "monkaH"
    peepoPolice = "peepoPolice"
    peepoWTF = "peepoWTF"
    sadKEK = "sadKEK"


class STV(StrEnum):
    """7TV emotes enabled at @Irene channel"""

    Adge = "Adge"
    Cinema = "Cinema"
    DankApprove = "DankApprove"
    dankHey = "dankHey"
    DankL = "DankL"
    DankMods = "DankMods"
    DankDolmes = "DankDolmes"
    DankG = "DankG"
    DankLurk = "DankLurk"
    DankReading = "DankReading"
    DankThink = "DankThink"
    Deadge = "Deadge"
    Discord = "Discord"
    donkDetective = "donkDetective"
    donkHappy = "donkHappy"
    donkHey = "donkHey"
    donkJam = "donkJam"
    donkSad = "donkSad"
    DonkPrime = "DonkPrime"
    ermtosis = "ermtosis"
    Erm = "Erm"
    FeelsBingMan = "FeelsBingMan"
    FirstTimeChadder = "FirstTimeChadder"
    gg = "gg"
    GroupScoots = "GroupScoots"
    Hello = "Hello"
    Hey = "Hey"
    heyinoticedyouhaveaprimegamingbadgenexttoyourname = "heyinoticedyouhaveaprimegamingbadgenexttoyourname"
    hi = "hi"
    How2Read = "How2Read"
    Offline = "Offline"
    peepoDapper = "peepoDapper"
    Plink = "Plink"
    PogChampPepe = "PogChampPepe"
    POGCRAZY = "POGCRAZY"
    yo = "yo"
    uuh = "uuh"
    widepeepoHappyRightHeart = "widepeepoHappyRightHeart"
    wow = "wow"


class Bots(StrEnum):
    """List of known bot names.

    Mostly, used to identify other bots' messages.
    Variable name is supposed to be their display name while
    the value is lowercase name for easier comparing.
    """

    nine_kmmrbot = "9kmmrbot"
    dotabod = "dotabod"
    Fossabot = "fossabot"
    Irene_s_Bot = "irene_s_bot"
    LolRankBot = "lolrankbot"
    Moobot = "moobot"
    Nightbot = "nightbot"
    Sery_Bot = "sery_Bot"
    StreamLabs = "streamlabs"
    Streamelements = "streamelements"
    Supibot = "supibot"
    WizeBot = "wizeBot"


DIGITS = [
    "\N{DIGIT ZERO}\N{COMBINING ENCLOSING KEYCAP}",
    "\N{DIGIT ONE}\N{COMBINING ENCLOSING KEYCAP}",
    "\N{DIGIT TWO}\N{COMBINING ENCLOSING KEYCAP}",
    "\N{DIGIT THREE}\N{COMBINING ENCLOSING KEYCAP}",
    "\N{DIGIT FOUR}\N{COMBINING ENCLOSING KEYCAP}",
    "\N{DIGIT FIVE}\N{COMBINING ENCLOSING KEYCAP}",
    "\N{DIGIT SIX}\N{COMBINING ENCLOSING KEYCAP}",
    "\N{DIGIT SEVEN}\N{COMBINING ENCLOSING KEYCAP}",
    "\N{DIGIT EIGHT}\N{COMBINING ENCLOSING KEYCAP}",
    "\N{DIGIT NINE}\N{COMBINING ENCLOSING KEYCAP}",
]
