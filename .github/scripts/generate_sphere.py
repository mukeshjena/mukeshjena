import math
import urllib.request
import json
import os
import sys

ICONS = [
    "html5", "css3", "javascript", "typescript", "react", "express", "nodedotjs",
    "nextdotjs", "python", "django", "c", "cplusplus", "java", "kotlin", "php",
    "dart", "mongodb", "mysql", "postgresql", "tailwindcss", "bootstrap",
    "git", "github", "gitlab", "firebase", "supabase", "appwrite",
    "redis", "docker", "androidstudio", "vercel", "netlify", "visualstudiocode",
    "figma", "framer"
]

COLORS = [
    "E34F26", "1572B6", "F7DF1E", "3178C6", "61DAFB", "000000", "339933",
    "000000", "3776AB", "092E20", "A8B9CC", "00599C", "007396", "7F52FF", "777BB4",
    "0175C2", "47A248", "4479A1", "4169E1", "06B6D4", "7952B3",
    "F05032", "181717", "FC6D26", "FFCA28", "3ECF8E", "FD366E",
    "DC382D", "2496ED", "3DDC84", "000000", "00C7B7", "007ACC",
    "F24E1E", "0055FF"
]

def get_simpleicons_path():
    paths = []
    print("Fetching icons...")
    for slug in ICONS:
        try:
            url = f"https://cdn.jsdelivr.net/npm/simple-icons@v11/icons/{slug}.svg"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                if response.status == 200:
                    svg_data = response.read().decode('utf-8')
                    start = svg_data.find('<path d="') + 9
                    end = svg_data.find('"', start)
                    path = svg_data[start:end]
                    paths.append(path)
                else:
                    paths.append(None)
        except Exception:
            paths.append(None)
    return paths

def generate_svg():
    paths = get_simpleicons_path()
    
    num_points = len(ICONS)
    frames = 60
    radius = 200
    center_x = 250
    center_y = 250
    
    points = []
    phi = math.pi * (3. - math.sqrt(5.))
    for i in range(num_points):
        y = 1 - (i / float(num_points - 1)) * 2
        r = math.sqrt(1 - y * y)
        theta = phi * i
        x = math.cos(theta) * r
        z = math.sin(theta) * r
        points.append((x, y, z))
        
    svg_content = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 500" width="500" height="500">\n'
    svg_content += '<style>.icon { transform-origin: center; }</style>\n'
    
    for i in range(num_points):
        if not paths[i]: continue
        
        x_vals = []
        y_vals = []
        scale_vals = []
        opacity_vals = []
        
        for f in range(frames + 1):
            angle = (f / frames) * 2 * math.pi
            # Rotate around Y axis
            px, py, pz = points[i]
            rx = px * math.cos(angle) + pz * math.sin(angle)
            ry = py
            rz = -px * math.sin(angle) + pz * math.cos(angle)
            
            # Perspective projection
            perspective = 300 / (300 - rz * radius * 0.5)
            proj_x = center_x + rx * radius * perspective
            proj_y = center_y + ry * radius * perspective
            
            scale = max(0.2, perspective * 1.5)
            opacity = max(0.1, (rz + 1) / 2) # closer = more opaque
            
            x_vals.append(f"{proj_x:.2f}")
            y_vals.append(f"{proj_y:.2f}")
            scale_vals.append(f"{scale:.2f}")
            opacity_vals.append(f"{opacity:.2f}")
            
        x_anim = ';'.join(x_vals)
        y_anim = ';'.join(y_vals)
        scale_anim = ';'.join(scale_vals)
        opacity_anim = ';'.join(opacity_vals)
        color = COLORS[i]
        
        svg_content += f'<g>\n'
        # Animate opacity
        svg_content += f'  <animate attributeName="opacity" values="{opacity_anim}" dur="10s" repeatCount="indefinite" />\n'
        
        # Outer group for translation
        svg_content += f'  <g>\n'
        svg_content += f'    <animateTransform attributeName="transform" type="translate" values="{x_anim}" dur="10s" repeatCount="indefinite" />\n'
        
        # Inner group for translation Y
        svg_content += f'    <g>\n'
        svg_content += f'      <animateTransform attributeName="transform" type="translate" values="{y_anim}" dur="10s" repeatCount="indefinite" additive="sum"/>\n'
        
        # Innermost group for scale
        svg_content += f'      <g>\n'
        svg_content += f'        <animateTransform attributeName="transform" type="scale" values="{scale_anim}" dur="10s" repeatCount="indefinite" additive="sum"/>\n'
        
        # The icon
        svg_content += f'        <svg x="-12" y="-12" width="24" height="24" viewBox="0 0 24 24" fill="#{color}">\n'
        svg_content += f'          <path d="{paths[i]}"/>\n'
        svg_content += f'        </svg>\n'
        
        svg_content += f'      </g>\n'
        svg_content += f'    </g>\n'
        svg_content += f'  </g>\n'
        svg_content += f'</g>\n'

    svg_content += '</svg>'
    
    with open('tech-stack-sphere.svg', 'w') as f:
        f.write(svg_content)

if __name__ == '__main__':
    generate_svg()
