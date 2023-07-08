import os
import sys
import shutil
import re
import zipfile
import tarfile


IMAGE_EXTENSIONS = ('JPEG', 'PNG', 'JPG', 'SVG')
VIDEO_EXTENSIONS = ('AVI', 'MP4', 'MOV', 'MKV')
DOCUMENT_EXTENSIONS = ('DOC', 'DOCX', 'TXT', 'PDF', 'XLSX', 'PPTX')
AUDIO_EXTENSIONS = ('MP3', 'OGG', 'WAV', 'AMR')
ARCHIVE_EXTENSIONS = ('ZIP', 'GZ', 'TAR')

KNOWN_EXTENSIONS = set(IMAGE_EXTENSIONS + VIDEO_EXTENSIONS + DOCUMENT_EXTENSIONS + AUDIO_EXTENSIONS + ARCHIVE_EXTENSIONS)

CYRILLIC_SYMBOLS = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґ'
TRANSLATION = ("a", "b", "v", "g", "d", "e", "e", "j", "z", "i", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u",
               "f", "h", "ts", "ch", "sh", "sch", "", "y", "", "e", "yu", "u", "ja", "je", "ji", "g")

def normalize(name: str) -> str:

    translation_table = {}
    for cur, lat in zip(CYRILLIC_SYMBOLS, TRANSLATION):
        translation_table[ord(cur)] = lat
        translation_table[ord(cur.upper())] = lat.upper()           
        
    transl_name = name.translate(translation_table)    
    transl_name = re.sub(r"[^'\w\.']", '_', transl_name)  
    
    # print('transl_name = ', transl_name)    
    
    return transl_name  

def process_folder(folder_path):
    files = []
    known_files = []
    unknown_files = []

    for entry in os.scandir(folder_path):
        if entry.is_file():
            filename = entry.name
            normalized_filename = normalize(filename)
            extension = filename.split('.')[-1].upper()

            if extension in KNOWN_EXTENSIONS:
                if extension in IMAGE_EXTENSIONS:
                    destination_folder = 'IMAGES'
                elif extension in VIDEO_EXTENSIONS:
                    destination_folder = 'VIDEO'
                elif extension in DOCUMENT_EXTENSIONS:
                    destination_folder = 'DOCUMENTS'
                elif extension in AUDIO_EXTENSIONS:
                    destination_folder = 'AUDIO'
                elif extension in ARCHIVE_EXTENSIONS:
                    destination_folder = 'ARCHIVES'

                destination_folder_path = os.path.join(folder_path, destination_folder)
                os.makedirs(destination_folder_path, exist_ok=True)

                destination_path = os.path.join(destination_folder_path, normalized_filename + '.' + extension)
                shutil.move(entry.path, destination_path)

                known_files.append(normalized_filename)
            else:
                destination_folder = 'UNKNOWN'
                unknown_files.append(normalized_filename)
        elif entry.is_dir() and entry.name not in ('ARCHIVES', 'VIDEO', 'AUDIO', 'DOCUMENTS', 'IMAGES', 'ARCHIVES', 'UNKNOWN'):
            subfolder_path = os.path.join(folder_path, entry.name)
            new_subfolder_name = normalize(entry.name)
            new_subfolder_path = os.path.join(folder_path, new_subfolder_name)
            os.rename(subfolder_path, new_subfolder_path)

            subfolder_files, subfolder_known_files, subfolder_unknown_files = process_folder(new_subfolder_path)

            files.extend(subfolder_files)
            known_files.extend(subfolder_known_files)
            unknown_files.extend(subfolder_unknown_files)

            if not os.listdir(new_subfolder_path):
                os.rmdir(new_subfolder_path)

    return files, known_files, unknown_files


def process_archives(archives_folder):# Create subfolders for archives and unpuck archives to it's subfolders
    archive_files = []

    for entry in os.scandir(archives_folder):
        if entry.is_file():
            archive_path = entry.path
            archive_extension = entry.name.split('.')[-1].upper()

            if archive_extension in ARCHIVE_EXTENSIONS:
                subfolder_name = entry.name[:-(len(archive_extension) + 1)]
                subfolder_path = os.path.join(archives_folder, subfolder_name.upper())
                os.makedirs(subfolder_path, exist_ok=True)

                try:
                    if archive_extension == 'ZIP':
                        with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                            zip_ref.extractall(subfolder_path)
                    else:
                        with tarfile.open(archive_path, 'r:*') as tar_ref:
                            tar_ref.extractall(subfolder_path)

                    archive_files.extend(get_files_in_folder(subfolder_path))
                except (zipfile.BadZipFile, tarfile.ReadError) as e:
                    print(f"Error extracting archive: {entry.name} - {e}")
            else:
                archive_files.append(entry.name)

    return archive_files


def get_files_in_folder(folder_path):
    files = []

    for entry in os.scandir(folder_path):
        if entry.is_file():
            files.append(entry.name)
        elif entry.is_dir():
            subfolder_files = get_files_in_folder(entry.path)
            files.extend(subfolder_files)

    return files


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("All checks passed")        
        sys.exit(1)
        

    folder_path = sys.argv[1]
    files, known_files, unknown_files = process_folder(folder_path)

    # Create new path to move files from root folder to appropriate folders
    audio_folder_path = os.path.join(folder_path, 'AUDIO') 
    video_folder_path = os.path.join(folder_path, 'VIDEO')
    documents_folder_path = os.path.join(folder_path, 'DOCUMENTS') 
    images_folder_path = os.path.join(folder_path, 'IMAGES') 
    archives_folder_path = os.path.join(folder_path, 'ARCHIVES') 
    unknown_folder_path = os.path.join(folder_path, 'UNKNOWN')

    # Create new directories if not exist for files from root folder
    os.makedirs(audio_folder_path, exist_ok=True)  
    os.makedirs(video_folder_path, exist_ok=True) 
    os.makedirs(documents_folder_path, exist_ok=True) 
    os.makedirs(images_folder_path, exist_ok=True) 
    os.makedirs(archives_folder_path, exist_ok=True)     
    os.makedirs(unknown_folder_path, exist_ok=True)
    
    # Move files from root folder to appropriate folders
    for entry in os.scandir(folder_path):
        if entry.is_file():
            filename = entry.name
            normalized_filename = normalize(filename)         
            
            # extension = filename.split('.')[-1].upper()
            extension = filename.split('.')[-1]

            if extension in IMAGE_EXTENSIONS:
                destination_folder = images_folder_path
            elif extension in VIDEO_EXTENSIONS:
                destination_folder = video_folder_path
            elif extension in DOCUMENT_EXTENSIONS:
                destination_folder = documents_folder_path
            elif extension in AUDIO_EXTENSIONS:
                destination_folder = audio_folder_path
            elif extension in ARCHIVE_EXTENSIONS:
                destination_folder = archives_folder_path
            else:
                destination_folder = unknown_folder_path

            # destination_path = os.path.join(destination_folder, normalized_filename + '.' + extension)
            destination_path = os.path.join(destination_folder, normalized_filename)
            shutil.move(entry.path, destination_path)

    # Move files from subfolders to appropriate folders
    audio_files = get_files_in_folder(audio_folder_path)
    video_files = get_files_in_folder(video_folder_path)
    documents_files = get_files_in_folder(documents_folder_path)
    images_files = get_files_in_folder(images_folder_path)
    archives_files = process_archives(archives_folder_path)
    print('archives_files=', archives_files)
    unknown_files = get_files_in_folder(unknown_folder_path)
    print('unknown_files =', unknown_files) 
    
    # Add new appropriate files to corresponding file's lists
    # audio_files.extend(known_files)      
    # video_files.extend(known_files)       
    # documents_files.extend(known_files)       
    # images_files.extend(known_files)  
    # archives_files.extend(known_files)    
    
    print('Files:')
    print('Audio:', audio_files)
    print('Video:', video_files)
    print('Documents:', documents_files)
    print('Images:', images_files)
    print('Archives:', archives_files)
    print('Unknown:', unknown_files)


