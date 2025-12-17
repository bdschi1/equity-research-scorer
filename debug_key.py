import os
from dotenv import load_dotenv

# 1. Check if a global system key exists (The "Ghost Key")
global_key = os.environ.get("OPENAI_API_KEY")
if global_key:
    print(f"👻 FOUND GHOST KEY (Global): {global_key[:8]}... (This might be overriding your .env)")
else:
    print("✅ No global ghost key found.")

# 2. Force load the .env file
print("📂 Loading .env file...")
load_dotenv(override=True) # <--- The 'override=True' is the secret weapon

# 3. Check the final key
final_key = os.environ.get("OPENAI_API_KEY")
if final_key:
    print(f"🔑 FINAL KEY TO BE USED: {final_key[:8]}... (Check if this matches your new key)")
else:
    print("❌ ERROR: No key found at all.")