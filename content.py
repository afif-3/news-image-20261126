"""Editorial content for the 26 November 2026 front page.

Every story below was cross-checked on the day against at least two
independent daily digests (One Turn's day report, the Daily Summary of
World, and Reuters' tariff analysis).  Facts are kept short so the page
stays legible at thumbnail size: one idea per line, numbers up front.
"""

DATE_LINE = "THURSDAY, NOVEMBER 26, 2026"
PAPER_NAME = "THE WORLD TODAY"
TAGLINE = "One page. One day. The whole planet."
EDITION_NOTE = "GLOBAL EDITION  -  65 STORIES TRACKED  -  MOOD: UNEASY"

LEAD = {
    "kicker": "TRADE  -  WASHINGTON",
    "headline": "AMERICA TAXES\nTHE WORLD AGAIN",
    "standfirst": (
        "The United States proposes new tariffs on 14 trading "
        "partners - China, the EU, Japan and India among them."
    ),
    "points": [
        "Rates up to 35% after an eight-month capacity probe",
        "China rejects the charges, stops short of retaliation",
        "Fourth Trump-Xi summit looms in Miami next month",
    ],
    "big_number": "14",
    "big_label": "economies\nin the firing line",
}

STORIES = [
    {
        "kicker": "CONFLICT  -  RIYADH",
        "headline": "Houthis strike Saudi\nports and refinery",
        "body": (
            "Attacks claimed on Saudi ports and the giant Ras "
            "Tanura refinery as defences intercept missiles over "
            "Riyadh. Brent crude tops $94."
        ),
        "accent": "oil",
    },
    {
        "kicker": "DISASTER  -  CAIRO",
        "headline": "Tanker fire kills 31\non Cairo ring road",
        "body": (
            "A fuel tanker overturned and burst into flames on "
            "the capital's busy ring road. At least 31 died and "
            "about 21 were injured."
        ),
        "accent": "fire",
    },
    {
        "kicker": "EUROPE  -  BRUSSELS",
        "headline": "EU leaders clash over\n45bn euro Ukraine loan",
        "body": (
            "Divisions over a loan for Kyiv and the bloc's next "
            "budget - as Ukraine reports damaging five jets at "
            "a Russian airbase."
        ),
        "accent": "eu",
    },
    {
        "kicker": "SPACE  -  TIANGONG",
        "headline": "First Pakistani astronaut\nboards China's station",
        "body": (
            "Muhammad Zeeshan Ali arrives aboard Shenzhou-24, "
            "the first foreign national to join Tiangong - a "
            "milestone for Beijing's space diplomacy."
        ),
        "accent": "space",
    },
]

MARKETS = {
    "kicker": "MARKETS  -  NEW YORK",
    "headline": "AI sell-off drags Nasdaq toward a bear market",
    "body": (
        "Selling in AI-linked stocks deepens - Nvidia falls 3.9% - "
        "even as the Dow closes above 50,000 for the first time."
    ),
    "stats": [
        ("NVIDIA", "-3.9%"),
        ("NASDAQ", "NEAR -20%"),
        ("DOW", "50,000+"),
        ("BRENT", "$94"),
    ],
}

TICKER = [
    "KIM JONG UN URGES WIDER TACTICAL NUCLEAR DEPLOYMENT",
    "SPAIN VOTES SUNDAY IN SNAP ELECTION",
    "RESCUERS RACE TO REACH 13 MINERS TRAPPED IN INDONESIA",
    "US TELLS CITIZENS TO LEAVE IRAN AS WAR FEARS GROW",
    "LIVERPOOL BEAT CLUB BRUGGE 3-0 IN CHAMPIONS LEAGUE",
    "JUDGES SUGGEST DROPPING TOP NETANYAHU CHARGE",
]

FOOTER = "Drawn entirely in code with Pillow  -  Sources: Reuters, One Turn, Daily Summary of World  -  26.11.2026"
