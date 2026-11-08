"""Builds the reserve: evergreen, fact-checked cricket posts + cards that go out when Claude is down.

Run:  python3 reserve/build.py        (re-renders everything into reserve/items and reserve/cards)
Only used by hand. The daily job uses reserve/fallback.py.
"""
import json, pathlib, subprocess, sys, tempfile

HERE = pathlib.Path(__file__).parent
ROOT = HERE.parent


def b(s):
    out = []
    for c in s:
        if "A" <= c <= "Z": out.append(chr(0x1D5D4 + ord(c) - 65))
        elif "a" <= c <= "z": out.append(chr(0x1D5EE + ord(c) - 97))
        elif "0" <= c <= "9": out.append(chr(0x1D7EC + ord(c) - 48))
        else: out.append(c)
    return "".join(out)


ORANGE = ("#FF9933", "rgba(255,153,51,.28)")
BLUE = ("#3B82F6", "rgba(59,130,246,.28)")
GREEN = ("#22C55E", "rgba(34,197,94,.26)")
GOLD = ("#F5B301", "rgba(245,179,1,.28)")
PINK = ("#EC4899", "rgba(236,72,153,.26)")
RED = ("#EF4444", "rgba(239,68,68,.26)")
TEAL = ("#14B8A6", "rgba(20,184,166,.26)")
GREY = "#9AA4B2"

# Each item: id, x(hook, line1, line2, tags), fb(hook, bullets, question, tags), card(...)
ITEMS = [
 dict(id="tendulkar-100", col=ORANGE,
  x=("THE CENTURY OF CENTURIES 💯", "Sachin Tendulkar: 51 Test + 49 ODI hundreds = 100 international tons.", "The only batter to reach 100. The 100th came at Mirpur, 16 March 2012. 🇮🇳", "#Cricket #Tendulkar"),
  fb=("100 international shatak! 💯🇮🇳", ["Sachin Tendulkar ke 51 Test + 49 ODI shatak", "100va shatak: Bangladesh ke khilaf, Mirpur, 16 March 2012 (114 run)", "Aaj tak koi aur batter 100 tak nahi pahunch paya"], "Tendulkar ka sabse yaadgaar shatak kaunsa tha? Comment karo 👇", "#Tendulkar"),
  card=dict(pill="RECORD BOOK · SACHIN TENDULKAR", tag="Record alert", headline="SACHIN'S <em>100 TONS</em>",
   rows=[("Tests", "51", "hundreds", False), ("ODIs", "49", "hundreds", True)],
   result="The 100th came vs Bangladesh, Mirpur, 16 Mar 2012",
   stats=[("51", "Test hundreds"), ("49", "ODI hundreds"), ("114", "in his 100th ton")], source="Data: ESPNcricinfo records")),
 dict(id="sachin-200", col=BLUE,
  x=("FIRST MALE BATTER TO 200 IN ODIs 🔥", "Sachin Tendulkar, 200* off 147 balls vs South Africa, Gwalior, 24 Feb 2010.", "India finished on 401/3 and won by 153 runs. 🏏", "#Cricket #Tendulkar"),
  fb=("ODI mein pehla double century! 🔥", ["Sachin Tendulkar – 147 balls mein 200* ✨", "Gwalior, 24 February 2010, South Africa ke khilaf", "India ne banaye 401/3 aur 153 run se jeet li"], "Wo din aapko yaad hai? Comment karo 👇", "#Tendulkar"),
  card=dict(pill="INDIA v SOUTH AFRICA · GWALIOR · 24 Feb 2010", tag="History made", headline="THE FIRST ODI <em>200</em>",
   rows=[("India", "401/3", "50 ov", True), ("South Africa", "248", "all out", False)],
   result="India won by 153 runs",
   stats=[("200*", "off 147 balls"), ("401/3", "India's total"), ("1st", "male double ton in ODIs")], source="Data: ESPNcricinfo")),
 dict(id="rohit-264", col=BLUE,
  x=("𝟮𝟲𝟰! THE HIGHEST ODI SCORE 🚀", "Rohit Sharma, 264 off 173 balls vs Sri Lanka, Eden Gardens, 13 Nov 2014.", "33 fours, 9 sixes. He has three ODI double hundreds. 🔥", "#Cricket #RohitSharma"),
  fb=("264! ODI ka sabse bada score 🚀", ["Rohit Sharma – 173 balls mein 264 run", "33 chauke aur 9 chhakke, Eden Gardens, 13 November 2014", "Rohit ke naam teen ODI double century hain (209, 264, 208*)"], "Rohit ki ye pari kitni baar dekhi aapne? Comment karo 👇", "#RohitSharma"),
  card=dict(pill="INDIA v SRI LANKA · EDEN GARDENS · 13 Nov 2014", tag="Record alert", headline="ROHIT'S <em>264</em>",
   rows=[("India", "404/5", "50 ov", True), ("Rohit Sharma", "264", "173 balls", True)],
   result="Still the highest score in men's ODI history",
   stats=[("264", "off 173 balls"), ("33 + 9", "fours and sixes"), ("3", "ODI double hundreds")], source="Data: ESPNcricinfo")),
 dict(id="kumble-10", col=ORANGE,
  x=("PERFECT 10! 🖐️🔟", "Anil Kumble took all 10 wickets for 74 vs Pakistan, Delhi, 7 Feb 1999.", "Only the second bowler ever to do it in a Test innings. India won by 212 runs. 🇮🇳", "#Cricket #Kumble"),
  fb=("Ek innings, dus wicket! 🖐️🔟", ["Anil Kumble – 10/74 vs Pakistan, Delhi, 7 February 1999", "Test innings mein saare 10 wicket lene wale sirf doosre gendbaaz", "India ne ye Test 212 run se jeeta"], "Kumble ka sabse bada spell yehi tha na? Comment karo 👇", "#Kumble"),
  card=dict(pill="INDIA v PAKISTAN · DELHI · 7 Feb 1999", tag="History made", headline="KUMBLE'S PERFECT <em>10</em>",
   rows=[("Anil Kumble", "10/74", "26.3 ov", True), ("India", "won", "by 212 runs", True)],
   result="Second bowler to take all ten in a Test innings",
   stats=[("10/74", "innings figures"), ("2nd", "after Jim Laker (1956)"), ("212", "runs India won by")], source="Data: ESPNcricinfo")),
 dict(id="laker-19", col=RED,
  x=("𝟭𝟵 WICKETS IN ONE TEST 🤯", "Jim Laker, Old Trafford 1956: 9/37 and 10/53 against Australia.", "Match figures of 19/90 are still the best in Test history. 🏏", "#Cricket #TestCricket"),
  fb=("Ek Test mein 19 wicket! 🤯", ["Jim Laker – Old Trafford, 1956 Ashes", "Pehli pari 9/37, doosri pari 10/53", "19/90 aaj bhi Test cricket ke best match figures hain"], "Kya aaj ke daur mein ye record toot sakta hai? Comment karo 👇", "#TestCricket"),
  card=dict(pill="ENGLAND v AUSTRALIA · OLD TRAFFORD · 1956", tag="Record alert", headline="LAKER TAKES <em>19</em>",
   rows=[("1st innings", "9/37", "", False), ("2nd innings", "10/53", "", True)],
   result="Best match figures in Test history: 19/90",
   stats=[("19/90", "match figures"), ("9/37", "first innings"), ("10/53", "second innings")], source="Data: ESPNcricinfo")),
 dict(id="lara-400", col=PINK,
  x=("𝟰𝟬𝟬 NOT OUT 👑", "Brian Lara: 400* vs England, St John's, April 2004 — the highest Test score ever.", "He also owned the old record with 375 in 1994. 🌴", "#Cricket #BrianLara"),
  fb=("400* – Test cricket ka sabse bada score! 👑", ["Brian Lara – England ke khilaf 400 not out, April 2004", "582 balls ki marathon pari, St John's (Antigua)", "1994 mein bhi unhone 375 banaye the"], "Kya koi ye record kabhi tod payega? Comment karo 👇", "#BrianLara"),
  card=dict(pill="WEST INDIES v ENGLAND · ST JOHN'S · Apr 2004", tag="Record alert", headline="LARA'S <em>400*</em>",
   rows=[("Brian Lara", "400*", "582 balls", True), ("Earlier record", "375", "in 1994", False)],
   result="Highest individual score in Test history",
   stats=[("400*", "not out"), ("582", "balls faced"), ("375", "his 1994 record")], source="Data: ESPNcricinfo")),
 dict(id="murali-800", col=GOLD,
  x=("𝟴𝟬𝟬 TEST WICKETS 🌀", "Muttiah Muralitharan: 800 in 133 Tests, the most in history.", "Shane Warne is next with 708, then James Anderson with 704. 🏏", "#Cricket #Muralitharan"),
  fb=("800 Test wicket! 🌀", ["Muttiah Muralitharan – 133 Tests mein 800 wicket", "Shane Warne ke 708, James Anderson ke 704", "Galle mein unka aakhri wicket bhi 800va tha"], "Aapka favourite spinner kaun hai? Comment karo 👇", "#Muralitharan"),
  card=dict(pill="TEST CRICKET · MOST WICKETS", tag="Record alert", headline="THE <em>800</em> CLUB OF ONE",
   rows=[("Muralitharan", "800", "133 Tests", True), ("Shane Warne", "708", "145 Tests", False)],
   result="Muralitharan holds the all-time Test wicket record",
   stats=[("800", "Muralitharan"), ("708", "Shane Warne"), ("704", "James Anderson")], source="Data: ESPNcricinfo")),
 dict(id="wc-1983", col=ORANGE,
  x=("𝟭𝟵𝟴𝟯! KAPIL'S DEVILS 🏆", "India beat the mighty West Indies by 43 runs at Lord's on 25 June 1983.", "India made just 183, then bowled WI out for 140. A nation fell in love with cricket. 🇮🇳", "#Cricket #1983WorldCup"),
  fb=("1983: India ne duniya jeet li! 🏆🇮🇳", ["Lord's, 25 June 1983 – India ne West Indies ko 43 run se haraya", "India 183 par out, phir West Indies ko 140 par roka", "Kapil Dev ki captaincy mein pehla World Cup"], "Is jeet ki kaunsi yaad sabse khaas hai? Comment karo 👇", "#1983WorldCup"),
  card=dict(pill="WORLD CUP FINAL · LORD'S · 25 Jun 1983", tag="History made", headline="INDIA WIN <em>1983</em>",
   rows=[("India", "183", "54.4 ov", True), ("West Indies", "140", "52 ov", False)],
   result="India won by 43 runs under Kapil Dev",
   stats=[("43", "runs margin"), ("183", "India's total"), ("140", "West Indies all out")], source="Data: ESPNcricinfo")),
 dict(id="kapil-175", col=GREEN,
  x=("𝟭𝟳𝟱* FROM 𝟭𝟳/𝟱 🔥", "Kapil Dev, Tunbridge Wells, 18 June 1983: 175* off 138 balls vs Zimbabwe.", "India were 17/5 when he walked in. They finished on 266/8 and won. 🇮🇳", "#Cricket #KapilDev"),
  fb=("17/5 se 266/8 tak! 🔥", ["Kapil Dev – Zimbabwe ke khilaf 138 balls mein 175*", "Tunbridge Wells, 18 June 1983", "India 17/5 par tha, phir 31 run se jeet mili"], "Kya aaj ke daur mein aisi pari banti hai? Comment karo 👇", "#KapilDev"),
  card=dict(pill="WORLD CUP · TUNBRIDGE WELLS · 18 Jun 1983", tag="Epic knock", headline="KAPIL'S <em>175*</em>",
   rows=[("India", "266/8", "60 ov", True), ("Kapil Dev", "175*", "138 balls", True)],
   result="From 17/5 to a 31-run win over Zimbabwe",
   stats=[("175*", "off 138 balls"), ("17/5", "when he walked in"), ("31", "runs India won by")], source="Data: ESPNcricinfo")),
 dict(id="t20wc-2007", col=GREEN,
  x=("𝟮𝟬𝟬𝟳 T20 WORLD CUP CHAMPIONS 🏆", "India beat Pakistan by 5 runs in the first T20 World Cup final, Johannesburg.", "India 157/5, Pakistan 152 all out. Gambhir made 75 and MS Dhoni led the way. 🇮🇳", "#Cricket #T20WorldCup"),
  fb=("Pehla T20 World Cup India ke naam! 🏆", ["Johannesburg, 24 September 2007 – final mein Pakistan ko 5 run se haraya", "India 157/5, Pakistan 152 par all out", "Gautam Gambhir ke 75 aur MS Dhoni ki captaincy"], "Aakhri over ka wo pal yaad hai? Comment karo 👇", "#T20WorldCup"),
  card=dict(pill="T20 WORLD CUP FINAL · JOHANNESBURG · 24 Sep 2007", tag="History made", headline="THE FIRST T20 <em>CROWN</em>",
   rows=[("India", "157/5", "20 ov", True), ("Pakistan", "152", "19.4 ov", False)],
   result="India won by 5 runs",
   stats=[("5", "runs margin"), ("75", "Gautam Gambhir"), ("1st", "T20 World Cup")], source="Data: ESPNcricinfo")),
 dict(id="wc-2011", col=BLUE,
  x=("𝟮𝟬𝟭𝟭! 28 YEARS LATER 🏆", "India beat Sri Lanka by 6 wickets at the Wankhede on 2 April 2011.", "Dhoni 91* and Gambhir 97 chased down 275. India lifted the World Cup at home. 🇮🇳", "#Cricket #2011WorldCup"),
  fb=("28 saal baad World Cup India ke paas! 🏆", ["Wankhede, 2 April 2011 – Sri Lanka ko 6 wicket se haraya", "MS Dhoni ke 91* aur Gautam Gambhir ke 97", "Ghar mein World Cup jeetne wali pehli host team"], "Dhoni ka wo winning six aap kabhi bhool sakte hain? Comment karo 👇", "#2011WorldCup"),
  card=dict(pill="WORLD CUP FINAL · WANKHEDE · 2 Apr 2011", tag="History made", headline="INDIA <em>CHAMPIONS</em>",
   rows=[("Sri Lanka", "274/6", "50 ov", False), ("India", "277/4", "48.2 ov", True)],
   result="India won by 6 wickets",
   stats=[("91*", "MS Dhoni"), ("97", "Gautam Gambhir"), ("28", "years since 1983")], source="Data: ESPNcricinfo")),
 dict(id="t20wc-2024", col=BLUE,
  x=("𝟮𝟬𝟮𝟰 T20 WORLD CUP WINNERS 🏆", "India beat South Africa by 7 runs in Barbados on 29 June 2024.", "Kohli 76, India 176/7, South Africa 169/8. An 11-year wait for an ICC trophy ended. 🇮🇳", "#Cricket #T20WorldCup"),
  fb=("T20 World Cup 2024 India ke naam! 🏆🇮🇳", ["Barbados, 29 June 2024 – South Africa ko 7 run se haraya", "India 176/7, South Africa 169/8", "Virat Kohli ke 76, 11 saal baad ICC trophy"], "Is final ka sabse bada hero kaun tha? Comment karo 👇", "#T20WorldCup"),
  card=dict(pill="T20 WORLD CUP FINAL · BARBADOS · 29 Jun 2024", tag="History made", headline="INDIA WIN THE <em>T20 WC</em>",
   rows=[("India", "176/7", "20 ov", True), ("South Africa", "169/8", "20 ov", False)],
   result="India won by 7 runs",
   stats=[("76", "Virat Kohli"), ("7", "runs margin"), ("11", "year ICC trophy wait ended")], source="Data: ICC / ESPNcricinfo")),
 dict(id="yuvraj-six-sixes", col=PINK,
  x=("𝗦𝗜𝗫 𝗦𝗜𝗫𝗘𝗦, 𝗢𝗡𝗘 𝗢𝗩𝗘𝗥 💥", "Yuvraj Singh hit six sixes off Stuart Broad at the 2007 T20 World Cup, Durban.", "His 50 came off just 12 balls. India beat England by 18 runs. 🔥", "#Cricket #Yuvraj"),
  fb=("Ek over, chhe chhakke! 💥", ["Yuvraj Singh – Stuart Broad ke ek over mein 6 sixes", "T20 World Cup 2007, Durban, 19 September", "Sirf 12 balls mein fifty, India 18 run se jeeta"], "Ye over aapne kitni baar dekha hai? Comment karo 👇", "#Yuvraj"),
  card=dict(pill="T20 WORLD CUP · DURBAN · 19 Sep 2007", tag="Power show", headline="YUVRAJ'S SIX <em>SIXES</em>",
   rows=[("Yuvraj Singh", "58", "16 balls", True), ("Stuart Broad", "36", "one over", False)],
   result="India beat England by 18 runs",
   stats=[("6 x 6", "sixes in an over"), ("12", "balls to fifty"), ("58", "off 16 balls")], source="Data: ESPNcricinfo")),
 dict(id="first-test-1877", col=GOLD,
  x=("THE VERY FIRST TEST 🏏", "Melbourne, March 1877: Australia beat England by 45 runs.", "Charles Bannerman made 165, retired hurt. Test cricket was born. 🌏", "#Cricket #TestCricket"),
  fb=("Duniya ka pehla Test match! 🏏", ["Melbourne, March 1877 – Australia vs England", "Australia ne 45 run se jeet li", "Charles Bannerman ke 165 (retired hurt)"], "Test cricket aapko kyun pasand hai? Comment karo 👇", "#TestCricket"),
  card=dict(pill="AUSTRALIA v ENGLAND · MELBOURNE · Mar 1877", tag="History made", headline="TEST CRICKET <em>IS BORN</em>",
   rows=[("Australia", "won", "by 45 runs", True), ("Charles Bannerman", "165", "retired hurt", True)],
   result="The first Test match ever played",
   stats=[("1877", "the year"), ("45", "runs margin"), ("165", "Bannerman")], source="Data: ESPNcricinfo")),
 dict(id="ashes-1882", col=RED,
  x=("HOW THE ASHES BEGAN ⚰️🏏", "The Oval, 1882: Australia beat England by 7 runs.", "A newspaper printed a mock obituary of English cricket, saying 'the ashes' would go to Australia. 🔥", "#Cricket #Ashes"),
  fb=("Ashes ki kahani yahin se shuru hui! ⚰️🏏", ["The Oval, 1882 – Australia ne England ko 7 run se haraya", "Spofforth ne match mein 14 wicket liye", "Akhbaar ne likha: English cricket ki 'ashes' Australia le jayega"], "Ashes ka sabse yaadgaar Test kaunsa hai? Comment karo 👇", "#Ashes"),
  card=dict(pill="ENGLAND v AUSTRALIA · THE OVAL · 1882", tag="Origin story", headline="THE ASHES <em>BEGIN</em>",
   rows=[("Australia", "won", "by 7 runs", True), ("Fred Spofforth", "14", "wickets", True)],
   result="The result that gave the Ashes their name",
   stats=[("7", "runs margin"), ("14", "wickets, Spofforth"), ("1882", "the year")], source="Data: ESPNcricinfo")),
 dict(id="harmanpreet-171", col=PINK,
  x=("𝟭𝟳𝟭* — HARMANPREET HITS BACK 🔥", "Harmanpreet Kaur, 171* off 115 vs Australia, 2017 World Cup semi-final, Derby.", "20 fours, 7 sixes. India won by 36 runs and reached the final. 🇮🇳", "#Cricket #WomensCricket"),
  fb=("Harmanpreet ki 171* – India ke liye final ka ticket! 🔥", ["Women's World Cup 2017 semi-final, Derby, 20 July", "115 balls mein 171* (20 chauke, 7 chhakke)", "India ne Australia ko 36 run se haraya"], "Is pari ko aap kya rating denge? Comment karo 👇", "#WomensCricket"),
  card=dict(pill="WOMEN'S WORLD CUP SEMI-FINAL · DERBY · 20 Jul 2017", tag="Epic knock", headline="HARMAN'S <em>171*</em>",
   rows=[("India", "281/4", "42 ov", True), ("Australia", "245", "40.1 ov", False)],
   result="India won by 36 runs and reached the final",
   stats=[("171*", "off 115 balls"), ("20 + 7", "fours and sixes"), ("36", "runs India won by")], source="Data: ESPNcricinfo")),
 dict(id="womens-wc-2025", col=PINK,
  x=("INDIA WOMEN, WORLD CHAMPIONS 🏆🇮🇳", "India beat South Africa by 52 runs in Navi Mumbai on 2 Nov 2025.", "Their first Women's World Cup title, after finals in 2005 and 2017. 💙", "#Cricket #WomensWorldCup"),
  fb=("India Women ne World Cup jeet liya! 🏆🇮🇳", ["Navi Mumbai, 2 November 2025 – South Africa ko 52 run se haraya", "India ka pehla Women's World Cup khitaab", "2005 aur 2017 ke final ki kasak poori hui"], "Is jeet par aapka reaction kya tha? Comment karo 👇", "#WomensWorldCup"),
  card=dict(pill="WOMEN'S WORLD CUP FINAL · NAVI MUMBAI · 2 Nov 2025", tag="History made", headline="INDIA WOMEN, <em>CHAMPIONS</em>",
   rows=[("India", "won", "by 52 runs", True), ("South Africa", "lost", "final", False)],
   result="India's first Women's World Cup title",
   stats=[("52", "runs margin"), ("1st", "World Cup title"), ("3rd", "final (2005, 2017, 2025)")], source="Data: ICC / ESPNcricinfo")),
 dict(id="mithali-runs", col=PINK,
  x=("𝟳,𝟴𝟬𝟬+ ODI RUNS 👑", "Mithali Raj finished with 7,800+ ODI runs, the most in women's ODI history.", "A 23-year international career, from 1999 to 2022. Legend. 🇮🇳", "#Cricket #MithaliRaj"),
  fb=("Mithali Raj – women's ODI ki run-machine! 👑", ["7,800+ ODI run, women's cricket mein sabse zyada", "Career: 1999 se 2022 tak, 23 saal", "Kitni hi ladkiyon ko cricket khelne ka hausla diya"], "Mithali Raj ke liye ek line likho 👇", "#MithaliRaj"),
  card=dict(pill="WOMEN'S CRICKET · MITHALI RAJ", tag="Legend", headline="MITHALI, THE <em>RUN QUEEN</em>",
   rows=[("ODI runs", "7,800+", "most ever", True), ("Career", "1999–2022", "23 years", False)],
   result="The all-time leading run-scorer in women's ODIs",
   stats=[("7,800+", "ODI runs"), ("1999", "debut year"), ("2022", "retired")], source="Data: ESPNcricinfo")),
 dict(id="dhoni-three-trophies", col=BLUE,
  x=("THREE ICC TROPHIES, ONE CAPTAIN 🧢", "MS Dhoni led India to the 2007 T20 World Cup, 2011 World Cup and 2013 Champions Trophy.", "The only captain to win all three white-ball ICC trophies. 🇮🇳", "#Cricket #Dhoni"),
  fb=("Teen ICC trophy, ek captain! 🧢🏆", ["2007 – T20 World Cup", "2011 – ODI World Cup", "2013 – Champions Trophy"], "MS Dhoni ka best finish kaunsa tha? Comment karo 👇", "#Dhoni"),
  card=dict(pill="MS DHONI · CAPTAIN COOL", tag="Legend", headline="DHONI'S TRIPLE <em>CROWN</em>",
   rows=[("T20 World Cup", "2007", "", True), ("World Cup", "2011", "", True)],
   result="Champions Trophy 2013 completes the set",
   stats=[("2007", "T20 World Cup"), ("2011", "ODI World Cup"), ("2013", "Champions Trophy")], source="Data: ICC")),
 dict(id="kohli-50", col=BLUE,
  x=("𝟱𝟬 ODI HUNDREDS 👑", "Virat Kohli's 117 vs New Zealand in the 2023 World Cup semi-final, Wankhede.", "It passed Tendulkar's 49. Kohli ended with a record 765 runs in that tournament. 🇮🇳", "#Cricket #ViratKohli"),
  fb=("Kohli ka 50va ODI shatak! 👑", ["Wankhede, 15 November 2023 – New Zealand ke khilaf 117", "Sachin Tendulkar ke 49 shatak ka record tod diya", "World Cup 2023 mein record 765 run"], "Kohli ki sabse badi pari kaunsi lagti hai? Comment karo 👇", "#ViratKohli"),
  card=dict(pill="WORLD CUP SEMI-FINAL · WANKHEDE · 15 Nov 2023", tag="Record alert", headline="KOHLI'S <em>50TH</em> TON",
   rows=[("Virat Kohli", "117", "113 balls", True), ("Sachin Tendulkar", "49", "ODI tons", False)],
   result="India beat New Zealand by 70 runs",
   stats=[("50", "ODI hundreds"), ("117", "in the semi-final"), ("765", "runs, record World Cup")], source="Data: ESPNcricinfo")),
 dict(id="gavaskar-10000", col=GOLD,
  x=("FIRST TO 𝟭𝟬,𝟬𝟬𝟬 TEST RUNS 🧱", "Sunil Gavaskar reached 10,000 Test runs in Ahmedabad, March 1987.", "He retired with 10,122 runs and 34 hundreds from 125 Tests. 🇮🇳", "#Cricket #Gavaskar"),
  fb=("Test cricket mein 10,000 run – sabse pehle! 🧱", ["Sunil Gavaskar – Ahmedabad, March 1987", "Career: 125 Tests, 10,122 run, 34 shatak", "Little Master ne kai pidhiyon ko inspire kiya"], "Gavaskar ke baare mein aapki favourite yaad? Comment karo 👇", "#Gavaskar"),
  card=dict(pill="TEST CRICKET · SUNIL GAVASKAR", tag="History made", headline="THE FIRST <em>10,000</em>",
   rows=[("Tests", "125", "matches", False), ("Runs", "10,122", "career", True)],
   result="First man to score 10,000 Test runs",
   stats=[("10,122", "Test runs"), ("34", "Test hundreds"), ("125", "Tests")], source="Data: ESPNcricinfo")),
 dict(id="kolkata-2001", col=ORANGE,
  x=("KOLKATA 𝟮𝟬𝟬𝟭: THE GREAT COMEBACK 🔥", "Laxman 281 and Dravid 180 shared a 376-run stand after India followed on.", "India beat Australia by 171 runs, ending their run of 16 straight Test wins. 🇮🇳", "#Cricket #VVSLaxman"),
  fb=("Kolkata 2001 – Test cricket ka sabse bada comeback! 🔥", ["Follow-on ke baad Laxman ke 281 aur Dravid ke 180", "Dono ke beech 376 run ki partnership", "India ne Australia ko 171 run se haraya, unki 16 jeet ki lakeer tod di"], "Is Test ki sabse yaadgaar jhalak kaunsi hai? Comment karo 👇", "#VVSLaxman"),
  card=dict(pill="INDIA v AUSTRALIA · EDEN GARDENS · Mar 2001", tag="Epic comeback", headline="LAXMAN AND DRAVID, <em>376</em>",
   rows=[("VVS Laxman", "281", "", True), ("Rahul Dravid", "180", "", True)],
   result="India won by 171 runs after following on",
   stats=[("376", "partnership"), ("171", "runs India won by"), ("16", "Australian wins ended")], source="Data: ESPNcricinfo")),
 dict(id="natwest-2002", col=BLUE,
  x=("𝗟𝗢𝗥𝗗'𝗦, 𝟮𝟬𝟬𝟮 🧥", "India chased down 326 to win the NatWest final by 2 wickets with 3 balls left.", "Kaif 87*, Yuvraj 69, and Ganguly's famous shirt wave. 🇮🇳", "#Cricket #NatWestFinal"),
  fb=("Lord's par Ganguly ki shirt! 🧥🔥", ["NatWest Series final, 13 July 2002 – England ne 325/5 banaye", "India ne 326 ka target 3 gend bacha kar chase kiya", "Mohammad Kaif 87* aur Yuvraj Singh 69"], "Is jeet ka sabse yaadgaar pal kaunsa tha? Comment karo 👇", "#NatWestFinal"),
  card=dict(pill="NATWEST SERIES FINAL · LORD'S · 13 Jul 2002", tag="Epic chase", headline="THE LORD'S <em>CHASE</em>",
   rows=[("England", "325/5", "50 ov", False), ("India", "326/8", "49.3 ov", True)],
   result="India won by 2 wickets",
   stats=[("326", "target chased"), ("87*", "Mohammad Kaif"), ("69", "Yuvraj Singh")], source="Data: ESPNcricinfo")),
 dict(id="sehwag-319", col=GREEN,
  x=("𝗦𝗘𝗛𝗪𝗔𝗚 𝟯𝟭𝟵 💥", "Virender Sehwag hit 319 vs South Africa in Chennai, 2008.", "His triple century came in just 278 balls, the fastest in Test history. 🇮🇳", "#Cricket #Sehwag"),
  fb=("Sehwag ka 319! 💥", ["Chennai, 2008 – South Africa ke khilaf 319 run", "Triple century sirf 278 balls mein, Test ka sabse tez", "Sehwag ne 2004 mein Multan mein bhi 309 banaye the"], "Sehwag ki batting ka andaaz aap kitna miss karte hain? Comment karo 👇", "#Sehwag"),
  card=dict(pill="INDIA v SOUTH AFRICA · CHENNAI · Mar 2008", tag="Power show", headline="SEHWAG'S <em>319</em>",
   rows=[("Virender Sehwag", "319", "", True), ("Fastest triple", "278", "balls", True)],
   result="The fastest triple century in Test history",
   stats=[("319", "his score"), ("278", "balls to 300"), ("2", "Test triples")], source="Data: ESPNcricinfo")),
 dict(id="bradman-9994", col=GREEN,
  x=("𝟵𝟵.𝟵𝟰 🐐", "Don Bradman needed just 4 runs in his last Test innings to average 100.", "He was out for 0 at The Oval, 1948 — and finished on 99.94. 🏏", "#Cricket #Bradman"),
  fb=("99.94 – cricket ka sabse mashhoor average! 🐐", ["Don Bradman – 52 Tests, 6,996 run, 29 shatak", "Aakhri pari mein sirf 4 run chahiye the 100 average ke liye", "The Oval, 1948 – out for 0"], "Aapke hisaab se Bradman ke baad sabse best batter kaun? Comment karo 👇", "#Bradman"),
  card=dict(pill="TEST CRICKET · DON BRADMAN", tag="Legend", headline="BRADMAN'S <em>99.94</em>",
   rows=[("Test average", "99.94", "", True), ("Needed for 100", "4", "runs, last inning", False)],
   result="Out for 0 at The Oval, 1948",
   stats=[("99.94", "Test average"), ("6,996", "Test runs"), ("29", "Test hundreds")], source="Data: ESPNcricinfo")),
 dict(id="warne-gatting", col=RED,
  x=("THE BALL OF THE CENTURY 🌀", "Shane Warne's first Ashes delivery in England: it pitched outside leg and bowled Mike Gatting.", "Old Trafford, 4 June 1993. Gatting just stared at it. 😳", "#Cricket #ShaneWarne"),
  fb=("Warne ki 'Ball of the Century'! 🌀", ["Old Trafford, 4 June 1993 – Ashes", "Leg stump ke bahar pitch hui, off stump ud gaya", "Mike Gatting ko samajh hi nahi aaya kya hua"], "Isse behtar ball aapne dekhi hai? Comment karo 👇", "#ShaneWarne"),
  card=dict(pill="THE ASHES · OLD TRAFFORD · 4 Jun 1993", tag="Magic ball", headline="WARNE'S <em>MAGIC BALL</em>",
   rows=[("Shane Warne", "1st", "Ashes ball in England", True), ("Mike Gatting", "b", "Warne", False)],
   result="Pitched outside leg stump, hit off stump",
   stats=[("1993", "the year"), ("708", "Warne's Test wickets"), ("145", "Tests played")], source="Data: ESPNcricinfo")),
 dict(id="tendulkar-debut", col=ORANGE,
  x=("𝗔𝗚𝗘𝗗 𝟭𝟲, 𝗧𝗘𝗦𝗧 𝗗𝗘𝗕𝗨𝗧 🇮🇳", "Sachin Tendulkar debuted in Karachi on 15 Nov 1989, against Pakistan.", "24 years later he retired with 200 Tests, 15,921 Test runs and 18,426 ODI runs. 🏏", "#Cricket #Tendulkar"),
  fb=("16 saal ki umar mein Test debut! 🇮🇳", ["Sachin Tendulkar – Karachi, 15 November 1989", "24 saal ka international career", "200 Test, 15,921 Test run aur 18,426 ODI run"], "Sachin ka aapko pehla yaad kya hai? Comment karo 👇", "#Tendulkar"),
  card=dict(pill="SACHIN TENDULKAR · THE CAREER", tag="Legend", headline="FROM 16 TO <em>200</em> TESTS",
   rows=[("Test runs", "15,921", "200 Tests", True), ("ODI runs", "18,426", "463 ODIs", True)],
   result="Debut: Karachi, 15 November 1989",
   stats=[("16", "years old at debut"), ("200", "Tests"), ("34,357", "international runs")], source="Data: ESPNcricinfo")),
 dict(id="wheelchair-spirit-1", col=TEAL,
  x=("NO LIMITS, JUST CRICKET ♿🏏", "Wheelchair cricketers train, sweat and compete just like any other cricketer.", "Respect to everyone who turns a limit into a game plan. 💪", "#Cricket #WheelchairCricket"),
  fb=("Jazba ho to cricket sab ke liye hai! ♿🏏", ["Wheelchair cricketers bhi utni hi mehnat karte hain", "Same khel, same junoon, same jeet ki bhookh", "Har khiladi ko salaam jo limit ko game plan bana deta hai"], "Wheelchair cricket ke khiladiyon ke liye ek line likho 👇", "#WheelchairCricket"),
  card=dict(pill="SPIRIT OF CRICKET", tag="Respect", headline="NO LIMITS, <em>JUST CRICKET</em>",
   rows=[("Training", "Daily", "like every cricketer", False), ("Spirit", "Unstoppable", "", True)],
   result="Wheelchair cricket is cricket, full stop",
   stats=[("Skill", "same game, same shots"), ("Fitness", "hard work, every day"), ("Heart", "never in doubt")], source="Cricket Ki Baat")),
 dict(id="wheelchair-spirit-2", col=TEAL,
  x=("CRICKET IS PLAYED WITH HEART FIRST ❤️", "Wheelchair cricket reminds us that the game is bigger than any limit.", "Next time you see a wheelchair cricket match, stop and watch. You'll be inspired. ♿🏏", "#Cricket #WheelchairCricket"),
  fb=("Cricket dil se khela jata hai ❤️♿", ["Wheelchair cricket sabko yaad dilata hai ki khel limit se bada hota hai", "Mauka mile to ek match zaroor dekhna", "Inka junoon aapko bhi inspire karega"], "Kya aapne kabhi wheelchair cricket dekha hai? Comment karo 👇", "#WheelchairCricket"),
  card=dict(pill="SPIRIT OF CRICKET", tag="Inspiration", headline="CRICKET <em>FROM THE HEART</em>",
   rows=[("The game", "Bigger", "than any limit", True), ("The players", "Fearless", "", False)],
   result="Watch a wheelchair cricket match and feel it",
   stats=[("Heart", "plays first"), ("Passion", "never stops"), ("Respect", "for every player")], source="Cricket Ki Baat")),
]

FIRST_COMMENTS = [
    "Roz ki cricket baat ke liye Cricket Ki Baat ko Follow karo 🔔🏏",
    "Duniya bhar ki cricket updates ke liye Cricket Ki Baat ko Follow karo 🔔🏏",
    "Cricket ki har baat ke liye Cricket Ki Baat ko Follow karo 🔔🏏",
]
IG_COMMENTS = [
    "Roz ki cricket baat ke liye @realcricketkibaat ko follow karo 🏏🔥",
    "Aisi aur cricket kahaniyon ke liye @realcricketkibaat ko follow karo 🔔🏏",
    "Cricket ki har baat ke liye @realcricketkibaat ko follow karo 🏏❤️",
]


def weighted(s):
    return sum(2 if ord(c) > 0x10FF else 1 for c in s)


def build(render=True):
    items_dir, cards_dir = HERE / "items", HERE / "cards"
    items_dir.mkdir(exist_ok=True); cards_dir.mkdir(exist_ok=True)
    problems = []
    for i, it in enumerate(ITEMS):
        hook, l1, l2, tags = it["x"]
        tweet = f"{b(hook)}\n\n{l1}\n{l2}\n\n{tags}"
        if len(tweet) > 250 or weighted(tweet) > 275:
            problems.append((it["id"], len(tweet), weighted(tweet)))
        fh, bullets, q, ftags = it["fb"]
        caption = f"{b(fh)}\n\n" + "\n".join("👉 " + x for x in bullets) + f"\n\n{q}\n\n#CricketKiBaat #Cricket {ftags}"
        a, g = it["col"]
        c = it["card"]
        card = {"pill": c["pill"], "tag": c["tag"], "headline": c["headline"], "accent": a, "glow": g,
                "teams": [{"name": n, "score": s, "overs": o, "color": (a if w else GREY), **({"win": True} if w else {})} for n, s, o, w in c["rows"]],
                "result": c["result"], "stats": [{"big": x, "small": y} for x, y in c["stats"]], "source": c["source"]}
        base = cards_dir / it["id"]
        if render:
            with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
                json.dump(card, f, ensure_ascii=False); tmp = f.name
            subprocess.run([sys.executable, str(ROOT / "cards" / "render.py"), tmp, str(base)], check=True, stdout=subprocess.DEVNULL)
        data = {"id": it["id"], "text": tweet,
                "facebook": {"caption": caption, "first_comment": FIRST_COMMENTS[i % 3]},
                "instagram": {"first_comment": IG_COMMENTS[i % 3]}}
        (items_dir / f"{it['id']}.json").write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    print(len(ITEMS), "items;", "length problems:", problems)


if __name__ == "__main__":
    build(render="--no-render" not in sys.argv)
