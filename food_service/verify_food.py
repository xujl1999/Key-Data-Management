import asyncio
import os
import sys
from pathlib import Path

# Fix path to include current directory so we can import from food_service
current_dir = os.path.dirname(os.path.abspath(__file__)) # d:\dream_life\data-management\food_service
parent_dir = os.path.dirname(current_dir) # d:\dream_life\data-management
sys.path.append(parent_dir)

try:
    from food_service.app import analyze_image
except ImportError:
    # If run from parent directory directly or module issues
    sys.path.append(os.getcwd())
    from food_service.app import analyze_image

async def main():
    # Image in the same folder as this script
    image_path = Path(current_dir) / "test_food.png"
    if not image_path.exists():
        print(f"Image not found: {image_path}")
        return

    with open(image_path, "rb") as f:
        image_bytes = f.read()

    print(f"Analyzing image: {image_path.name} ({len(image_bytes)} bytes)...")
    
    # Mocking parameters
    content_type = "image/png"
    meal_hint = "lunch"
    locale = "zh-CN"
    request_id = "manual-test-001"

    # Check Environment
    print(f"API Key present: {'Yes' if os.getenv('QWEN_API_KEY') else 'No'}")
    print(f"API Base: {os.getenv('QWEN_API_BASE', 'Default')}")

    try:
        result, took, pid = await analyze_image(
            image_bytes=image_bytes,
            content_type=content_type,
            meal_hint=meal_hint,
            locale=locale,
            request_id=request_id
        )
        print("\n--- Analysis Result (JSON) ---")
        import json
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
        print("\n=== Summary ===")
        for item in result.get("items", []):
            name = item.get("name_zh") or item.get("name_en")
            cal = item.get("calories_kcal")
            macros = item.get("macros_g", {})
            print(f"🍲 {name} | 热量: {cal} kcal")
            print(f"   蛋白质: {macros.get('protein_g')}g | 脂肪: {macros.get('fat_g')}g | 碳水: {macros.get('carbs_g')}g")

    except Exception as e:
        print(f"\n❌ Error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
