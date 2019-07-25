from binarywalker import *

class PackmapExtractor:

    def __init__(self):
        pass

    @staticmethod
    def extract_file(key, packmap_save_location,packmap_folder, dest_full_path):
        data = ""
        try:
            with open(packmap_save_location) as f:
                data = f.read().split("\n")
        except Exception as error:
            print("Failed to open the packmap location", error)

        key = key.lower()
        lines = [k for k in data if key in k.lower()]
        if len(lines) == 0:
            print("Entry not found for key '%s'" % key)
            return

        line = lines[0].split("\"")
        file_name = line[1].split("/")[-1]
        file_location = line[3].split("/")[-1]
        offset, size = [int(k,16) for k in line[4].lstrip().split(" ")]

        try:
            raw_data = bytearray()
            with open(packmap_folder+file_location,"rb") as f:
                f.seek(offset)
                raw_data+= f.read(size)

            with open(dest_full_path+file_name,"wb+") as f:
                f.write(raw_data)

        except Exception as error:
            print("Failed to read the packmap file contents", error)

        return raw_data





