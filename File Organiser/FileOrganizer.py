import os
import shutil
from datetime import datetime

# Define extension categories
VIDEO_EXTS = {'.mp4', '.mov', '.avi', '.mkv', '.flv'}
IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg'}
DOCUMENT_EXTS = {'.pdf', '.docx', '.doc', '.txt', '.xlsx', '.pptx'}

def get_category(extension):
    ext = extension.lower()
    if ext in VIDEO_EXTS:
        return 'Videos'
    elif ext in IMAGE_EXTS:
        return 'Images'
    elif ext in DOCUMENT_EXTS:
        return 'Documents'
    else:
        return 'Others'

def log_message(logfile, message):
    try:
        with open(logfile, 'a', encoding='utf-8') as log:
            log.write(message + '\n')
    except Exception as e:
        print(f"⚠️ Failed to write to log file: {e}")

def process_item(item_path, category, target_folder, operation, log_file):
    filename = os.path.basename(item_path)
    try:
        os.makedirs(target_folder, exist_ok=True)
        dest_path = os.path.join(target_folder, filename)

        if os.path.exists(dest_path):
            base, ext = os.path.splitext(filename)
            dest_path = os.path.join(target_folder, f"{base}_duplicate{ext}")

        if operation == 'copy':
            shutil.copy2(item_path, dest_path)
            action = "Copied"
        else:
            shutil.move(item_path, dest_path)
            action = "Moved"

        msg = f"           --> {action} to '{category}' folder."
        print(msg)
        log_message(log_file, msg + "\n")

    except Exception as e:
        err_msg = f"           !! Error processing '{filename}': {e}"
        print(err_msg + "\n")
        log_message(log_file, err_msg + "\n")

def flatten_and_delete_subfolders(base_directory, log_file):
    # Find subfolders (excluding main category folders)
    subfolders = [
        f for f in os.listdir(base_directory)
        if os.path.isdir(os.path.join(base_directory, f)) and f not in ['Images', 'Videos', 'Documents', 'Others']
    ]

    if not subfolders:
        print("(No subfolders to flatten.)")
        return

    user_input = input("\nDo you want to flatten (move files up) these subfolders? (yes/no): ").strip().lower()
    if user_input != 'yes':
        print("Skipping flattening subfolders.")
        return

    print("\n🧹 Flattening subfolders (moving their contents up)...")
    for item in subfolders:
        item_path = os.path.join(base_directory, item)
        try:
            has_content = False
            for sub_item in os.listdir(item_path):
                has_content = True
                src_path = os.path.join(item_path, sub_item)
                dest_path = os.path.join(base_directory, sub_item)

                if os.path.exists(dest_path):
                    base, ext = os.path.splitext(sub_item)
                    dest_path = os.path.join(base_directory, f"{base}_from_{item}{ext}")

                shutil.move(src_path, dest_path)
                msg = f"Moved '{src_path}' to '{dest_path}'"
                print(msg)
                log_message(log_file, msg)

            if has_content:
                user_del = input(f"🗑️ Do you want to delete the empty folder '{item_path}'? (yes/no): ").strip().lower()
                if user_del == 'yes':
                    os.rmdir(item_path)
                    msg = f"Deleted empty folder '{item_path}'"
                    print(msg)
                    log_message(log_file, msg)
                else:
                    print(f"Skipped deleting folder '{item_path}'.")
                    log_message(log_file, f"Skipped deleting folder '{item_path}'.")

        except Exception as e:
            err_msg = f"⚠️ Failed to process subfolder '{item_path}': {e}"
            print(err_msg)
            log_message(log_file, err_msg)

def organize_files(directory, operation):
    log_file = os.path.join(directory, 'organize_log.txt')
    start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message(log_file, f"\n--- Scan started at {start_time} ---\n")

    try:
        if not os.path.exists(directory):
            raise FileNotFoundError(f"Directory '{directory}' does not exist.")
        if not os.path.isdir(directory):
            raise NotADirectoryError(f"Path '{directory}' is not a directory.")

        print(f"\n📂 Scanning '{directory}'...\n")

        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)

            if os.path.isdir(item_path):
                if item not in ['Images', 'Videos', 'Documents', 'Others']:
                    msg = f"[Folder]   {item} - Skipped"
                    print(msg)
                    log_message(log_file, msg)
                continue

            if os.path.isfile(item_path):
                _, ext = os.path.splitext(item)
                category = get_category(ext)

                msg = f"[File]     {item} - Type: {category}"
                print(msg)
                log_message(log_file, msg)

                target_folder = os.path.join(directory, category)
                process_item(item_path, category, target_folder, operation, log_file)

        # Prompt user whether to flatten leftover folders
        flatten_and_delete_subfolders(directory, log_file)

        end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message(log_file, f"--- Scan completed at {end_time} ---\n")

    except Exception as e:
        error_msg = f"⚠️ An unexpected error occurred: {e}"
        print(error_msg)
        log_message(log_file, error_msg)

# Entry point for multiple folder options
if __name__ == "__main__":
    print("🧭 Choose how you want to test:")
    print("1. Input multiple specific folder paths (comma-separated)")
    print("2. Process all subfolders inside a parent directory")
    
    choice = input("Enter your choice (1 or 2): ").strip()

    while True:
        operation = input("Do you want to 'copy' or 'move' the files? (copy/move): ").strip().lower()
        if operation in ['copy', 'move']:
            break
        print("❌ Invalid input. Please enter 'copy' or 'move'.")

    if choice == '1':
        folder_input = input("📥 Enter paths of folders to organize (comma-separated): ").strip()
        folder_paths = [folder.strip() for folder in folder_input.split(',') if folder.strip()]

        for folder in folder_paths:
            print(f"\n==============================")
            print(f"📦 Organizing: {folder}")
            print(f"==============================\n")
            organize_files(folder, operation)

    elif choice == '2':
        parent_folder = input("📥 Enter path of the parent folder: ").strip()

        if os.path.exists(parent_folder) and os.path.isdir(parent_folder):
            for item in os.listdir(parent_folder):
                item_path = os.path.join(parent_folder, item)
                if os.path.isdir(item_path):
                    print(f"\n==============================")
                    print(f"📦 Organizing: {item_path}")
                    print(f"==============================\n")
                    organize_files(item_path, operation)
        else:
            print("❌ Provided path is not a valid directory.")
    else:
        print("❌ Invalid option. Please restart and choose 1 or 2.")

#python3 -u "/Users/garv/Infotact File Organizer Project/FileOrganizer.py"