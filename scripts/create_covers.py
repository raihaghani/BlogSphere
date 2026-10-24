"""Generate original local SVG artwork. No remote assets or uploads."""
from pathlib import Path

PALETTES = {
    'technology': ('#dce4ee', '#243a5c', '#8da6c9'),
    'programming': ('#e8e4dc', '#5d6048', '#afb29a'),
    'artificial-intelligence': ('#e7e0f2', '#584185', '#b6a0cf'),
    'cybersecurity': ('#dde9e4', '#244f48', '#8db8a8'),
    'business': ('#f1e4d7', '#825a39', '#cda986'),
}
for index, (name, (background, foreground, accent)) in enumerate(PALETTES.items()):
    shapes = [
        f'<circle cx="400" cy="250" r="155" fill="{accent}"/><circle cx="400" cy="250" r="105" fill="{background}"/><circle cx="400" cy="250" r="55" fill="{foreground}"/><path d="M170 360L630 140" stroke="{foreground}" stroke-width="20"/>',
        f'<rect x="180" y="110" width="440" height="280" rx="24" fill="{foreground}"/><path d="M310 190L245 250L310 310M490 190L555 250L490 310M425 170L375 330" fill="none" stroke="{background}" stroke-width="16"/>',
        f'<path d="M400 70L585 170V330L400 430L215 330V170Z" fill="none" stroke="{foreground}" stroke-width="3"/><circle cx="400" cy="250" r="95" fill="{accent}"/><path d="M215 170L585 330M215 330L585 170M400 70V430" stroke="{foreground}" stroke-width="4"/><circle cx="400" cy="250" r="32" fill="{foreground}"/>',
        f'<path d="M400 75L560 135V260Q550 365 400 430Q250 365 240 260V135Z" fill="{foreground}"/><rect x="345" y="220" width="110" height="90" rx="12" fill="{background}"/><path d="M365 220V190A35 35 0 0170 0V220" fill="none" stroke="{background}" stroke-width="14"/>',
        f'<rect x="210" y="290" width="85" height="110" rx="8" fill="{accent}"/><rect x="355" y="210" width="85" height="190" rx="8" fill="{accent}"/><rect x="500" y="115" width="85" height="285" rx="8" fill="{foreground}"/><path d="M210 230L385 140L510 65" fill="none" stroke="{foreground}" stroke-width="10"/>',
    ][index]
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 500"><rect width="800" height="500" fill="{background}"/><g opacity=".25" stroke="{foreground}" fill="none"><circle cx="400" cy="250" r="220"/><path d="M0 250H800M400 0V500"/></g>{shapes}<text x="35" y="460" font-family="sans-serif" font-size="13" letter-spacing="4" fill="{foreground}">BLOGSPHERE / {name.upper().replace("-", " ")}</text></svg>'
    Path(f'static/images/{name}.svg').write_text(svg, encoding='utf-8')
