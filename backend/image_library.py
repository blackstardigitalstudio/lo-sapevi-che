"""Image library: multiple curated Unsplash images per category and sub-category.

Only URLs verified to return HTTP 200 should live here.
"""
import hashlib
from typing import Dict, List, Optional

_CDN = "https://images.unsplash.com/"
_PARAMS = "?w=900&q=80&auto=format&fit=crop"


def _u(photo_id: str) -> str:
    return f"{_CDN}{photo_id}{_PARAMS}"


CATEGORY_IMAGES = {
    "Spazio": [
        _u("photo-1462331940025-496dfbfc7564"),
        _u("photo-1446776653964-20c1d3a81b06"),
        _u("photo-1451187580459-43490279c0fa"),
        _u("photo-1543722530-d2c3201371e7"),
        _u("photo-1516339901601-2e1b62dc0c45"),
        _u("photo-1502134249126-9f3755a50d78"),
    ],
    "Scienza": [
        _u("photo-1532094349884-543bc11b234d"),
        _u("photo-1628595351029-c2bf17511435"),
        _u("photo-1532187863486-abf9dbad1b69"),
        _u("photo-1614935151651-0bea6508db6b"),
        _u("photo-1581093588401-fbb62a02f120"),
        _u("photo-1554475901-4538ddfbccc2"),
    ],
    "Tecnologia": [
        _u("photo-1518770660439-4636190af475"),
        _u("photo-1550439062-609e1531270e"),
        _u("photo-1526374965328-7f61d4dc18c5"),
        _u("photo-1488229297570-58520851e868"),
        _u("photo-1535378917042-10a22c95931a"),
    ],
    "Natura": [
        _u("photo-1441974231531-c6227db76b6e"),
        _u("photo-1470071459604-3b5ec3a7fe05"),
        _u("photo-1472214103451-9374bd1c798e"),
        _u("photo-1501785888041-af3ef285b470"),
        _u("photo-1493246507139-91e8fad9978e"),
        _u("photo-1433086966358-54859d0ed716"),
    ],
    "Storia": [
        _u("photo-1515162816999-a0c47dc192f7"),
        _u("photo-1552832230-c0197dd311b5"),
        _u("photo-1599946347371-68eb71b16afc"),
        _u("photo-1519677100203-a0e668c92439"),
    ],
    "Mitologia": [
        _u("photo-1541432901042-2d8bd64b4a9b"),
        _u("photo-1552832230-c0197dd311b5"),
        _u("photo-1565106430482-8f6e74349ca1"),
        _u("photo-1564399579883-451a5d44ec08"),
    ],
    "Cucina": [
        _u("photo-1504674900247-0877df9cc836"),
        _u("photo-1565299624946-b28f40a0ae38"),
        _u("photo-1473093295043-cdd812d0e601"),
        _u("photo-1498579150354-977475b7ea0b"),
        _u("photo-1555939594-58d7cb561ad1"),
        _u("photo-1414235077428-338989a2e8c0"),
    ],
    "Sport": [
        _u("photo-1459865264687-595d652de67e"),
        _u("photo-1461896836934-ffe607ba8211"),
        _u("photo-1579952363873-27f3bade9f55"),
        _u("photo-1517649763962-0c623066013b"),
        _u("photo-1546519638-68e109498ffc"),
        _u("photo-1552667466-07770ae110d0"),
    ],
    "Arte": [
        _u("photo-1513364776144-60967b0f800f"),
        _u("photo-1579783902614-a3fb3927b6a5"),
        _u("photo-1536924430914-91f9e2041b83"),
        _u("photo-1544967082-d9d25d867d66"),
        _u("photo-1578662996442-48f60103fc96"),
        _u("photo-1558865869-c93f6f8482af"),
    ],
    "Psicologia": [
        _u("photo-1559757148-5c350d0d3c56"),
        _u("photo-1544367567-0f2fcb009e0b"),
        _u("photo-1529333166437-7750a6dd5a70"),
        _u("photo-1499209974431-9dddcece7f88"),
    ],
    "Cinema": [
        _u("photo-1489599849927-2ee91cede3ba"),
        _u("photo-1485846234645-a62644f84728"),
        _u("photo-1440404653325-ab127d49abc1"),
        _u("photo-1478720568477-152d9b164e26"),
        _u("photo-1524985069026-dd778a71c7b4"),
    ],
    "Musica": [
        _u("photo-1511671782779-c97d3d27a1d4"),
        _u("photo-1470225620780-dba8ba36b745"),
        _u("photo-1493225457124-a3eb161ffa5f"),
        _u("photo-1514320291840-2e0a9bf2a9ae"),
        _u("photo-1485579149621-3123dd979885"),
        _u("photo-1459749411175-04bf5292ceea"),
    ],
    "Geografia": [
        _u("photo-1519074002996-a69e7ac46a42"),
        _u("photo-1524661135-423995f22d0b"),
        _u("photo-1476973422084-e0fa66ff9456"),
        _u("photo-1531065208531-4036c0dba3ca"),
        _u("photo-1524813686514-a57563d77965"),
    ],
    "Medicina": [
        _u("photo-1576091160399-112ba8d25d1d"),
        _u("photo-1559757175-5700dde675bc"),
        _u("photo-1579684385127-1ef15d508118"),
    ],
    "Filosofia": [
        _u("photo-1544967082-d9d25d867d66"),
        _u("photo-1504052434569-70ad5836ab65"),
        _u("photo-1476275466078-4007374efbbe"),
        _u("photo-1447069387593-a5de0862481e"),
    ],
    "Economia": [
        _u("photo-1611974789855-9c2a0a7236a3"),
        _u("photo-1579532537598-459ecdaf39cc"),
        _u("photo-1590283603385-17ffb3a7f29f"),
        _u("photo-1526304640581-d334cdbbf45e"),
        _u("photo-1559526324-4b87b5e36e44"),
    ],
    "Letteratura": [
        _u("photo-1481627834876-b7833e8f5570"),
        _u("photo-1519682337058-a94d519337bc"),
        _u("photo-1524995997946-a1c2e315a42f"),
        _u("photo-1495446815901-a7297e633e8d"),
        _u("photo-1457369804613-52c61a468e7d"),
    ],
    "Animali": [
        _u("photo-1501854140801-50d01698950b"),
        _u("photo-1474511320723-9a56873867b5"),
        _u("photo-1546182990-dffeafbe841d"),
        _u("photo-1535338454770-8be927b5a00b"),
        _u("photo-1437622368342-7a3d73a34c8f"),
    ],
    "Matematica": [
        _u("photo-1509228468518-180dd4864904"),
        _u("photo-1635070041078-e363dbe005cb"),
        _u("photo-1509228627152-72ae9ae6848d"),
        _u("photo-1596495578065-6e0763fa1178"),
    ],
    "Viaggi": [
        _u("photo-1488646953014-85cb44e25828"),
        _u("photo-1436491865332-7a61a109cc05"),
        _u("photo-1530521954074-e64f6810b32d"),
        _u("photo-1517760444937-f6397edcbbcd"),
        _u("photo-1503220317375-aaad61436b1b"),
    ],
    "Mafia": [
        _u("photo-1507679799987-c73779587ccf"),
        _u("photo-1519415943484-9fa1873496d4"),
        _u("photo-1568214379698-8aeb8c6c6ac8"),
        _u("photo-1461151304267-38535e780c79"),
        _u("photo-1497215842964-222b430dc094"),
    ],
    "Guerre": [
        _u("photo-1541516160071-4bb0c5af65ba"),
        _u("photo-1506806732259-39c2d0268443"),
        _u("photo-1515162816999-a0c47dc192f7"),
    ],
    "Motori": [
        _u("photo-1503376780353-7e6692767b70"),
        _u("photo-1583121274602-3e2820c69888"),
        _u("photo-1493238792000-8113da705763"),
        _u("photo-1609630875171-b1321377ee65"),
        _u("photo-1552519507-da3b142c6e3d"),
    ],
    "Macchine": [
        _u("photo-1503376780353-7e6692767b70"),
        _u("photo-1552519507-da3b142c6e3d"),
        _u("photo-1542282088-fe8426682b8f"),
        _u("photo-1511919884226-fd3cad34687c"),
        _u("photo-1494976388531-d1058494cdd8"),
    ],
    "Moto": [
        _u("photo-1568772585407-9361f9bf3a87"),
        _u("photo-1558981806-ec527fa84c39"),
        _u("photo-1547549082-6bc09f2049ae"),
        _u("photo-1558981001-5864b3250a69"),
        _u("photo-1609630875171-b1321377ee65"),
    ],
    "Invenzioni": [
        _u("photo-1518770660439-4636190af475"),
        _u("photo-1581091226825-a6a2a5aee158"),
        _u("photo-1453733190371-0a9bedd82893"),
        _u("photo-1581092795360-fd1ca04f0952"),
        _u("photo-1504384308090-c894fdcc538d"),
    ],
    "Disastri": [
        _u("photo-1547683905-f686c993aae5"),
        _u("photo-1569091791842-7cfb64e04797"),
        _u("photo-1527482797697-8795b05a13fe"),
        _u("photo-1505322022379-7c3353ee6291"),
        _u("photo-1541516160071-4bb0c5af65ba"),
    ],
    "Religioni": [
        _u("photo-1507692049790-de58290a4334"),
        _u("photo-1519915028121-7d3463d20b13"),
        _u("photo-1438032005730-c779502df39b"),
        _u("photo-1519817650390-64a93db51149"),
        _u("photo-1552832230-c0197dd311b5"),
    ],
    "Misteri": [
        _u("photo-1478760329108-5c3ed9d495a0"),
        _u("photo-1509248961158-e54f6934749c"),
        _u("photo-1531065208531-4036c0dba3ca"),
        _u("photo-1531306728370-e2ebd9d7bb99"),
        _u("photo-1476275466078-4007374efbbe"),
    ],
}


# ============================================================
# SUB-CATEGORY specific images (brands, themes) - all verified
# ============================================================
SUBCATEGORY_IMAGES = {
    # ---- Moto brands ----
    "Vespa": [
        _u("photo-1609630875171-b1321377ee65"),
        _u("photo-1558981001-5864b3250a69"),
        _u("photo-1547549082-6bc09f2049ae"),
    ],
    "Ducati": [
        _u("photo-1558981806-ec527fa84c39"),
        _u("photo-1568772585407-9361f9bf3a87"),
        _u("photo-1609630875171-b1321377ee65"),
    ],
    "Harley-Davidson": [
        _u("photo-1568772585407-9361f9bf3a87"),
        _u("photo-1449426468159-d96dbf08f19f"),
    ],
    "Yamaha": [
        _u("photo-1558981806-ec527fa84c39"),
        _u("photo-1609630875171-b1321377ee65"),
    ],
    "Honda": [
        _u("photo-1558981001-5864b3250a69"),
        _u("photo-1568772585407-9361f9bf3a87"),
    ],
    "MV Agusta": [
        _u("photo-1558981806-ec527fa84c39"),
        _u("photo-1609630875171-b1321377ee65"),
    ],
    # ---- Auto brands ----
    "Ferrari": [
        _u("photo-1552519507-da3b142c6e3d"),
        _u("photo-1503376780353-7e6692767b70"),
        _u("photo-1583121274602-3e2820c69888"),
        _u("photo-1600712242805-5f78671b24da"),
    ],
    "Lamborghini": [
        _u("photo-1621135802920-133df287f89c"),
        _u("photo-1606664515524-ed2f786a0bd6"),
        _u("photo-1503376780353-7e6692767b70"),
    ],
    "Porsche": [
        _u("photo-1511919884226-fd3cad34687c"),
        _u("photo-1503376780353-7e6692767b70"),
        _u("photo-1580273916550-e323be2ae537"),
    ],
    "Tesla": [
        _u("photo-1560958089-b8a1929cea89"),
        _u("photo-1617788138017-80ad40651399"),
        _u("photo-1551830820-330a71b99659"),
        _u("photo-1617814065893-00757125efab"),
    ],
    "Fiat": [
        _u("photo-1541443131876-44b03de101c5"),
        _u("photo-1554744512-d6c603f27c54"),
        _u("photo-1588636142475-a62d56692870"),
        _u("photo-1606220945770-b5b6c2c55bf1"),
    ],
    "BMW": [
        _u("photo-1555215695-3004980ad54e"),
        _u("photo-1617531653332-bd46c24f2068"),
        _u("photo-1580274455191-1c62238fa333"),
    ],
    "Mercedes": [
        _u("photo-1618843479313-40f8afb4b4d8"),
        _u("photo-1617531653332-bd46c24f2068"),
        _u("photo-1563720223185-11003d516935"),
    ],
    "Alfa Romeo": [
        _u("photo-1552519507-da3b142c6e3d"),
        _u("photo-1503376780353-7e6692767b70"),
        _u("photo-1583121274602-3e2820c69888"),
    ],
    "Maserati": [
        _u("photo-1552519507-da3b142c6e3d"),
        _u("photo-1503376780353-7e6692767b70"),
    ],
    "Bugatti": [
        _u("photo-1580273916550-e323be2ae537"),
    ],
    "Aston Martin": [
        _u("photo-1511919884226-fd3cad34687c"),
        _u("photo-1580273916550-e323be2ae537"),
    ],
    "Rolls-Royce": [
        _u("photo-1563720223185-11003d516935"),
        _u("photo-1618843479313-40f8afb4b4d8"),
    ],
    # ---- Motori sub-themes ----
    "Formula 1": [
        _u("photo-1583121274602-3e2820c69888"),
        _u("photo-1600712242805-5f78671b24da"),
        _u("photo-1599819811279-d5ad9cccf838"),
    ],
    "MotoGP": [
        _u("photo-1568772585407-9361f9bf3a87"),
        _u("photo-1558981806-ec527fa84c39"),
        _u("photo-1609630875171-b1321377ee65"),
    ],
    "Rally": [
        _u("photo-1493238792000-8113da705763"),
        _u("photo-1580273916550-e323be2ae537"),
    ],
    "Auto d'epoca": [
        _u("photo-1552519507-da3b142c6e3d"),
        _u("photo-1542282088-fe8426682b8f"),
        _u("photo-1494976388531-d1058494cdd8"),
    ],
}

# ==========================================================
# KEYWORD-BASED IMAGE MATCHING
# ==========================================================
# Matched against lowercase fact title + short_fact. First keyword hit wins.
# Keywords use Italian stems so both singular/plural & declensions match
# (e.g. "pinguin" catches "pinguino", "pinguini"; "koala" stays as-is).
KEYWORD_IMAGES: Dict[str, List[str]] = {
    "pinguin": [
        _u("photo-1551986782-d0169b3f8fa7"),
        _u("photo-1598439210625-5067c578f3f6"),
        _u("photo-1517783999520-f068d7431a60"),
    ],
    "koala": [
        _u("photo-1459262838948-3e2de6c1ec80"),
    ],
    "polpo": [
        _u("photo-1545671913-b89ac1b4ac10"),
        _u("photo-1566417713940-fe7c737a9ef2"),
        _u("photo-1580019542155-247062e19ce4"),
    ],
    "piovr": [
        _u("photo-1545671913-b89ac1b4ac10"),
        _u("photo-1566417713940-fe7c737a9ef2"),
    ],
    "delfin": [
        _u("photo-1607153333879-c174d265f1d2"),
    ],
    "tartarug": [
        _u("photo-1437622368342-7a3d73a34c8f"),
        _u("photo-1591025207163-942350e47db2"),
    ],
    "balen": [
        _u("photo-1568430462989-44163eb1752f"),
        _u("photo-1551244072-5d12893278ab"),
    ],
    "squal": [
        _u("photo-1560275619-4662e36fa65c"),
    ],
    "leone": [
        _u("photo-1546182990-dffeafbe841d"),
        _u("photo-1534188753412-3e26d0d618d6"),
    ],
    "tigre": [
        _u("photo-1561731216-c3a4d99437d5"),
        _u("photo-1549480017-d76466a4b7e8"),
    ],
    "elefant": [
        _u("photo-1564760055775-d63b17a55c44"),
    ],
    "giraff": [
        _u("photo-1547721064-da6cfb341d50"),
        _u("photo-1534567110243-8875d64ca8ff"),
    ],
    "panda": [
        _u("photo-1564349683136-77e08dba1ef7"),
        _u("photo-1527118732049-c88155f2107c"),
    ],
    "orso": [
        _u("photo-1530595467537-0b5996c41f2d"),
        _u("photo-1446824505046-e43605ffb17f"),
    ],
    "lupo": [
        _u("photo-1564466809058-bf4114d55352"),
    ],
    "volpe": [
        _u("photo-1474511320723-9a56873867b5"),
        _u("photo-1516934024742-b461fba47600"),
    ],
    "scimm": [
        _u("photo-1540573133985-87b6da6d54a9"),
    ],
    "serpent": [
        _u("photo-1531386151447-fd76ad50012f"),
    ],
    "ape": [
        _u("photo-1464809142576-df63ca4ed7f0"),
        _u("photo-1568526381923-caf3fd520382"),
    ],
    "formica": [
        _u("photo-1535941339077-2dd1c7963098"),
    ],
    "cavall": [
        _u("photo-1553284965-83fd3e82fa5a"),
    ],
    "gatt": [
        _u("photo-1514888286974-6c03e2ca1dba"),
        _u("photo-1533738363-b7f9aef128ce"),
    ],
    "cane ": [
        _u("photo-1587300003388-59208cc962cb"),
        _u("photo-1548199973-03cce0bbc87b"),
    ],
    "fenicott": [
        _u("photo-1497206365907-f5e630693df0"),
        _u("photo-1505506874110-6a7a69069a08"),
    ],
    "aquil": [
        _u("photo-1551972251-12070d63502a"),
        _u("photo-1549366021-9f761d450615"),
    ],
    "pesce": [
        _u("photo-1524704654690-b56c05c78a00"),
        _u("photo-1535591273668-578e31182c4f"),
    ],
    "luna": [
        _u("photo-1532693322450-2cb5c511067d"),
        _u("photo-1514897575457-c4db467cf78e"),
    ],
    "marte": [
        _u("photo-1630839437035-dac17da580d0"),
        _u("photo-1451187580459-43490279c0fa"),
    ],
    "saturn": [
        _u("photo-1614314107768-6018061b5b72"),
        _u("photo-1446776877081-d282a0f896e2"),
    ],
    "giove": [
        _u("photo-1630694093867-4b947d812bf0"),
    ],
    "buco nero": [
        _u("photo-1462331940025-496dfbfc7564"),
        _u("photo-1419242902214-272b3f66ee7a"),
    ],
    "galass": [
        _u("photo-1462331940025-496dfbfc7564"),
        _u("photo-1419242902214-272b3f66ee7a"),
    ],
    "cometa": [
        _u("photo-1419242902214-272b3f66ee7a"),
    ],
    "vulcan": [
        _u("photo-1562184552-997c461abbe6"),
    ],
    "ocean": [
        _u("photo-1505142468610-359e7d316be0"),
        _u("photo-1507525428034-b723cf961d3e"),
    ],
    "deserto": [
        _u("photo-1473580044384-7ba9967e16a0"),
        _u("photo-1547235001-d703406d3f17"),
    ],
    "foresta": [
        _u("photo-1448375240586-882707db888b"),
        _u("photo-1441974231531-c6227db76b6e"),
    ],
    "montagn": [
        _u("photo-1464822759023-fed622ff2c3b"),
        _u("photo-1506905925346-21bda4d32df4"),
    ],
    "ghiacci": [
        _u("photo-1517299321609-52687d1bc55a"),
    ],
    "pizza": [
        _u("photo-1513104890138-7c749659a591"),
        _u("photo-1574071318508-1cdbab80d002"),
    ],
    "pasta": [
        _u("photo-1598866594230-a7c12756260f"),
        _u("photo-1551892374-ecf8754cf8b0"),
    ],
    "caffè": [
        _u("photo-1495474472287-4d71bcdd2085"),
        _u("photo-1509042239860-f550ce710b93"),
    ],
    "cioccolat": [
        _u("photo-1511381939415-e44015466834"),
    ],
    "vino": [
        _u("photo-1510812431401-41d2bd2722f3"),
        _u("photo-1553361371-9b22f78e8b1d"),
    ],
    "leonardo": [
        _u("photo-1578926288207-a90a5366759d"),
    ],
    "napoleon": [
        _u("photo-1555848962-6e79363ec58f"),
    ],
    "piramid": [
        _u("photo-1568667256549-094345857637"),
    ],
    "colosseo": [
        _u("photo-1552832230-c0197dd311b5"),
    ],
    "titanic": [
        _u("photo-1569091791842-7cfb64e04797"),
    ],
}

_FALLBACK = CATEGORY_IMAGES["Spazio"]


def image_for_fact(category: str, seed: str, sub_category: Optional[str] = None) -> str:
    """Pick the most relevant image.

    Priority:
      1. Keyword match against the seed text (e.g. title / short_fact) — picks
         an image that actually matches the subject of the fact (penguin, koala, etc).
      2. Sub-category pool (brands / themes).
      3. Category pool.
      4. Global fallback.
    """
    import re
    lowered = str(seed).lower()
    pool: Optional[List[str]] = None

    # 1) Keyword match — use word boundaries to avoid false positives
    #    like "napoleone" matching "leone".
    for kw, urls in KEYWORD_IMAGES.items():
        # Build a regex that requires the keyword to start on a word boundary
        # (keyword may be a stem like "pinguin" so it matches "pinguini" too).
        pattern = r"\b" + re.escape(kw.rstrip())
        if re.search(pattern, lowered):
            pool = urls
            break

    # 2) Sub-category
    if pool is None and sub_category and sub_category in SUBCATEGORY_IMAGES:
        pool = SUBCATEGORY_IMAGES[sub_category]

    # 3) Category
    if pool is None:
        pool = CATEGORY_IMAGES.get(category, _FALLBACK)

    if not pool:
        pool = _FALLBACK

    h = int(hashlib.md5(str(seed).encode("utf-8")).hexdigest()[:8], 16)
    return pool[h % len(pool)]


async def image_for_fact_async(db, category: str, seed: str, sub_category: Optional[str] = None) -> str:
    """Prefer a real Unsplash photo searched by keyword; fall back to the
    curated catalog if Unsplash has no key / errors / is rate-limited."""
    try:
        from unsplash import get_fact_image
        url = await get_fact_image(db, category, str(seed), sub_category)
        if url:
            return url
    except Exception as e:
        import logging
        logging.getLogger("losapevi").warning(f"[image] Unsplash failed, using catalog: {e}")
    return image_for_fact(category, seed, sub_category)


def first_image_for_category(category: str) -> str:
    pool = CATEGORY_IMAGES.get(category, _FALLBACK)
    return pool[0] if pool else _FALLBACK[0]
