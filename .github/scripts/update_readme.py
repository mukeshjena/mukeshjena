import os
import urllib.request
import json
import re
from collections import defaultdict

# Setup
TOKEN = os.getenv("GITHUB_TOKEN")
USERNAME = "mukeshjena"

def fetch_json(url):
    req = urllib.request.Request(url)
    req.add_header('User-Agent', 'mukeshjena-profile-updater')
    if TOKEN:
        req.add_header('Authorization', f'Bearer {TOKEN}')
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def fetch_repos():
    repos = []
    page = 1
    while True:
        url = f"https://api.github.com/users/{USERNAME}/repos?per_page=100&page={page}&sort=updated"
        data = fetch_json(url)
        if not data:
            break
        repos.extend(data)
        if len(data) < 100:
            break
        page += 1
    return repos

def fetch_starred():
    url = f"https://api.github.com/users/{USERNAME}/starred?per_page=4"
    return fetch_json(url) or []

def fetch_user():
    url = f"https://api.github.com/users/{USERNAME}"
    return fetch_json(url) or {}

def generate_stats_markdown(user_data, repos):
    public_repos = user_data.get("public_repos", len(repos))
    stars = sum(repo.get("stargazers_count", 0) for repo in repos)
    followers = user_data.get("followers", 0)
    
    return f"<i>{public_repos} public repos • {stars} total stars • {followers} followers</i>"

def generate_building_markdown(repos):
    active_repos = [r for r in repos if not r.get("fork") and r.get("name") != USERNAME][:4]
    
    md = ""
    for repo in active_repos:
        name = repo.get("name")
        desc = repo.get("description") or "No description"
        url = repo.get("html_url")
        md += f"- 💻 **[{name}]({url})** — {desc}\n"
    return md

def generate_learning_markdown(starred):
    md = ""
    for repo in starred:
        name = repo.get("name")
        desc = repo.get("description") or "No description"
        url = repo.get("html_url")
        md += f"- 📚 **[{name}]({url})** — {desc}\n"
    
    # Fallback to static if no starred repos
    if not md:
        md = "- 🏛️ Distributed Systems & Event-Driven Arch\n- ⚡ Advanced .NET Performance\n- ☁️ Azure Cloud-Native Applications\n- 🐳 Kubernetes at Scale\n"
    return md

def generate_stack_markdown(repos):
    langs = defaultdict(int)
    for repo in repos:
        if repo.get("fork"):
            continue
        lang = repo.get("language")
        if lang:
            langs[lang] += 1
            
    sorted_langs = sorted(langs.items(), key=lambda x: x[1], reverse=True)[:10]
    
    colors = {
        "TypeScript": "3178C6", "JavaScript": "F7DF1E", "Python": "3776AB",
        "C#": "239120", "Dart": "0175C2", "Go": "00ADD8",
        "HTML": "E34F26", "CSS": "1572B6", "Java": "007396",
        "C++": "00599C", "Ruby": "CC342D", "PHP": "777BB4",
        "Swift": "F05138", "Kotlin": "7F52FF", "Rust": "000000"
    }
    
    logo_map = {
        "C#": "csharp",
        "C++": "cplusplus"
    }
    
    md = "**Top Languages Used**\n\n"
    for lang, count in sorted_langs:
        color = colors.get(lang, "58A6FF")
        encoded_lang = urllib.parse.quote(lang.replace("-", "--").replace(" ", "_"))
        logo = logo_map.get(lang, lang.lower())
        md += f"![{lang}](https://img.shields.io/badge/{encoded_lang}-{color}?style=flat-square&logo={logo}&logoColor=white) "
    return md + "\n"

def update_readme(stats_md, building_md, learning_md, stack_md):
    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()
        
    content = re.sub(r"(<!--STATS:start-->).*?(<!--STATS:end-->)", f"\\1\n{stats_md}\n\\2", content, flags=re.DOTALL)
    content = re.sub(r"(<!--BUILDING:start-->).*?(<!--BUILDING:end-->)", f"\\1\n{building_md}\n\\2", content, flags=re.DOTALL)
    content = re.sub(r"(<!--LEARNING:start-->).*?(<!--LEARNING:end-->)", f"\\1\n{learning_md}\n\\2", content, flags=re.DOTALL)
    content = re.sub(r"(<!--STACK:start-->).*?(<!--STACK:end-->)", f"\\1\n{stack_md}\n\\2", content, flags=re.DOTALL)
    
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    print("Fetching data...")
    user = fetch_user()
    repos = fetch_repos()
    starred = fetch_starred()
    
    print("Generating markdown...")
    stats_md = generate_stats_markdown(user, repos)
    building_md = generate_building_markdown(repos)
    learning_md = generate_learning_markdown(starred)
    stack_md = generate_stack_markdown(repos)
    
    print("Updating README.md...")
    update_readme(stats_md, building_md, learning_md, stack_md)
    print("Done!")
