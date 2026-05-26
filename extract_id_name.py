import json
import os

def main():
    dest_dir = "./dist/tradution"
    
    if not os.path.exists(dest_dir):
        print(f"Error: {dest_dir} does not exist.")
        return
        
    num_files = 10
    
    for i in range(num_files):
        src_path = os.path.join(dest_dir, f"{i}.json")
        dest_path = os.path.join(dest_dir, f"{i}_short.json")
        
        if not os.path.exists(src_path):
            print(f"Warning: {src_path} not found.")
            continue
            
        with open(src_path, "r", encoding="utf-8") as f:
            exercises = json.load(f)
            
        # Filter each exercise to only keep 'id' and 'name'
        short_exercises = []
        for ex in exercises:
            short_ex = {
                "id": ex.get("id"),
                "name": ex.get("name")
            }
            short_exercises.append(short_ex)
            
        with open(dest_path, "w", encoding="utf-8") as f_out:
            json.dump(short_exercises, f_out, ensure_ascii=False, indent=2)
            
        print(f"Saved {len(short_exercises)} reduced exercises to {dest_path}")

if __name__ == "__main__":
    main()
