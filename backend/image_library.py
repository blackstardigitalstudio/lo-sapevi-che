"""Image library: multiple curated Unsplash images per category.

Each category has 4-6 varied images. Each fact gets a deterministic image
based on a hash of its title, so the same fact always shows the same image
but different facts in the same category show different images.
"""
import hashlib
from typing import List

_CDN = "https://images.unsplash.com/"
_PARAMS = "?w=900&q=80&auto=format&fit=crop"


def _u(photo_id: str) -> str:
    return f"{_CDN}{photo_id}{_PARAMS}"


CATEGORY_IMAGES = {
    "Spazio": [
        _u("photo-1462331940025-496dfbfc7564"),  # galaxy
        _u("photo-1446776653964-20c1d3a81b06"),  # nebula
        _u("photo-1451187580459-43490279c0fa"),  # earth
        _u("photo-1543722530-d2c3201371e7"),     # planet
        _u("photo-1516339901601-2e1b62dc0c45"),  # astronaut
        _u("photo-1502134249126-9f3755a50d78"),  # stars
    ],
    "Scienza": [
        _u("photo-1532094349884-543bc11b234d"),  # microscope
        _u("photo-1628595351029-c2bf17511435"),  # lab
        _u("photo-1532187863486-abf9dbad1b69"),  # science
        _u("photo-1614935151651-0bea6508db6b"),  # tubes
        _u("photo-1581093588401-fbb62a02f120"),  # formula
        _u("photo-1554475901-4538ddfbccc2"),     # atom
    ],
    "Tecnologia": [
        _u("photo-1518770660439-4636190af475"),  # circuit
        _u("photo-1550439062-609e1531270e"),     # code
        _u("photo-1526374965328-7f61d4dc18c5"),  # binary
        _u("photo-1488229297570-58520851e868"),  # chip
        _u("photo-1518709268805-4e9042af2176"),  # computer
        _u("photo-1535378917042-10a22c95931a"),  # tech abstract
    ],
    "Natura": [
        _u("photo-1441974231531-c6227db76b6e"),  # forest misty
        _u("photo-1470071459604-3b5ec3a7fe05"),  # mountain clouds
        _u("photo-1472214103451-9374bd1c798e"),  # nature sunset
        _u("photo-1501785888041-af3ef285b470"),  # lake reflection
        _u("photo-1493246507139-91e8fad9978e"),  # aurora
        _u("photo-1433086966358-54859d0ed716"),  # waterfall
    ],
    "Storia": [
        _u("photo-1515162816999-a0c47dc192f7"),  # roman ruins
        _u("photo-1552832230-c0197dd311b5"),     # colosseum
        _u("photo-1599946347371-68eb71b16afc"),  # manuscript
        _u("photo-1519677100203-a0e668c92439"),  # castle
        _u("photo-1526912301892-fec5b6d833d5"),  # statue
        _u("photo-1589828994425-a83f2f9b8488"),  # ancient temple
    ],
    "Mitologia": [
        _u("photo-1541432901042-2d8bd64b4a9b"),  # statue greek
        _u("photo-1533425962554-cf87ed6130b4"),  # temple columns
        _u("photo-1552832230-c0197dd311b5"),     # colosseum
        _u("photo-1565106430482-8f6e74349ca1"),  # ancient sculpture
        _u("photo-1608889476561-6242cfdbf622"),  # medusa
    ],
    "Cucina": [
        _u("photo-1504674900247-0877df9cc836"),  # plated dish
        _u("photo-1565299624946-b28f40a0ae38"),  # pizza
        _u("photo-1473093295043-cdd812d0e601"),  # pasta
        _u("photo-1498579150354-977475b7ea0b"),  # spices
        _u("photo-1555939594-58d7cb561ad1"),     # italian dish
        _u("photo-1414235077428-338989a2e8c0"),  # chef
    ],
    "Sport": [
        _u("photo-1459865264687-595d652de67e"),  # stadium
        _u("photo-1461896836934-ffe607ba8211"),  # running
        _u("photo-1579952363873-27f3bade9f55"),  # fitness
        _u("photo-1517649763962-0c623066013b"),  # soccer
        _u("photo-1546519638-68e109498ffc"),     # weights
        _u("photo-1552667466-07770ae110d0"),     # basketball
    ],
    "Arte": [
        _u("photo-1513364776144-60967b0f800f"),  # gallery
        _u("photo-1579783902614-a3fb3927b6a5"),  # painting
        _u("photo-1536924430914-91f9e2041b83"),  # brushes
        _u("photo-1544967082-d9d25d867d66"),     # statue art
        _u("photo-1578662996442-48f60103fc96"),  # louvre
        _u("photo-1558865869-c93f6f8482af"),     # oil painting
    ],
    "Psicologia": [
        _u("photo-1559757148-5c350d0d3c56"),     # brain
        _u("photo-1544367567-0f2fcb009e0b"),     # meditation
        _u("photo-1529333166437-7750a6dd5a70"),  # thinking
        _u("photo-1499209974431-9dddcece7f88"),  # mind
        _u("photo-1474418397713-b1eac5595a4e"),  # head silhouette
    ],
    "Cinema": [
        _u("photo-1489599849927-2ee91cede3ba"),  # film reel
        _u("photo-1485846234645-a62644f84728"),  # cinema seats
        _u("photo-1440404653325-ab127d49abc1"),  # film strip
        _u("photo-1478720568477-152d9b164e26"),  # clapperboard
        _u("photo-1524985069026-dd778a71c7b4"),  # theater
    ],
    "Musica": [
        _u("photo-1511671782779-c97d3d27a1d4"),  # vinyl
        _u("photo-1470225620780-dba8ba36b745"),  # concert
        _u("photo-1493225457124-a3eb161ffa5f"),  # piano
        _u("photo-1514320291840-2e0a9bf2a9ae"),  # guitar
        _u("photo-1485579149621-3123dd979885"),  # notes sheet
        _u("photo-1459749411175-04bf5292ceea"),  # microphone
    ],
    "Geografia": [
        _u("photo-1519074002996-a69e7ac46a42"),  # globe
        _u("photo-1524661135-423995f22d0b"),     # vintage map
        _u("photo-1476973422084-e0fa66ff9456"),  # earth from space
        _u("photo-1531065208531-4036c0dba3ca"),  # compass
        _u("photo-1524813686514-a57563d77965"),  # mountains
    ],
    "Medicina": [
        _u("photo-1583912267550-aae6fa8c775a"),  # stethoscope
        _u("photo-1576091160399-112ba8d25d1d"),  # pills
        _u("photo-1559757175-5700dde675bc"),     # doctor
        _u("photo-1579684385127-1ef15d508118"),  # heart
        _u("photo-1631815588090-d4bfec5b9c3f"),  # lab
    ],
    "Filosofia": [
        _u("photo-1544967082-d9d25d867d66"),     # thinker statue
        _u("photo-1504052434569-70ad5836ab65"),  # old books
        _u("photo-1476275466078-4007374efbbe"),  # library
        _u("photo-1447069387593-a5de0862481e"),  # ancient scripture
    ],
    "Economia": [
        _u("photo-1611974789855-9c2a0a7236a3"),  # coins
        _u("photo-1579532537598-459ecdaf39cc"),  # chart
        _u("photo-1590283603385-17ffb3a7f29f"),  # market
        _u("photo-1526304640581-d334cdbbf45e"),  # dollar
        _u("photo-1559526324-4b87b5e36e44"),     # trading
    ],
    "Letteratura": [
        _u("photo-1481627834876-b7833e8f5570"),  # old library
        _u("photo-1519682337058-a94d519337bc"),  # open book
        _u("photo-1524995997946-a1c2e315a42f"),  # books tall
        _u("photo-1495446815901-a7297e633e8d"),  # typewriter
        _u("photo-1457369804613-52c61a468e7d"),  # reading lamp
    ],
    "Animali": [
        _u("photo-1501854140801-50d01698950b"),  # wildlife
        _u("photo-1474511320723-9a56873867b5"),  # fox
        _u("photo-1546182990-dffeafbe841d"),     # owl
        _u("photo-1535338454770-8be927b5a00b"),  # elephant
        _u("photo-1437622368342-7a3d73a34c8f"),  # turtle
    ],
    "Matematica": [
        _u("photo-1509228468518-180dd4864904"),  # equations chalk
        _u("photo-1635070041078-e363dbe005cb"),  # numbers
        _u("photo-1635070041409-e63b10cfe37c"),  # math abstract
        _u("photo-1509228627152-72ae9ae6848d"),  # abacus
        _u("photo-1596495578065-6e0763fa1178"),  # geometry
    ],
    "Viaggi": [
        _u("photo-1488646953014-85cb44e25828"),  # suitcase
        _u("photo-1436491865332-7a61a109cc05"),  # airplane window
        _u("photo-1530521954074-e64f6810b32d"),  # compass map
        _u("photo-1517760444937-f6397edcbbcd"),  # passport
        _u("photo-1503220317375-aaad61436b1b"),  # backpack travel
    ],
    "Mafia": [
        _u("photo-1507679799987-c73779587ccf"),  # suit man shadow
        _u("photo-1519415943484-9fa1873496d4"),  # cigar dark
        _u("photo-1568214379698-8aeb8c6c6ac8"),  # vintage car dark
        _u("photo-1461151304267-38535e780c79"),  # noir alley
        _u("photo-1497215842964-222b430dc094"),  # old typewriter
    ],
    "Guerre": [
        _u("photo-1526803150637-f3705c1b7da4"),  # soldier silhouette
        _u("photo-1541516160071-4bb0c5af65ba"),  # tank
        _u("photo-1516575355023-c28313324ca9"),  # military
        _u("photo-1530260626-82b39f5cca29"),     # old war photo
        _u("photo-1506806732259-39c2d0268443"),  # memorial
    ],
    "Motori": [
        _u("photo-1503376780353-7e6692767b70"),  # sports car
        _u("photo-1519925610903-381054cc2a1c"),  # formula 1
        _u("photo-1493238792000-8113da705763"),  # race track
        _u("photo-1571068316344-75bc76f77890"),  # motorcycle
        _u("photo-1505761671935-60b3a7427bad"),  # classic car
    ],
    "Macchine": [
        _u("photo-1503376780353-7e6692767b70"),  # sports car red
        _u("photo-1552519507-da3b142c6e3d"),     # ferrari like
        _u("photo-1544829099-b9a0c5303bea"),     # lamborghini
        _u("photo-1542282088-fe8426682b8f"),     # classic
        _u("photo-1511919884226-fd3cad34687c"),  # porsche
        _u("photo-1494976388531-d1058494cdd8"),  # muscle car
    ],
    "Moto": [
        _u("photo-1568772585407-9361f9bf3a87"),  # motorcycle
        _u("photo-1558981806-ec527fa84c39"),     # ducati red
        _u("photo-1547549082-6bc09f2049ae"),     # rider sunset
        _u("photo-1558981001-5864b3250a69"),     # vintage moto
        _u("photo-1571068316344-75bc76f77890"),  # sport bike
    ],
}

# Fallback for any missing category
_FALLBACK = CATEGORY_IMAGES["Spazio"]


def image_for_fact(category: str, seed: str) -> str:
    """Deterministically pick an image for a fact based on hash of its seed (e.g. title)."""
    pool: List[str] = CATEGORY_IMAGES.get(category, _FALLBACK)
    if not pool:
        pool = _FALLBACK
    h = int(hashlib.md5(str(seed).encode("utf-8")).hexdigest()[:8], 16)
    return pool[h % len(pool)]


def first_image_for_category(category: str) -> str:
    pool = CATEGORY_IMAGES.get(category, _FALLBACK)
    return pool[0] if pool else _FALLBACK[0]
