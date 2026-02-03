# Command : python extract_frameworks.py Web_Dev_Only.json
 

# ---------- extract_frameworks.py ----------
import json
import sys
from llm.local_llama_client import call_llm

def load_json_file(filename: str) -> dict:
    """Load JSON file."""
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)

def extract_all_keys_with_context(obj, parent_chain=None, depth=0):
    """
    Recursively extract all keys with their parent chain and depth.
    Returns list of tuples: (key_name, parent_chain, depth, value_type)
    """
    if parent_chain is None:
        parent_chain = []
    
    results = []
    
    if isinstance(obj, dict):
        for key, value in obj.items():
            # Record this key with context
            results.append({
                "key": key,
                "parent_chain": parent_chain.copy(),
                "depth": depth,
                "value_type": type(value).__name__,
                "has_children": isinstance(value, (dict, list)) and len(value) > 0
            })
            
            # Recurse into children
            results.extend(extract_all_keys_with_context(value, parent_chain + [key], depth + 1))
    
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            if isinstance(item, dict):
                results.extend(extract_all_keys_with_context(item, parent_chain, depth))
    
    return results

def identify_frameworks_with_llm(all_keys_data: list) -> list:
    """
    Use local LLM to identify which keys are framework names.
    """
    # Prepare a structured list of all keys for the LLM
    key_list = []
    for item in all_keys_data:
        context = " -> ".join(item["parent_chain"]) if item["parent_chain"] else "ROOT"
        key_list.append(f"{item['key']} (parent: {context}, depth: {item['depth']})")
    
    # Create prompt for LLM
    prompt = f"""You are analyzing a web development technology stack JSON file.
Your task is to identify which keys represent FRAMEWORK or BUILD TOOL names.

Frameworks/Build tools include things like:
- Frontend frameworks: React, Vue, Angular, Svelte, Next.js, etc.
- Build tools: Vite, Webpack, Parcel, Rollup, etc.
- Backend frameworks: Django, Flask, Express, FastAPI, Spring Boot, etc.
- CSS frameworks: Tailwind, Bootstrap, etc.

NOT frameworks:
- General categories like "Frontend", "Backend", "Deployment"
- Technology types like "Node.js", "Python", "JavaScript" (these are languages)
- Deployment platforms like "Heroku", "AWS", "Netlify"
- Web servers like "Gunicorn", "NGINX", "Apache"
- Concepts like "Static Hosting", "Containerization"

Here are ALL the keys from the JSON file:
{chr(10).join(key_list)}

Return ONLY a JSON array of framework/build tool names you identified. Example format:
["React", "Vue", "Django", "Flask", "Vite", "Webpack"]

Do not include any explanations, just the JSON array.
"""

    print("🤖 Asking LLM to identify frameworks...")
    print(f"📊 Total keys to analyze: {len(key_list)}")
    
    # Call LLM
    response = call_llm(prompt, model="llama2")
    
    print("\n📝 LLM Response:")
    print(response)
    
    # Parse response
    try:
        # Try to extract JSON array from response
        import re
        match = re.search(r'\[.*?\]', response, re.DOTALL)
        if match:
            frameworks = json.loads(match.group(0))
            return frameworks
        else:
            print("⚠️ Could not find JSON array in LLM response")
            return []
    except Exception as e:
        print(f"❌ Error parsing LLM response: {e}")
        return []

def identify_frameworks_with_heuristics(all_keys_data: list) -> list:
    """
    Fallback: Use heuristics to identify frameworks.
    """
    # Common framework/build tool names
    known_frameworks = {
        # Frontend frameworks
        "react", "vue", "angular", "svelte", "solid", "preact", "lit",
        "next.js", "nuxt", "sveltekit", "remix", "astro", "gatsby",
        
        # Build tools
        "vite", "webpack", "parcel", "rollup", "esbuild", "snowpack", "turbopack",
        
        # Backend frameworks
        "django", "flask", "fastapi", "express", "koa", "hapi", "nestjs",
        "spring", "spring boot", "laravel", "symfony", "rails", "sinatra",
        "gin", "echo", "fiber", "chi",
        
        # CSS frameworks
        "tailwind", "tailwindcss", "bootstrap", "bulma", "foundation", "materialize",
        
        # Mobile frameworks
        "react native", "flutter", "ionic", "cordova", "capacitor",
        
        # Others
        "electron", "tauri", "meteor"
    }
    
    frameworks = []
    for item in all_keys_data:
        key_lower = item["key"].lower()
        
        # Check if it matches known frameworks
        if key_lower in known_frameworks:
            frameworks.append(item["key"])
            continue
        
        # Check for partial matches (e.g., "Next.js" vs "next.js")
        for known in known_frameworks:
            if known in key_lower or key_lower in known:
                frameworks.append(item["key"])
                break
    
    return list(set(frameworks))  # Remove duplicates

def main():
    if len(sys.argv) < 2:
        print("Usage: python extract_frameworks.py <json_file>")
        print("Example: python extract_frameworks.py Web_Dev_Only.json")
        sys.exit(1)
    
    json_file = sys.argv[1]
    
    print(f"📂 Loading JSON file: {json_file}")
    data = load_json_file(json_file)
    
    print("🔍 Extracting all keys with context...")
    all_keys_data = extract_all_keys_with_context(data)
    
    print(f"✅ Found {len(all_keys_data)} total keys\n")
    
    # Try LLM first
    print("=" * 70)
    print("METHOD 1: Using Local LLM (Llama2)")
    print("=" * 70)
    frameworks_llm = identify_frameworks_with_llm(all_keys_data)
    
    if frameworks_llm:
        print(f"\n✅ LLM identified {len(frameworks_llm)} frameworks:")
        for fw in sorted(frameworks_llm):
            print(f"  • {fw}")
    
    # Also try heuristics as backup
    print("\n" + "=" * 70)
    print("METHOD 2: Using Heuristics (Fallback)")
    print("=" * 70)
    frameworks_heuristic = identify_frameworks_with_heuristics(all_keys_data)
    
    if frameworks_heuristic:
        print(f"\n✅ Heuristics identified {len(frameworks_heuristic)} frameworks:")
        for fw in sorted(frameworks_heuristic):
            print(f"  • {fw}")
    
    # Combine and deduplicate
    print("\n" + "=" * 70)
    print("COMBINED RESULTS")
    print("=" * 70)
    all_frameworks = list(set(frameworks_llm + frameworks_heuristic))
    
    print(f"\n🎯 Total unique frameworks found: {len(all_frameworks)}")
    for fw in sorted(all_frameworks):
        print(f"  • {fw}")
    
    # Save to file
    output_file = "identified_frameworks.json"
    output_data = {
        "llm_identified": sorted(frameworks_llm),
        "heuristic_identified": sorted(frameworks_heuristic),
        "combined": sorted(all_frameworks)
    }
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2)
    
    print(f"\n💾 Results saved to: {output_file}")
    
    # Generate Python set for easy copy-paste
    print("\n" + "=" * 70)
    print("COPY-PASTE FOR main_runner.py:")
    print("=" * 70)
    print("\nFRAMEWORK_NODES = {")
    for fw in sorted(all_frameworks):
        print(f'    "{fw}",')
    print("}")

if __name__ == "__main__":
    main()