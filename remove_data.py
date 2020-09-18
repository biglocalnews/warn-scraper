import os 

def move_data(data_dir):

    dirs = os.listdir(data_dir)
    for file in dirs:
        file_path = "{}{}".format(data_dir, file)
        os.remove(file_path)

if __name__ == '__main__':
    move_data()