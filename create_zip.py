import os
import zipfile

def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        # Exclude directories
        dirs[:] = [d for d in dirs if d not in ['node_modules', 'venv', '__pycache__', '.git']]
        for file in files:
            file_path = os.path.join(root, file)
            # Make the path relative to the root folder of the project
            arcname = os.path.relpath(file_path, os.path.join(path, '..'))
            ziph.write(file_path, arcname)

project_path = r"c:\Users\priya\Downloads\nutrisense-ai (2)"
zip_path = r"C:\Users\priya\.gemini\antigravity\brain\f72d3f60-9765-4787-a3cf-d929e6be5351\nutrisense-ai-production.zip"

print(f"Creating zip file at {zip_path}...")
with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
    zipdir(project_path, zipf)

print("Zip creation completed successfully.")
