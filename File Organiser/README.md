# 📁 Smart File Organizer with Subfolder Flattening

## 🧠 Overview

This Python script organizes files in a given folder (or set of folders) into categorized directories based on their file type:

- 📷 `Images`
- 🎥 `Videos`
- 📄 `Documents`
- 📦 `Others`

It also optionally **flattens subfolders**, **copies or moves files**, and logs every action in a text file.

## 🚀 Features

- ✅ Organize files by extension into categories
- ✅ Works with multiple folders or a parent folder containing subfolders
- ✅ Choose between **copy** or **move**
- ✅ Optionally **flatten nested subfolders**
- ✅ Optional deletion of empty subfolders
- ✅ Logs all actions and errors (`organize_log.txt`)
- ✅ Handles duplicate filenames with safe renaming

## 📂 File Type Categories

| Category  | Extensions |
|-----------|------------|
| Images    | `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.svg` |
| Videos    | `.mp4`, `.avi`, `.mov`, `.mkv`, `.flv` |
| Documents | `.pdf`, `.docx`, `.doc`, `.txt`, `.xlsx`, `.pptx` |
| Others    | Any other file types |

## 💡 How It Works

### 🟩 Step 1: Select Folder Input Mode

On running the script, choose how to supply folders:
1)Input multiple specific folder paths (comma-separated)
2)Process all subfolders inside a parent directory

### 🟩 Step 2: Choose Action

The script then asks whether to:
Do you want to 'copy' or 'move' the files? (copy/move)

- **copy**: keeps the original files in place
- **move**: transfers files into categorized folders

### 🟩 Step 3: Organizing Files

For each folder:

- Files are detected and categorized by extension
- Corresponding folders (`Images`, `Videos`, etc.) are **dynamically created**
- Files are **copied/moved** to the correct folders
- If a filename conflict occurs, it is renamed safely

Do you want to flatten (move files up) these subfolders? (yes/no)

### 🟩 Step 4: Optional Subfolder Flattening

After organization, the script prompts:


If **yes**:
- Files from subfolders are moved to the main folder
- Then asks:
Do you want to delete the empty folder 'X'? (yes/no)

### 🟩 Step 5: Logging

Every step is logged to `organize_log.txt` inside the main folder, including:

- Start/end timestamps
- File actions (copied, moved, renamed)
- Folder creations
- Errors or permission issues

## 🧪 Testing Instructions

### ✅ Single Folder
- Put test files into one folder
- Run script and use Option 1

### ✅ Multiple Folders
- Supply multiple paths via comma-separated input

### ✅ Parent Folder Mode
- Create a parent directory with multiple subfolders
- Use Option 2

### ✅ Subfolder Flattening
- Add nested subfolders inside a test folder
- Enable flattening when prompted

## 📌 Requirements

- Python 3.6+
- Standard libraries only (`os`, `shutil`, `datetime`)

## 👨‍💻 Usage

1. Save the script as `organize_files.py`
2. Run the script:
 ```bash
 python organize_files.py

## Sample Log Entry
--- Scan started at 2025-05-25 14:21:10 ---
[File]     resume.pdf - Type: Documents
           --> Moved to 'Documents' folder.
[File]     vacation.jpg - Type: Images
           --> Moved to 'Images' folder.
Moved 'project.zip' from subfolder to parent.
Deleted empty folder 'old_files'
--- Scan completed at 2025-05-25 14:21:20 ---


## Before Flattening
MyFolder/
├── holiday_photos/
│   ├── beach.jpg
│   └── mountain.png
├── notes/
│   └── todo.txt
└── image.jpg

## After Flattening
MyFolder/
├── beach.jpg
├── mountain.png
├── todo.txt
├── image.jpg


##Option 1
 Before
test_folder1/
├── holiday.jpg
├── resume.pdf
├── vacation.mp4
├── script.py
├── backup/
│   └── note.txt

test_folder2/
├── dog.png
├── report.docx
├── install.exe

  After
test_folder1/
├── Images/
│   └── holiday.jpg
├── Documents/
│   └── resume.pdf
├── Videos/
│   └── vacation.mp4
├── Others/
│   ├── script.py
│   └── note.txt
├── organize_log.txt

test_folder2/
├── Images/
│   └── dog.png
├── Documents/
│   └── report.docx
├── Others/
│   └── install.exe
├── organize_log.txt



## Option2
/Users/you/Projects/
├── FolderA/
│   ├── pic.png
│   ├── file.docx
│
├── FolderB/
│   ├── movie.mp4
│   ├── notes.txt
│
├── FolderC/
│   ├── image.jpg
│   ├── readme.md

If you choose Option 2 and provide the path /Users/you/Projects, the script will:

Go into FolderA, organize its files
Then do the same for FolderB
Then repeat for FolderC
Each folder gets processed independently — with its own new subfolders like Images, Videos, Documents, etc.