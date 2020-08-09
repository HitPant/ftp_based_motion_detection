import os.path
import os
import json



# check if config file exist
check= os.path.exists('conf1.json')
if check == True:
    conf = json.load(open("conf1.json"))#loads the values from config file
else:
    conf = json.load(open("default.json"))#default values

#functiono for optimizing
def cleanup():
    file_path = ("/home/AT/Projects/motion_detection_ftp/save")
    file_len = os.listdir(file_path)

    fold_size= 0

    for (path, dirs, files) in os.walk(file_path):
        for file in files:
            filename = os.path.join(path, file)
            fold_size += os.path.getsize(filename)
        size = fold_size/(1000*1000)

    #size and file limit is set by the user in the json file
    if (len(file_len) >= conf["max_file_limit"]) or (size >= conf["total_size"]):

        #checks the oldest file in the folder and delets it.
        delfile = min(os.listdir(file_path), key=lambda p: os.path.getctime(os.path.join(file_path, p)))
        delete = os.path.join(file_path,delfile)
        os.remove(delete) #removes the file
        print(f"{delfile} deleted!")





