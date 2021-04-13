import json
import lock
import os
import shutil


def update_field_in_file(path, field, updated_value):
    key = lock.lock()
    if key == 'key':
        while True:
            try:
                with open(path, 'r') as old_file:
                    readable_file = json.load(old_file)
                    readable_file[field] = updated_value
                    break
            except Exception as e:
                print(e)
                print('this error appeared in update_field_in_file for file: ' + path)
        while True:
            try:
                with open(path, 'w') as new_file:
                    json.dump(readable_file, new_file, indent=4)
                break
            except Exception as e:
                print(e)
                print('this error appeared in update_field_in_file for file: ' + path)
        lock.unlock()


def read_field_in_file(path, field):
    key = lock.lock()
    if key == 'key':
        while True:
            try:
                with open(path, 'r') as f:
                    file = json.load(f)
                    break
            except Exception as e:
                print(e)
                print('this error appeared in read_field_in_file for file: ' + path)
        lock.unlock()
        return file[field]


def write_file(file_path, contents):
    key = lock.lock()
    if key == 'key':
        while True:
            try:
                with open(file_path, 'w') as f:
                    json.dump(contents, f, indent=4)
                break
            except Exception as e:
                print(e)
                print('this error appeared in write_file for file: ' + file_path)
        lock.unlock()


def clean_directory():
    directory_path = 'temporary'
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))
            print('this error appeared in clean_directory')
    while lock.locking_queue.qsize() > 0:
        lock.lock()
    lock.unlock()
