from enum import IntEnum, StrEnum

# ruff: noqa: N815

ERROR_ROLE_MENTION = "<@&1116171071528374394>"


class ID(IntEnum):
    Irene = 180499648
    Bot = 519438249


class Name(StrEnum):
    Irene = "Irene_Adler__"


class Global(StrEnum):
    # BTTV
    monkaS = "monkaS"


class BTTV(StrEnum):
    PogU = "PogU"
    Smoge = "Smoge"


class FFZ(StrEnum):
    Weirdge = "Weirdge"
    monkaGIGA = "monkaGIGA"
    monkaGIGAGUN = "monkaGIGAGUN"
    monkaH = "monkaH"
    peepoWTF = "peepoWTF"


class STV(StrEnum):
    Adge = "Adge"
    Cinema = "Cinema"
    DankApprove = "DankApprove"
    DankMods = "DankMods"
    DankDolmes = "DankDolmes"
    DankLurk = "DankLurk"
    DankReading = "DankReading"
    DankThink = "DankThink"
    Deadge = "Deadge"
    Discord = "Discord"
    donkDetective = "donkDetective"
    donkHappy = "donkHappy"
    donkJam = "donkJam"
    DonkPrime = "DonkPrime"
    Erm = "Erm"
    FeelsBingMan = "FeelsBingMan"
    GroupScoots = "GroupScoots"
    Hello = "Hello"
    heyinoticedyouhaveaprimegamingbadgenexttoyourname = "heyinoticedyouhaveaprimegamingbadgenexttoyourname"
    hi = "hi"
    How2Read = "How2Read"
    Offline = "Offline"
    peepoDapper = "peepoDapper"
    peepoPolice = "peepoPolice"
    PogChampPepe = "PogChampPepe"
    POGCRAZY = "POGCRAZY"
    yo = "yo"
    uuh = "uuh"


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


# fmt: off
class Bots(StrEnum):
    nine_kmmrbot   = "9kmmrbot"
    dotabod        = "dotabod"
    Fossabot       = "fossabot"
    Irene_s_Bot    = "irene_s_bot"
    LolRankBot     = "lolrankbot"
    Moobot         = "moobot"
    Nightbot       = "nightbot"
    Sery_Bot       = "Sery_Bot"
    StreamLabs     = "streamlabs"
    Streamelements = "streamelements"
    Supibot        = "supibot"
    WizeBot        = "wizeBot"
# fmt: on
