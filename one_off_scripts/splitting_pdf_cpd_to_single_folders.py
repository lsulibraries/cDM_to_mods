import subprocess
import shutil
import glob
import os


def split_items(source_dir):
    pointers = set()
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            pointers.add(os.path.splitext(file)[0])
    for num, pointer in enumerate(pointers):
        dest_dir = '/vagrant/UploadToIslandora/{}'.format(num)
        os.makedirs(dest_dir, exist_ok=True)
        for extension in ('pdf', 'xml'):
            filename = '{}.{}'.format(pointer, extension)
            shutil.copy2(os.path.join(source_dir, filename), os.path.join(dest_dir, filename))
    else:
        return num


def preprocess_one(folder, parent):
    namespace = parent.split(':')[0]
    command_list = ['drush',
                    '-v',
                    'islandora_paged_content_pdf_batch_preprocess',
                    '--user=admin',
                    '--scan_target={}'.format(folder),
                    '--type=directory',
                    '--content_model=islandora:bookCModel',
                    '--parent={}'.format(parent),
                    '--namespace={}'.format(namespace),
                    ]
    completed_process = subprocess.run(command_list)
    if str(completed_process.returncode) != '0':
        print('failed preprocessing of {}'.format(folder))
        exit()


def ibi_one(count):
    command_list = ['drush',
                    '-v',
                    'ibi',
                    '--user=admin',
                    '--ingest_set={}'.format(count),
                    ]
    completed_process = subprocess.run(command_list)
    if str(completed_process.returncode) != '0':
        print('failed ibi of {}'.format(count))
        exit()


def cleanup_dir():
    for filename in ('page*', 'full*', 'curl*', 'drush_*', '*.jp2', '*.tif', 'tuque*'):
        for match in glob.glob(os.path.join('/tmp', filename)):
            os.remove(match)


if __name__ == '__main__':
    if "/var/www/ldl" not in os.getcwd():
        print('run this script with python3.6 from /var/www/ldl')
        exit()
    unsplit_directory = input('what is the path to the unzipped pdf/mods files? ')
    current_highest_batch = int(input('what is the current highest batch set? '))
    parent = input('what is the parent namespace:pid? ')
    max_folders = split_items(unsplit_directory)
    for count in range(max_folders + 1):
        preprocess_one('/vagrant/UploadToIslandora/{}'.format(count), parent)
        ibi_one(str(count + current_highest_batch + 1))
        cleanup_dir()
    for folder in os.listdir(os.path.split(unsplit_directory)[0]):
        if folder.isnumeric():
            shutil.rmtree(os.path.join(os.path.split(unsplit_directory)[0], folder))
