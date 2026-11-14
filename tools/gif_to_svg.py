from pathlib import Path
from PIL import Image, ImageSequence
import base64, io, html

source = Path("assets/code-duelist-075x.gif")
target = Path("assets/code-duelist-original.svg")
with Image.open(source) as gif:
    frames = []
    durations = []
    for frame in ImageSequence.Iterator(gif):
        rgba = frame.convert("RGBA")
        buf = io.BytesIO()
        rgba.save(buf, format="PNG", optimize=True)
        frames.append(base64.b64encode(buf.getvalue()).decode("ascii"))
        durations.append(max(20, int(frame.info.get("duration", gif.info.get("duration", 200)))))
    width, height = gif.size

if not frames:
    raise RuntimeError("GIF sem quadros")

# Preserva exatamente os quadros e o tempo original (a versão GIF já é 0,75x).
total = sum(durations)
start = 0
elements = []
for index, (data, duration) in enumerate(zip(frames, durations)):
    times = [0.0, start / total, (start + duration) / total, 1.0]
    # Animação discreta: exibe um quadro por vez, sem interpolação nem redesenho.
    values = ["0", "1", "0", "0"]
    if index == 0:
        values = ["1", "1", "0", "1"]
    # Um único ciclo define o quadro visível em cada intervalo.
    schedule = []
    elapsed = 0
    for j, d in enumerate(durations):
        schedule.append((elapsed / total, "1" if j == index else "0"))
        elapsed += d
    schedule.append((1.0, "1" if index == 0 else "0"))
    key_times = ";".join(f"{t:.9f}" for t, _ in schedule)
    vals = ";".join(v for _, v in schedule)
    elements.append(
        f'<image x="0" y="0" width="{width}" height="{height}" '
        f'href="data:image/png;base64,{data}" opacity="{1 if index == 0 else 0}">'
        f'<animate attributeName="opacity" calcMode="discrete" '
        f'values="{vals}" keyTimes="{key_times}" dur="{total}ms" '
        f'repeatCount="indefinite"/></image>'
    )
svg = (
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
    f'viewBox="0 0 {width} {height}" role="img" '
    f'aria-label="The Code Duelist — animação original em loop">\n'
    + "\n".join(elements) + "\n</svg>\n"
)
target.write_text(svg, encoding="utf-8")
print(f"Convertidos {len(frames)} quadros, {total} ms, {width}x{height}; SVG {target.stat().st_size} bytes")
