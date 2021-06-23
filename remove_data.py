import os

def delete_files(data_dir):
    dirs = os.listdir(data_dir)
    for file in dirs:
        file_path = "{}/{}".format(data_dir, file)
        # print(file_path)
        os.remove(file_path)
