#!/usr/bin/env python3
from pathlib import Path
import zipfile, struct, re, hashlib, json, shutil, unicodedata, collections

import argparse

ap = argparse.ArgumentParser(
    description="Build the Classic CP949 v1.0.7-rc4 translation from the audited OpenMW RC4 package and owned GOTY master files."
)
ap.add_argument("--rc4", required=True, type=Path, help="v1.0.7-rc4 MANUAL TOPIC CLOSURE ZIP")
ap.add_argument("--morrowind", required=True, type=Path, help="Morrowind.esm")
ap.add_argument("--tribunal", required=True, type=Path, help="Tribunal.esm")
ap.add_argument("--bloodmoon", required=True, type=Path, help="Bloodmoon.esm")
ap.add_argument("--output-dir", type=Path, default=Path("."), help="Directory for generated files")
args = ap.parse_args()

RC4_ZIP = args.rc4.resolve()
MORROWIND = args.morrowind.resolve()
TRIBUNAL = args.tribunal.resolve()
BLOODMOON = args.bloodmoon.resolve()
BASE = args.output_dir.resolve()
BASE.mkdir(parents=True, exist_ok=True)

OUT_BASENAME = "Morrowind_Korean_ReTranslation_v1.0.7-rc4_Classic_CP949"
WORK = BASE / ".v107_rc4_classic_build"
DIST = WORK / "MO2"
OUT_ESP = DIST / f"{OUT_BASENAME}.esp"
OUT_MRK = DIST / f"{OUT_BASENAME}.mrk"
OUT_README = DIST / "README.txt"
OUT_ZIP = BASE / f"{OUT_BASENAME}_MO2.zip"
OUT_VALIDATION = BASE / f"{OUT_BASENAME}_validation.json"
OUT_EXE_PATCHER = BASE / "patch_morrowind_cp949.py"
OUT_BUILD_NOTES = BASE / "BUILD_NOTES_v1.0.7-rc4_Classic_CP949.txt"

if WORK.exists():
    shutil.rmtree(WORK)
DIST.mkdir(parents=True)
for p in (OUT_ZIP, OUT_VALIDATION, OUT_EXE_PATCHER, OUT_BUILD_NOTES):
    if p.exists():
        p.unlink()

# Extract RC4 source.
SRC_DIR = WORK / "rc4_source"
SRC_DIR.mkdir()
with zipfile.ZipFile(RC4_ZIP) as z:
    esp_name = next(n for n in z.namelist() if n.endswith("/Morrowind_Korean_ReTranslation.esp"))
    mrk_name = next(n for n in z.namelist() if n.endswith("/Morrowind_Korean_ReTranslation.mrk"))
    SRC_ESP = SRC_DIR / "Morrowind_Korean_ReTranslation.esp"
    SRC_MRK = SRC_DIR / "Morrowind_Korean_ReTranslation.mrk"
    SRC_ESP.write_bytes(z.read(esp_name))
    SRC_MRK.write_bytes(z.read(mrk_name))

# Composite Hangul decoder.
L_CODES=[0x10,0x11,0x12,0x13,0x14,0x15,0x16,0x17,0x18,0x19,0x1A,0x1B,0x1C,0x1D,0x1E,0x1F,0x83,0x87,0xB0]
V_CODES=[0xA1,0xA2,0xA3,0xA5,0xA6,0xAA,0xB2,0xB5,0xB7,0xBA,0xBB,0xBC,0xBD,0xBF,0xC4,0xC5,0xC6,0xC7,0xC9,0xD1,0xD6]
T_CODES=[0xDC,0xDF,0xE0,0xE1,0xE2,0xE4,0xE5,0xE6,0xE7,0xE8,0xE9,0xEA,0xEB,0xEC,0xED,0xEE,0xEF,0xF1,0xF2,0xF3,0xF4,0xF6,0xF7,0xF9,0xFA,0xFB,0xFC]
LMAP={b:i for i,b in enumerate(L_CODES)}
VMAP={b:i for i,b in enumerate(V_CODES)}
TMAP={0x7F:0, **{b:i+1 for i,b in enumerate(T_CODES)}}

def decode_custom(data):
    out=[]; i=0
    while i<len(data):
        if i+2<len(data) and data[i] in LMAP and data[i+1] in VMAP and data[i+2] in TMAP:
            out.append(chr(0xAC00+((LMAP[data[i]]*21+VMAP[data[i+1]])*28+TMAP[data[i+2]])))
            i+=3
        else:
            b=data[i]
            out.append(chr(b) if b<0x80 else bytes([b]).decode("cp1252","replace"))
            i+=1
    return "".join(out)

PUNCT_FALLBACK={"\u2018":"'", "\u2019":"'", "\u201A":",", "\u201C":'"', "\u201D":'"', "\u201E":'"',
                "\u2013":"-", "\u2014":"-", "\u2026":"...", "\u00A0":" "}
fallbacks=collections.Counter()
def encode_cp949(text):
    out=bytearray()
    for ch in text:
        try:
            out+=ch.encode("cp949")
        except UnicodeEncodeError:
            if ch in PUNCT_FALLBACK:
                repl=PUNCT_FALLBACK[ch]
            else:
                decomp=unicodedata.normalize("NFKD",ch)
                repl="".join(c for c in decomp if ord(c)<128 and not unicodedata.combining(c)) or "?"
            out+=repl.encode("ascii")
            fallbacks[(ch,repl)]+=1
    return bytes(out)

def iter_records(blob):
    pos=0
    while pos<len(blob):
        rtype=blob[pos:pos+4]
        size=struct.unpack_from("<I",blob,pos+4)[0]
        rest=blob[pos+8:pos+16]
        end=pos+16+size
        if end>len(blob):raise ValueError("record overrun")
        q=pos+16; subs=[]
        while q<end:
            stype=blob[q:q+4]
            ssize=struct.unpack_from("<I",blob,q+4)[0]
            payload=blob[q+8:q+8+ssize]
            if q+8+ssize>end:raise ValueError("subrecord overrun")
            subs.append((stype,payload));q+=8+ssize
        yield rtype,rest,subs
        pos=end

def build_record(rtype,rest,subs):
    body=bytearray()
    for s,p in subs:
        body+=s+struct.pack("<I",len(p))+p
    return rtype+struct.pack("<I",len(body))+rest+body

def get_sub(subs,key):
    for s,p in subs:
        if s==key:return p
    return None

def record_id(subs):
    p=get_sub(subs,b"NAME")
    return None if p is None else p.rstrip(b"\0").decode("latin1","replace")

def sha256(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for c in iter(lambda:f.read(1024*1024),b""):h.update(c)
    return h.hexdigest()

# Last official script definition wins: Morrowind -> Tribunal -> Bloodmoon.
master_scripts={}
for master_path in (MORROWIND,TRIBUNAL,BLOODMOON):
    for rtype,rest,subs in iter_records(master_path.read_bytes()):
        if rtype!=b"SCPT":continue
        d={k:v for k,v in subs}
        schd=d.get(b"SCHD")
        if schd:
            name=schd[:32].split(b"\0",1)[0].decode("latin1","replace")
            master_scripts[name]=(master_path.name,rest,subs,d)

src_blob=SRC_ESP.read_bytes()
source_record_names=[]
source_scripts={}
for rtype,rest,subs in iter_records(src_blob):
    if rtype!=b"SCPT":continue
    d={k:v for k,v in subs}
    name=d[b"SCHD"][:32].split(b"\0",1)[0].decode("latin1","replace")
    source_record_names.append(name)
    source_scripts[name]=(rest,subs,d)

if len(source_record_names)!=238 or len(source_scripts)!=236:
    raise RuntimeError("unexpected RC4 SCPT inventory")
if set(source_scripts)-set(master_scripts):
    raise RuntimeError("source script missing from official masters")

def strip_comment(line):
    out=[];q=False
    for ch in line:
        if ch=='"':q=not q
        if ch==';' and not q:break
        out.append(ch)
    return "".join(out)

def command_lines(text,cmd):
    out=[]
    for line in text.replace("\0","").splitlines():
        s=strip_comment(line).strip()
        if s and re.search(rf"(?i)\b{re.escape(cmd)}\b",s):
            out.append(s)
    return out

def quoted_strings(line):
    return re.findall(r'"([^"]*)"',line)

def canonical_line(line):
    s=strip_comment(line).strip()
    if not s:return ""
    s=re.sub(r'(?i)(\baddtopic\s+)"[^"]*"',r'\1"<TOPIC>"',s)
    m=re.search(r"(?i)\bsay\b",s)
    if m:
        ms=list(re.finditer(r'"[^"]*"',s[m.end():]))
        if len(ms)>=2:
            a=m.end()+ms[1].start();b=m.end()+ms[1].end()
            s=s[:a]+'"<SUBTITLE>"'+s[b:]
    if re.search(r"(?i)\bmessagebox\b",s):
        c=[0]
        def repl(_):
            c[0]+=1
            return f'"<M{c[0]}>"'
        s=re.sub(r'"[^"]*"',repl,s)
    if re.search(r"(?i)\bgetpccell\b",s):
        s=re.sub(r'(?i)(\bgetpccell\s+)"[^"]*"',r'\1"<CELL>"',s)
    return re.sub(r"\s+"," ",s.lower()).strip().replace(" ,",",")

def canonical_script(text):
    return [x for line in text.replace("\0","").splitlines() if (x:=canonical_line(line))]

logic_mismatches=[]
master_source_for_script={}
for name,(_,_,sd) in source_scripts.items():
    master_name,_,_,md=master_scripts[name]
    master_source_for_script[name]=master_name
    if canonical_script(decode_custom(sd[b"SCTX"]))!=canonical_script(md[b"SCTX"].decode("latin1","replace")):
        logic_mismatches.append(name)
if logic_mismatches:
    raise RuntimeError(f"source/master logic mismatch: {logic_mismatches}")

SAY_SHORTER={
r"vo\misc\bill_assantus.wav":"아산투스: '고맙습니다, 외지인이여. 친절하고 너그러우시군요.'",
r"vo\misc\chargenwoman2.wav":"왜, 아직 멍하니 있어? 다들 기다려",
r"vo\misc\chargenname4.wav":"저들이 시키는 대로 해.",
r"vo\misc\chargendock3.wav":"들어가게.",
r"vo\misc\chargendock1.wav":"도착했군. 기록엔 자네 출신지가 없네.",
r"vo\misc\chargenwalk3.wav":"갑판으로 올라가, 죄수.",
r"vo\k\m\flw_km003.mp3":"고맙습니다.",
r"vo\misc\hit heart 3.wav":"바보!",
r"vo\misc\tr_almaend_1.mp3":"네레바린. 여기서 끝이다. 이 시계태엽 도시는 네 무덤이 될 터였다. 너는 가장 위대한 순교자가 될 터였다! 미친 소사 실로부터 모로윈드를 지키려 모든 것을 바친 영웅 네레바린. 그런데 네가 살아 있다! 살아 있단 말이다!",
r"vo\misc\tr_almaend_3.mp3":"바릴자르의 미궁 반지가 나를 이곳으로 데려왔다. 여기서 소사 실을 죽였다. 여기서 패브리칸트들을 소환해 모운홀드를 공격하게 했다. 내가 내 백성의 구원자가 될 것이다! 오직 나만이 그들을 구원하리라!",
r"vo\misc\wolfdoor.mp3":"우렁찬 음성이 울려 퍼진다.",
r"vo\misc\wolfdoornone.mp3":"대답하지 않았다.",
r"vo\misc\tr_almgreet1.mp3":"충직한 종이여, 수많은 축복이 내리기를.",
}

compiled_records=[]
script_stats=collections.Counter()
unmatched_say=[]

for name in sorted(source_scripts):
    _,_,sd=source_scripts[name]
    master_name,mrest,msubs,md=master_scripts[name]
    src_text=decode_custom(sd[b"SCTX"]).replace("\0","")
    mst_text=md[b"SCTX"].decode("latin1","replace").replace("\0","")
    scdt=md[b"SCDT"]
    repls=[]

    # MessageBox: 00 10 + uint16(text_len) + text
    src_mbs=command_lines(src_text,"messagebox")
    mst_mbs=command_lines(mst_text,"messagebox")
    if len(src_mbs)!=len(mst_mbs):raise RuntimeError(f"{name}: MessageBox count mismatch")
    cursor=0
    for sl,ml in zip(src_mbs,mst_mbs):
        sq,mq=quoted_strings(sl),quoted_strings(ml)
        if len(sq)!=len(mq) or not mq:raise RuntimeError(f"{name}: MessageBox args mismatch")
        ob=mq[0].encode("latin1");nb=encode_cp949(sq[0])
        pat=b"\x00\x10"+struct.pack("<H",len(ob))+ob
        p=scdt.find(pat,cursor)
        if p<0:raise RuntimeError(f"{name}: MessageBox text not found")
        repls.append((p+2,p+4+len(ob),struct.pack("<H",len(nb))+nb,"MessageBox"))
        search=p+len(pat)
        for oldb,newb in zip(mq[1:],sq[1:]):
            obb=oldb.encode("latin1");nbb=encode_cp949(newb)
            if len(nbb)+1>255:raise RuntimeError(f"{name}: button too long")
            bpat=bytes([len(obb)+1])+obb+b"\x00"
            bp=scdt.find(bpat,search)
            if bp<0:raise RuntimeError(f"{name}: button not found {oldb!r}")
            repls.append((bp,bp+1+len(obb),bytes([len(nbb)+1])+nbb,"MessageBoxButton"))
            search=bp+len(bpat)
        cursor=search

    # AddTopic: 22 10 + uint8(len) + topic.
    src_add=[quoted_strings(x)[-1] for x in command_lines(src_text,"addtopic") if quoted_strings(x)]
    mst_add=[quoted_strings(x)[-1] for x in command_lines(mst_text,"addtopic") if quoted_strings(x)]
    if len(src_add)!=len(mst_add):raise RuntimeError(f"{name}: AddTopic count mismatch")
    cursor=0
    for oldt,newt in zip(mst_add,src_add):
        ob=oldt.encode("latin1");nb=encode_cp949(newt)
        if len(nb)>255:raise RuntimeError(f"{name}: topic too long")
        pat=b"\x22\x10"+bytes([len(ob)])+ob
        p=scdt.find(pat,cursor)
        if p<0:raise RuntimeError(f"{name}: AddTopic not found {oldt!r}")
        repls.append((p+2,p+3+len(ob),bytes([len(nb)])+nb,"AddTopic"))
        cursor=p+len(pat)

    # Say: 1B 11 + sound path + uint16 subtitle.
    src_says=collections.defaultdict(list)
    for line in command_lines(src_text,"say"):
        q=quoted_strings(line)
        if len(q)>=2 and re.search(r"[가-힣]",q[1]):
            src_says[q[0].replace("/","\\").lower()].append(q[1])
    used={k:0 for k in src_says}
    i=0
    while i<len(scdt)-5:
        if scdt[i]==0x1B and scdt[i+1]==0x11:
            plen=scdt[i+2];ps=i+3;pe=ps+plen
            if pe+2<=len(scdt):
                sound=scdt[ps:pe].decode("latin1","replace")
                low=sound.replace("/","\\").lower()
                if low in src_says:
                    oldlen=struct.unpack_from("<H",scdt,pe)[0]
                    ss=pe+2;se=ss+oldlen
                    idx=used[low]
                    if idx<len(src_says[low]):
                        source_ko=src_says[low][idx];used[low]+=1
                        installed=SAY_SHORTER.get(low,source_ko)
                        nb=encode_cp949(installed)
                        repls.append((pe,se,struct.pack("<H",len(nb))+nb,"Say"))
                    i=se
                    continue
        i+=1
    for low,arr in src_says.items():
        for subtitle in arr[used[low]:]:
            unmatched_say.append({"script":name,"sound":low,"subtitle":subtitle})

    repls.sort(key=lambda x:x[0])
    for a,b in zip(repls,repls[1:]):
        if a[1]>b[0]:raise RuntimeError(f"{name}: replacement overlap")
    patched=bytearray(scdt)
    for start,end,new,kind in reversed(repls):
        patched[start:end]=new
        script_stats[kind]+=1

    schd=bytearray(md[b"SCHD"])
    struct.pack_into("<I",schd,44,len(patched))
    ns=[]
    for s,p in msubs:
        if s==b"SCTX":continue
        if s==b"SCHD":p=bytes(schd)
        elif s==b"SCDT":p=bytes(patched)
        ns.append((s,p))
    compiled_records.append(build_record(b"SCPT",mrest,ns))

if unmatched_say:
    raise RuntimeError(f"unmatched translated Say slots: {unmatched_say}")

# Fixed-width Classic display names.
SHORT_FNAM={
("MISC","key_Indaren"):"인다렌 무덤의 녹슨 열쇠",
("ACTI","active_sign_c_goods_01"):"베릭 저메인: 상인",
("ACTI","puzzle canal daedric triolith"):'"Doug 메시지를 넣으세요."',
("ACTI","active_sign_c_goods_caldera"):"베릭 저메인: 상인",
("ACTI","furn_bannerd_alchemy_suran"):"이바나다드 아시르나라리: 약제상",
("ACTI","furn_de_banner_pawn_suran"):"골딘 벨라람: 전당포",
("ACTI","furn_bannerd_goods_aldruhnbook"):"코두스 칼로누스: 서점",
("ACTI","furn_bannerd_books_aldruhnbook"):"코두스 칼로누스: 서점",
("CONT","urn_ash_Brinne00_unique"):'"브린 경" 라벨 항아리',
("CONT","urn_ash_Nan00_unique"):'"D. Bryant" 라벨 항아리',
("CONT","urn_ash_Lyngas00_unique"):'"G. Lyngas" 라벨 항아리',
("DOOR","Ex_Dae_door_static"):"아누드나비아로 가는 막힌 문",
("BOOK","BookSkill_Alteration4"):"비벡의 36가지 가르침, 제13설교",
("BOOK","BookSkill_Alchemy5"):"비벡의 36가지 가르침, 제18설교",
("BOOK","bookskill_unarmored3"):"비벡의 36가지 가르침, 제11설교",
("BOOK","bookskill_unarmored4"):"비벡의 36가지 가르침, 제15설교",
("BOOK","bookskill_unarmored5"):"비벡의 36가지 가르침, 제34설교",
("BOOK","BookSkill_Block5"):"비벡의 36가지 가르침, 제32설교",
("BOOK","bookskill_heavy armor5"):"비벡의 36가지 가르침, 제12설교",
("BOOK","BookSkill_Blunt Weapon4"):"비벡의 36가지 가르침, 제3설교",
("BOOK","BookSkill_Blunt Weapon5"):"비벡의 36가지 가르침, 제9설교",
("BOOK","bookskill_long blade3"):"비벡의 36가지 가르침, 제17설교",
("BOOK","bookskill_long blade4"):"비벡의 36가지 가르침, 제20설교",
("BOOK","bookskill_long blade5"):"비벡의 36가지 가르침, 제23설교",
("BOOK","BookSkill_Short Blade4"):"비벡의 36가지 가르침, 제10설교",
("BOOK","BookSkill_Short Blade5"):"비벡의 36가지 가르침, 제30설교",
("BOOK","bk_wherewereyoudragonbroke"):"용이 부서졌을 때 어디에 있었나",
("BOOK","bk_a1_2_introtocadiusus"):"세닐리아스 카디우수스의 편지",
("BOOK","bk_a1_1_caiuspackage"):"카이우스 코사데스의 꾸러미",
("BOOK","sc_ulmjuicedasfeather"):"주이시다의 깃털 두루마리",
("BOOK","sc_inasismysticfinger"):"이나시의 신비 손가락 두루마리",
("BOOK","BookSkill_Axe5_open"):"비벡의 36가지 가르침, 제16설교",
("BOOK","sc_Erna"):"에르나가 브란드르에게 보낸 쪽지",
}
DISPLAY_PAIRS={("INFO","NAME"),("INFO","BNAM"),("DIAL","NAME"),("BOOK","TEXT"),("GMST","STRV")}
DISPLAY_SUBS={"FNAM","DESC"}

out_blob=bytearray()
current_dial_type=None
stats=collections.Counter()
fnam_changes=[]
for rtype,rest,subs in iter_records(src_blob):
    rn=rtype.decode("ascii")
    if rtype==b"SCPT":
        stats["source_SCPT_removed"]+=1
        continue
    if rtype==b"DIAL":
        d=get_sub(subs,b"DATA");current_dial_type=d[0] if d else None
    rid=record_id(subs)
    ns=[]
    for s,p in subs:
        sn=s.decode("ascii")
        if rn=="INFO" and sn=="ANAM" and current_dial_type==1 and p.rstrip(b"\0")==b"Wilderness":
            stats["voice_Wilderness_ANAM_removed"]+=1
            continue
        if rn=="INFO" and sn=="ANAM":
            if decode_custom(p.rstrip(b"\0"))=="세이다 닌, 인구조사 및 세무국":
                p=b"Seyda Neen, Census and Excise Office\0"
                stats["technical_ANAM_restored"]+=1
        elif rn=="FACT" and sn=="RNAM":
            text=decode_custom(p).rstrip("\0")
            if re.search(r"[가-힣]",text):
                enc=encode_cp949(text)
                if len(enc)>31:raise RuntimeError(f"FACT/RNAM too long {rid}")
                p=enc+b"\0"*(32-len(enc));stats["FACT_RNAM_converted"]+=1
        elif ((rn,sn) in DISPLAY_PAIRS) or sn in DISPLAY_SUBS:
            text=decode_custom(p)
            if re.search(r"[가-힣]",text):
                p=encode_cp949(text);stats["display_subrecords_converted"]+=1
        if sn=="FNAM" and (rn,rid) in SHORT_FNAM:
            p=SHORT_FNAM[(rn,rid)].encode("cp949")+b"\0"
            if len(p)>32:raise RuntimeError(f"FNAM too long {(rn,rid)}")
            fnam_changes.append((rn,rid,len(p)))
        ns.append((s,p))
    out_blob+=build_record(rtype,rest,ns)

for rec in compiled_records:
    out_blob+=rec

# HEDR count.
out_records=list(iter_records(bytes(out_blob)))
first_size=struct.unpack_from("<I",out_blob,4)[0]
q=16;hedr=None;first_end=16+first_size
while q<first_end:
    s=bytes(out_blob[q:q+4]);ss=struct.unpack_from("<I",out_blob,q+4)[0]
    if s==b"HEDR":
        hedr=q+8;break
    q+=8+ss
if hedr is None:raise RuntimeError("HEDR missing")
struct.pack_into("<I",out_blob,hedr+296,len(out_records)-1)
OUT_ESP.write_bytes(out_blob)

# MRK CP949.
mrk_rows=[]
for line in SRC_MRK.read_bytes().replace(b"\r\n",b"\n").replace(b"\r",b"\n").split(b"\n"):
    if not line:continue
    parts=line.split(b"\t")
    if len(parts)!=2:raise RuntimeError("malformed MRK")
    mrk_rows.append(encode_cp949(decode_custom(parts[0]))+b"\t"+encode_cp949(decode_custom(parts[1])))
OUT_MRK.write_bytes(b"\r\n".join(mrk_rows)+b"\r\n")

# Validate.
out_records=list(iter_records(OUT_ESP.read_bytes()))
scpt_out=[];fnam_over=[];bad_rnam=[];wild=0;tech_anam=[]
current_dial_type=None
for rtype,rest,subs in out_records:
    rn=rtype.decode("ascii")
    if rtype==b"DIAL":
        d=get_sub(subs,b"DATA");current_dial_type=d[0] if d else None
    if rtype==b"SCPT":
        d={k:v for k,v in subs}
        name=d[b"SCHD"][:32].split(b"\0",1)[0].decode("latin1","replace")
        decl=struct.unpack_from("<I",d[b"SCHD"],44)[0]
        scpt_out.append((name,b"SCTX" in d,len(d.get(b"SCDT",b"")),decl))
    rid=record_id(subs)
    for s,p in subs:
        if s==b"FNAM" and len(p)>32:fnam_over.append((rn,rid,len(p)))
        if rn=="FACT" and s==b"RNAM" and len(p)!=32:bad_rnam.append((rid,len(p)))
        if rn=="INFO" and s==b"ANAM":
            if current_dial_type==1 and p.rstrip(b"\0")==b"Wilderness":wild+=1
            if decode_custom(p.rstrip(b"\0"))=="세이다 닌, 인구조사 및 세무국":tech_anam.append(rid)

proc=[]
for rtype,rest,subs in out_records:
    if rtype==b"INFO":
        i=get_sub(subs,b"INAM")
        if i and i.rstrip(b"\0")==b"14173191683162810366":
            a=get_sub(subs,b"ANAM")
            proc.append(None if a is None else a.rstrip(b"\0").decode("latin1","replace"))

checks={
"RC4_ZIP_hash":sha256(RC4_ZIP)=="49aa8c70b518539b0f8519a09940cda305187f4205677e4e8d2efdd526e5511c",
"RC4_ESP_hash":sha256(SRC_ESP)=="c83299ebc70877b61b945a5124c5b224eb758c1fdde32e4f97a3b2434bde2fa1",
"master_override_logic_match":not logic_mismatches,
"source_SCPT_238":stats["source_SCPT_removed"]==238,
"compiled_unique_SCPT_236":len(scpt_out)==236,
"all_SCPT_SCDT":all(x[2]>0 for x in scpt_out),
"no_SCPT_SCTX":all(not x[1] for x in scpt_out),
"SCHD_size_matches":all(x[2]==x[3] for x in scpt_out),
"MessageBox_main_413":script_stats["MessageBox"]==413,
"MessageBox_buttons_359":script_stats["MessageBoxButton"]==359,
"AddTopic_105":script_stats["AddTopic"]==105,
"Say_128":script_stats["Say"]==128,
"Say_unmatched_zero":not unmatched_say,
"FNAM_short_33":len(fnam_changes)==33,
"FNAM_over32_zero":not fnam_over,
"FACT_RNAM_32":not bad_rnam,
"Voice_Wilderness_zero":wild==0,
"translated_technical_ANAM_zero":not tech_anam,
"Processus_one_correct":proc==["Seyda Neen, Census and Excise Office"],
"MRK_387":len(mrk_rows)==387,
"HEDR_count":struct.unpack_from("<I",OUT_ESP.read_bytes(),hedr+296)[0]==len(out_records)-1,
}
validation={
"status":"PASS" if all(checks.values()) else "FAIL",
"runtime_status":"UNTESTED_RC4_FULL_COMPILED_BUILD; CP949 rendering and earlier compiled-Say pilot previously runtime-confirmed",
"source":{
"rc4_zip_sha256":sha256(RC4_ZIP),
"rc4_esp_sha256":sha256(SRC_ESP),
"morrowind_esm_sha256":sha256(MORROWIND),
"tribunal_esm_sha256":sha256(TRIBUNAL),
"bloodmoon_esm_sha256":sha256(BLOODMOON),
},
"output":{
"esp":OUT_ESP.name,
"esp_sha256":sha256(OUT_ESP),
"esp_size":OUT_ESP.stat().st_size,
"mrk":OUT_MRK.name,
"mrk_sha256":sha256(OUT_MRK),
"mrk_rows":len(mrk_rows),
"record_count_including_TES3":len(out_records),
"compiled_SCPT":len(scpt_out),
},
"script_compile":{
"source_SCPT_records":238,
"unique_scripts":236,
"messagebox_main":script_stats["MessageBox"],
"messagebox_buttons":script_stats["MessageBoxButton"],
"addtopic":script_stats["AddTopic"],
"translated_say":script_stats["Say"],
"unmatched_say":unmatched_say,
"master_source_distribution":dict(collections.Counter(master_source_for_script.values())),
"important_override_resolution":{
"CharGen_ring_keley":master_source_for_script["CharGen_ring_keley"],
"CavernIncarnateDoor":master_source_for_script["CavernIncarnateDoor"],
"VampireCheck":master_source_for_script["VampireCheck"],
},
},
"classic_fixes":{
"FNAM_shortened":len(fnam_changes),
"Voice_Wilderness_ANAM_removed":stats["voice_Wilderness_ANAM_removed"],
"technical_ANAM_restored":stats["technical_ANAM_restored"],
"FACT_RNAM_converted":stats["FACT_RNAM_converted"],
"display_subrecords_converted":stats["display_subrecords_converted"],
"cp949_fallbacks":{f"{a!r}->{b!r}":n for (a,b),n in fallbacks.items()},
},
"checks":checks,
}
OUT_VALIDATION.write_text(json.dumps(validation,ensure_ascii=False,indent=2),encoding="utf-8")
if validation["status"]!="PASS":
    raise RuntimeError(json.dumps(checks,ensure_ascii=False,indent=2))

readme=f"""Morrowind 한국어 재번역 v1.0.7-rc4 / Classic CP949
======================================================

정적 검증: PASS
런타임 상태: RC4 전체 compiled-script 통합판은 아직 회귀 테스트 필요
기존 CP949 렌더링과 compiled Say 방식은 실제 게임에서 확인됨.

기준 번역
---------
v1.0.7-rc4 MANUAL TOPIC CLOSURE
ESP SHA-256:
c83299ebc70877b61b945a5124c5b224eb758c1fdde32e4f97a3b2434bde2fa1

Classic 처리
------------
- 일반 표시 문자열 CP949 변환
- FNAM 32바이트 초과 33건 안전 축약
- Voice INFO ANAM="Wilderness" 조건 제거 (INFO 유지)
- 프로케수스 중복 INFO 수정 유지
- 공식 마스터의 마지막 정의(Morrowind -> Tribunal -> Bloodmoon)를 기준으로
  번역 스크립트 236개를 compiled SCDT에서 재구성
- MessageBox 본문 413개 / 버튼 359개 CP949 compiled 문자열 적용
- AddTopic 105개 CP949 compiled 문자열 적용
- 번역 scripted Say 128개 CP949 자막 적용
- 모든 출력 SCPT에 SCDT 포함, SCTX 없음 -> 소스 재컴파일 경고 방지
- GetPCCell 등 기술 문자열은 공식 마스터 값을 유지
- RC4 MRK 387행 CP949 변환본 포함

중요 수정
---------
기존 시험판에서 CavernIncarnateDoor의 Say 1개가 Morrowind.esm 구버전 기준으로
누락된 것으로 보였으나, Bloodmoon.esm이 4개 Say가 있는 최종 스크립트를 제공합니다.
이번 판은 최종 마스터 정의를 사용하므로 번역 Say 128개가 전부 1:1 대응합니다.

설치
----
1. Morrowind.esm / Tribunal.esm / Bloodmoon.esm 활성화
2. 정상 동작 중인 CP949 Korean Pilot Morrowind.exe 사용
3. 정상 동작 중인 Classic CP949 폰트 구성 유지
4. 이 ZIP을 MO2로 설치
5. {OUT_ESP.name} 활성화
6. 이전 한국어 번역 ESP 시험판 비활성화

이 ZIP에는 실행파일과 폰트 바이너리가 들어 있지 않습니다.

회귀 테스트 권장
----------------
- 새 게임 시작부 지웁/경비병 Say 자막
- 시작부 MessageBox 튜토리얼
- 흐리스카르 관련 토픽
- 프로케수스 비텔리우스 살해 토픽
- 전사 길드 / 마법사 길드 토픽
- 대장 찾기 관련 토픽
- Tribunal / Bloodmoon scripted dialogue

ESP SHA-256:
{sha256(OUT_ESP)}

MRK SHA-256:
{sha256(OUT_MRK)}
"""
OUT_README.write_text(readme,encoding="utf-8")

with zipfile.ZipFile(OUT_ZIP,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for p in sorted(DIST.iterdir()):
        if not p.is_file():
            continue
        info = zipfile.ZipInfo(p.name, date_time=(1980,1,1,0,0,0))
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = 0o100644 << 16
        info.create_system = 3
        z.writestr(info, p.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)

patcher=r'''#!/usr/bin/env python3
import argparse, hashlib
from pathlib import Path

SUPPORTED = {
    "8fe33fb11b6a682721e7456af78eefd228e8b60dc7c9f4253f89a361f8a4dfc5",
    "c3585b91741689057c18ff86a1c3381d47278cd1d81443d38ed3b179c2fa1cd8",
}
OFFSET = 0x3457C0
PATCH = bytes.fromhex(
    "5589e58b4d080fb70186c480fc81723480fcfd772f80ec813c4172283c5a7614"
    "3c6172203c7a76103c8172183cfe77142c4deb062c41eb022c47503e8b4d0ce9"
    "15000000e987000000"
)
PILOT_SHA256 = "710196b98d1a4efa174aebb5539e14b36cff20d008dc1f0c0610ce099d06cf72"

def digest(b): return hashlib.sha256(b).hexdigest()

def main():
    p=argparse.ArgumentParser(description="Patch a supported MCP Morrowind.exe for the CP949 Korean pilot.")
    p.add_argument("input",type=Path)
    p.add_argument("output",nargs="?",type=Path,default=Path("Morrowind.MCP-Korean-Pilot.exe"))
    p.add_argument("--check",action="store_true")
    a=p.parse_args()
    data=bytearray(a.input.read_bytes())
    h=digest(data)
    if h not in SUPPORTED:
        raise SystemExit(f"Unsupported input SHA-256: {h}")
    if a.check:
        print("Supported input:",h)
        return
    data[OFFSET:OFFSET+len(PATCH)] = PATCH
    a.output.write_bytes(data)
    out=digest(data)
    print("Output:",a.output)
    print("SHA-256:",out)
    if out != PILOT_SHA256:
        print("NOTE: output differs from the originally validated pilot hash.")

if __name__=="__main__":
    main()
'''
OUT_EXE_PATCHER.write_text(patcher,encoding="utf-8",newline="\n")

notes=f"""BUILD NOTES — {OUT_BASENAME}

RC4 source ZIP SHA-256:
{sha256(RC4_ZIP)}

Classic ESP SHA-256:
{sha256(OUT_ESP)}

Master resolution:
Morrowind.esm -> Tribunal.esm -> Bloodmoon.esm, last script definition wins.

All 236 unique translated script sources match the final official master logic
after normalizing only user-visible MessageBox, Say, AddTopic strings and known
GetPCCell technical literals.

Expansion overrides preserved:
- CharGen_ring_keley -> Tribunal.esm
- CavernIncarnateDoor -> Bloodmoon.esm
- VampireCheck -> Bloodmoon.esm

RC4 contains 238 SCPT records but 236 unique names because dbattackScript and
dbattackScriptOLD each occur twice. Their later duplicates only localize a
technical Seyda Neen GetPCCell string, so Classic output emits one master-correct
compiled record per unique script.

No font binary and no Morrowind.exe binary is included.
"""
OUT_BUILD_NOTES.write_text(notes,encoding="utf-8")

print("Created:",OUT_ZIP)
print("Validation:",validation["status"])
print("Runtime:",validation["runtime_status"])
print("ESP SHA-256:",sha256(OUT_ESP))
print("MRK SHA-256:",sha256(OUT_MRK))
print("ZIP SHA-256:",sha256(OUT_ZIP))
print("Compiled SCPT:",len(scpt_out))
print("MessageBox:",script_stats["MessageBox"],"main /",script_stats["MessageBoxButton"],"buttons")
print("AddTopic:",script_stats["AddTopic"])
print("Say:",script_stats["Say"])
