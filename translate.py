import os
import json
import glob
import time
import sys
import argparse
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# Categorical translation dictionary
CATEGORIES_TRANSLATION = {
    "level": {
        "beginner": "iniciante",
        "intermediate": "intermediário",
        "expert": "avançado"
    },
    "force": {
        "pull": "tração",
        "push": "empurrar",
        "static": "estático"
    },
    "mechanic": {
        "compound": "composto",
        "isolation": "isolamento"
    },
    "equipment": {
        "bands": "elásticos",
        "barbell": "barra",
        "body only": "peso corporal",
        "cable": "cabo",
        "dumbbell": "haltere",
        "e-z curl bar": "barra W",
        "exercise ball": "bola de exercício",
        "foam roll": "rolo de espuma",
        "kettlebells": "kettlebells",
        "machine": "máquina",
        "medicine ball": "bola medicinal",
        "other": "outro"
    },
    "muscles": {
        "abdominals": "abdominais",
        "abductors": "abdutores",
        "adductors": "adutores",
        "biceps": "bíceps",
        "calves": "panturrilhas",
        "chest": "peitoral",
        "forearms": "antebraços",
        "glutes": "glúteos",
        "hamstrings": "isquiotibiais",
        "lats": "dorsais",
        "lower back": "lombar",
        "middle back": "costas (meio)",
        "neck": "pescoço",
        "quadriceps": "quadríceps",
        "shoulders": "ombros",
        "traps": "trapézio",
        "triceps": "tríceps"
    }
}

def main():
    parser = argparse.ArgumentParser(description="Offline translation script.")
    parser.add_argument("--num-workers", type=int, default=1, help="Total number of parallel workers")
    parser.add_argument("--worker-id", type=int, default=0, help="ID of this worker (0-indexed)")
    args = parser.parse_args()

    print(f"Worker {args.worker_id}/{args.num_workers}: Loading Hugging Face model Helsinki-NLP/opus-mt-tc-big-en-pt...")
    model_name = "Helsinki-NLP/opus-mt-tc-big-en-pt"
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    except Exception as e:
        print(f"Worker {args.worker_id}: Error loading model: {e}")
        sys.exit(1)
        
    def translate_field(text):
        if not text or not text.strip():
            return text
        try:
            # Prepend language token for Portuguese
            input_text = f">>por<< {text}"
            inputs = tokenizer(input_text, return_tensors="pt")
            outputs = model.generate(**inputs)
            decoded = tokenizer.decode(outputs[0], skip_special_tokens=True)
            return decoded
        except Exception as e:
            print(f"Worker {args.worker_id}: Error translating text '{text[:20]}...': {e}", file=sys.stderr)
            return text
    
    src_dir = "./exercises"
    dest_dir = "./exercises_pt"
    os.makedirs(dest_dir, exist_ok=True)
    
    # Get list of all json files in exercises/
    all_json_files = sorted(glob.glob(os.path.join(src_dir, "*.json")))
    
    # Filter files for this worker (modulo assignment)
    worker_files = [filepath for idx, filepath in enumerate(all_json_files) if idx % args.num_workers == args.worker_id]
    total_files = len(worker_files)
    
    print(f"Worker {args.worker_id}/{args.num_workers}: Assigned {total_files} of {len(all_json_files)} files.")
    
    start_time = time.time()
    translated_count = 0
    skipped_count = 0
    
    for idx, filepath in enumerate(worker_files, 1):
        filename = os.path.basename(filepath)
        dest_filepath = os.path.join(dest_dir, filename)
        
        # Checkpoint/Resume: Skip if already translated
        if os.path.exists(dest_filepath):
            skipped_count += 1
            continue
            
        print(f"Worker {args.worker_id}: [{idx}/{total_files}] Translating {filename}...")
        
        with open(filepath, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except Exception as e:
                print(f"Worker {args.worker_id}: Error reading JSON {filename}: {e}", file=sys.stderr)
                continue
        
        # Translate name
        if "name" in data and data["name"]:
            data["name"] = translate_field(data["name"])
            
        # Translate instructions list
        if "instructions" in data and isinstance(data["instructions"], list):
            translated_instructions = []
            for inst in data["instructions"]:
                translated_instructions.append(translate_field(inst))
            data["instructions"] = translated_instructions
            
        # Map categorical level
        if "level" in data and data["level"] in CATEGORIES_TRANSLATION["level"]:
            data["level"] = CATEGORIES_TRANSLATION["level"][data["level"]]
            
        # Map categorical force
        if "force" in data and data["force"] in CATEGORIES_TRANSLATION["force"]:
            data["force"] = CATEGORIES_TRANSLATION["force"][data["force"]]
            
        # Map categorical mechanic
        if "mechanic" in data and data["mechanic"] in CATEGORIES_TRANSLATION["mechanic"]:
            data["mechanic"] = CATEGORIES_TRANSLATION["mechanic"][data["mechanic"]]
            
        # Map categorical equipment
        if "equipment" in data and data["equipment"] in CATEGORIES_TRANSLATION["equipment"]:
            data["equipment"] = CATEGORIES_TRANSLATION["equipment"][data["equipment"]]
            
        # Map primaryMuscles
        if "primaryMuscles" in data and isinstance(data["primaryMuscles"], list):
            data["primaryMuscles"] = [CATEGORIES_TRANSLATION["muscles"].get(m, m) for m in data["primaryMuscles"]]
            
        # Map secondaryMuscles
        if "secondaryMuscles" in data and isinstance(data["secondaryMuscles"], list):
            data["secondaryMuscles"] = [CATEGORIES_TRANSLATION["muscles"].get(m, m) for m in data["secondaryMuscles"]]
            
        # Save translated JSON
        with open(dest_filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        translated_count += 1
        
        # Report progress statistics every 10 files
        if translated_count % 10 == 0:
            elapsed = time.time() - start_time
            avg_time = elapsed / translated_count
            est_remaining = avg_time * (total_files - idx)
            print(f"Worker {args.worker_id}: Processed {translated_count} files. Avg: {avg_time:.2f}s/file. Remaining: {est_remaining/60:.2f}m")

    print(f"\nWorker {args.worker_id}: Complete! Processed: {total_files}, Translated: {translated_count}, Skipped: {skipped_count}")

if __name__ == "__main__":
    main()
