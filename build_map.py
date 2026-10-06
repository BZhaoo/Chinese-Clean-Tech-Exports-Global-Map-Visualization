"""Rebuild the China clean-tech export map from a fresh CSV.
Usage: python build_map.py <clean_tech_exports.csv> [out.html] [ne_110m_admin_0_countries.geojson]
Borders: download the Natural Earth 110m countries GeoJSON (public domain) and pass it as the 3rd argument.
Re-run whenever you download a new release; the page itself is fully offline."""
import sys, json, datetime
import pandas as pd

COORDS = """United States:38,-97;Germany:51,10;Netherlands:52,5;India:22,79;South Korea:36.5,128;Japan:36,138;Brazil:-10,-52;Belgium:50.6,4.6;Viet Nam:15,107;Australia:-25,134;United Kingdom:53,-1.5;Spain:40,-4;Thailand:15,101;Hong Kong (SAR of China):22.3,114.2;United Arab Emirates:24,54;Mexico:23,-102;Saudi Arabia:24,45;Italy:42.5,12.5;Malaysia:3.5,102;Poland:52,19;France:46.5,2.5;Indonesia:-2,114;Pakistan:30,70;Russia:60,70;Israel:31.5,35;Türkiye:39,35;The Philippines:12.5,122;Slovenia:46,14.8;South Africa:-29,24;Chile:-33,-71;Canada:56,-100;Uzbekistan:41,64;Taiwan (China):23.7,121;Greece:39,22;Hungary:47,19.5;Iraq:33,44;Singapore:1.35,103.8;Colombia:4,-73;Nigeria:9,8;Portugal:39.5,-8;Sweden:62,15;Slovakia:48.7,19.5;Kazakhstan:48,67;Norway:61,9;Kyrgyzstan:41.5,74.5;Czechia:49.8,15.5;Cambodia:12.5,105;Ukraine:49,32;Argentina:-35,-65;Egypt:27,30;Jordan:31,36.5;Romania:46,25;Finland:63,26;Bangladesh:24,90;Bulgaria:42.7,25.5;Denmark:56,10;Oman:21,57;New Zealand:-41,174;Austria:47.5,14;Morocco:32,-6;Myanmar:21,96;Lao PDR:18.5,103.5;Panama:8.5,-80;Belarus:53.5,28;Qatar:25.3,51.2;Azerbaijan:40.3,47.7;Uruguay:-33,-56;Kenya:0,38;Lebanon:33.9,35.9;Croatia:45.1,15.5;Congo (DRC):-3,23;Sri Lanka:7.8,80.7;Peru:-10,-75;Ghana:7.9,-1;Switzerland:46.8,8.2;Dominican Republic:19,-70.5;Ecuador:-1.5,-78;Algeria:28,3;Ethiopia:9,40;Kuwait:29.3,47.6;Tanzania (the United Republic of):-6,35;Venezuela:7,-66;Nepal:28,84;Lithuania:55.3,23.9;Serbia:44,21;Yemen:15.5,48;Tajikistan:38.8,71;Costa Rica:10,-84;Senegal:14.5,-14.5;Libya:27,17;Georgia:42,43.5;Iran:32,53;Ireland:53.3,-8;Paraguay:-23,-58;Cote d'Ivoire:7.5,-5.5;Djibouti:11.8,42.6;Armenia:40.2,45;Albania:41,20;Tunisia:34,9;Cuba:21.5,-79;Mozambique:-18,35;Mongolia:47000,0;Estonia:58.7,25.5;Guatemala:15.5,-90.3;Zambia:-14,28;Cameroon:6,12;Bahrain:26,50.5;Zimbabwe:-19,30;Togo:8.6,1;Mali:17,-4;Guinea:10.5,-11;Angola:-12,17.5;Honduras:14.8,-86.5;Macao (SAR of China):22.2,113.5;El Salvador:13.7,-88.9;Latvia:56.9,24.9;Benin:9.5,2.3;Sudan:15,30;Afghanistan:33.9,66;Cyprus:35,33;Uganda:1.3,32.3;Mauritius:-20.3,57.6;Jamaica:18.1,-77.3;Bolivia:-17,-64.5;Namibia:-22,17;Madagascar:-19,46.7;Turkmenistan:39,59;Puerto Rico:18.2,-66.5;Burkina Faso:12.3,-1.6;Bosnia Herzegovina:44,17.8;Haiti:19,-72.4;Mauritania:20,-10.5;Brunei Darussalam:4.5,114.7;Maldives:3.2,73.2;Moldova:47,28.5;Syria:35,38.5;Guyana:5,-59;Sierra Leone:8.5,-11.8;Chad:15,19;North Macedonia:41.6,21.7"""
COORDS = COORDS.replace("47000,0", "46.9,103.8")
coords = {k: tuple(map(float, v.split(","))) for k, v in (p.rsplit(":", 1) for p in COORDS.split(";"))}

SUB = {
"Southeast Asia":"Viet Nam|Thailand|Malaysia|Indonesia|The Philippines|Singapore|Cambodia|Myanmar|Lao PDR|Brunei Darussalam",
"South Asia":"India|Pakistan|Bangladesh|Sri Lanka|Nepal|Afghanistan|Maldives",
"East Asia":"South Korea|Japan|Hong Kong (SAR of China)|Taiwan (China)|Macao (SAR of China)|Mongolia",
"Central Asia":"Uzbekistan|Kazakhstan|Kyrgyzstan|Tajikistan|Turkmenistan",
"Middle East":"United Arab Emirates|Saudi Arabia|Israel|Türkiye|Iraq|Jordan|Oman|Qatar|Azerbaijan|Armenia|Georgia|Lebanon|Kuwait|Yemen|Iran|Bahrain|Syria",
"Western Europe":"Germany|Netherlands|Belgium|France|Austria|Switzerland",
"Northern Europe":"United Kingdom|Ireland|Sweden|Norway|Finland|Denmark|Lithuania|Latvia|Estonia",
"Southern Europe":"Spain|Italy|Portugal|Greece|Slovenia|Croatia|Serbia|Albania|North Macedonia|Bosnia Herzegovina|Cyprus",
"Eastern Europe":"Poland|Hungary|Slovakia|Czechia|Romania|Bulgaria|Ukraine|Belarus|Moldova|Russia",
"Northern Africa":"Egypt|Morocco|Algeria|Libya|Tunisia|Sudan",
"Western Africa":"Nigeria|Ghana|Senegal|Cote d'Ivoire|Togo|Mali|Guinea|Benin|Burkina Faso|Mauritania|Sierra Leone",
"Central Africa":"Congo (DRC)|Cameroon|Angola|Chad",
"Eastern Africa":"Kenya|Ethiopia|Tanzania (the United Republic of)|Djibouti|Mozambique|Zambia|Zimbabwe|Uganda|Mauritius|Madagascar",
"Southern Africa":"South Africa|Namibia",
"Central America & Caribbean":"Mexico|Panama|Costa Rica|Guatemala|Honduras|El Salvador|Cuba|Dominican Republic|Jamaica|Puerto Rico|Haiti",
"Latin America":"Brazil|Chile|Colombia|Argentina|Uruguay|Peru|Ecuador|Venezuela|Paraguay|Bolivia|Guyana",
"North America":"United States|Canada","Oceania":"Australia|New Zealand"}
SR = {c: k for k, v in SUB.items() for c in v.split("|")}
src = sys.argv[1]; out = sys.argv[2] if len(sys.argv) > 2 else "china_cleantech_export_map.html"
d = pd.read_csv(src)
d = d[(d["Area type"] == "Country or economy") & (d["Commodity category"] != "All technologies")]
techs = sorted(d["Commodity category"].unique())
months = sorted(d["Date"].unique())
p = d.pivot_table(index=["Area", "Commodity category"], columns="Date", values="Amount (USD)", aggfunc="sum").reindex(columns=months).fillna(0)
reg = d.groupby("Area")["Region"].first()
C = []
for a, (la, lo) in coords.items():
    if a not in reg.index: continue
    v = [[round(x / 1e6, 2) for x in p.loc[(a, t)]] if (a, t) in p.index else [0] * len(months) for t in techs]
    C.append({"n": a, "r": reg[a] if isinstance(reg[a], str) else "Other", "sr": SR.get(a, reg[a] if isinstance(reg[a], str) else "Other"), "la": la, "lo": lo, "v": v})
data = json.dumps({"t": techs, "m": [m[:7] for m in months], "c": C}, separators=(",", ":"))
geo = "null"
if len(sys.argv) > 3:
    rings = []
    for f in json.load(open(sys.argv[3]))["features"]:
        g = f["geometry"]; polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
        for poly in polys:
            r = [[round(x, 1), round(y, 1)] for x, y in poly[0] if y > -60]
            if len(r) > 3: rings.append(r)
    geo = json.dumps(rings, separators=(",", ":"))
html = open(__file__.replace("build_map.py", "template.html")).read().replace("__DATA__", data).replace("__GEO__", geo).replace("__BUILT__", datetime.date.today().isoformat())
open(out, "w").write(html); print("wrote", out, len(html) // 1024, "KB")
