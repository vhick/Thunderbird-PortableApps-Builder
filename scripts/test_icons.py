"""Offline icon pipeline contract tests, not a claim of a live upstream download."""
import hashlib,io,json,pathlib,struct,tempfile
from PIL import Image,ImageDraw
import prepare_icons as icons

with tempfile.TemporaryDirectory() as folder:
    target=pathlib.Path(folder)
    # Synthetic artwork only for an offline conversion test; never shipped.
    base=Image.new('RGBA',(256,256),(0,0,0,0))
    draw=ImageDraw.Draw(base)
    draw.ellipse((16,16,240,240), fill=(0,122,210,255))
    draw.rectangle((72,96,184,160),fill=(255,255,255,255))
    stream=io.BytesIO()
    base.save(stream,format='ICO',sizes=[(16,16),(32,32),(48,48),(128,128),(256,256)])
    raw=stream.getvalue()
    assert icons.parse_ico(raw)
    icons.create_pngs(raw,target)
    assert (target/'appicon.ico').read_bytes()==raw
    for size in icons.SIZES:
        p=target/f'appicon_{size}.png'
        with Image.open(p) as img:
            assert img.size==(size,size) and img.getbbox()
    assert len(icons.gitblob_sha(raw))==40
    broken=bytearray(raw);broken[0]=1
    try:icons.parse_ico(broken)
    except RuntimeError:pass
    else:raise AssertionError('Corrupt ICO unexpectedly accepted')
print('PASS: offline ICO parse, original binary retention, five PNG sizes, Git blob digest validation')
