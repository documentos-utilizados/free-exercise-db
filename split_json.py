import json
import os
import math

def main():
    json_path = "./dist/exercises.json"
    dest_dir = "./dist/tradution"
    
    if not os.path.exists(json_path):
        print(f"Error: {json_path} does not exist.")
        return
        
    os.makedirs(dest_dir, exist_ok=True)
    
    with open(json_path, "r", encoding="utf-8") as f:
        exercises = json.load(f)
        
    total_exercises = len(exercises)
    num_files = 10
    
    # We want exactly 10 files. Let's calculate the slice indices.
    # To split as evenly as possible:
    chunk_size = math.ceil(total_exercises / num_files) # 88
    
    for i in range(num_files):
        start_idx = i * chunk_size
        end_idx = min(start_idx + chunk_size, total_exercises)
        chunk = exercises[start_idx:end_idx]
        
        output_path = os.path.join(dest_dir, f"{i}.json")
        with open(output_path, "w", encoding="utf-8") as out_f:
            json.dump(chunk, out_f, ensure_ascii=False, indent=2)
            
        print(f"Saved {len(chunk)} exercises to {output_path}")

if __name__ == "__main__":
    main()
