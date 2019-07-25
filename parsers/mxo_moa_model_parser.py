from binarywalker import *
from objmodel import *
import zlib

class MoaParser:

    @staticmethod
    def parse_file(file_name):

        with open(file_name, "rb") as f:
            data = f.read()

        b = BinaryWalker()
        b.setData(data)

        parsing_file = True

        while parsing_file:
            headerSize = b.getInt32()
            b.seek(headerSize) # skip about 0x0C bytes

            moa_name_len = b.getChar()
            moa_name = b.getBlob(moa_name_len)

            print("Found moa item: ", moa_name)

            unknownTag = b.getChar()

            if unknownTag == 0x04:
                b.seek(0x50) # related to the above
            elif unknownTag == 0x01:
                b.seek(0x44)

            sub_items = b.getChar()
            print("Moa subitems: ", sub_items)

            for i in range(sub_items):
                item_texture = b.getInt32()
                item_mla = b.getInt32()
                print("Item: %s => MGA geometry file %s,  MLA file %s" % (i+1, hex(item_texture), hex(item_mla)))

                block_tag = b.getBlob(4)
                print("\tBlock:", block_tag)
                block_items = b.getChar()

                for j in range(block_items):
                    sub_block_name = b.getBlob(4)
                    sub_block_value = b.getInt32()
                    print("\t\tSubblock:", sub_block_name, "Value:", hex(sub_block_value))

                # dont understand why there is another block
                block_items_2nd = b.getInt32()
                for j in range(block_items_2nd):
                    sub_block_name = b.getBlob(4)
                    sub_block_value_type = b.getChar()

                    if sub_block_value_type == 0x03:
                        sub_block_value = b.getVector4f()
                    else:
                        print("Unknown block value: ", hex(sub_block_value_type))

                    print("\t\tSubblock2:", sub_block_name,"Value:", sub_block_value)





            b.getChar() # dont know why 1 byte remains to be read

            if b.reachedEnd():
                break







