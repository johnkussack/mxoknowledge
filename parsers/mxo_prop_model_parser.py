from binarywalker import *
from objmodel import *
import zlib

class PropParser:

    @staticmethod
    def parse_file(file_name):

        with open(file_name, "rb") as f:
            data = f.read()
        b = BinaryWalker()
        b.setData(data)

        b.seekToStr("DIMS")

        dims_bytes_to_read = b.getInt32()
        dims_bytes_to_read2 = b.getInt32() # ignore it, already known (6 * float)

        # bounding box
        dims = []
        for i in range(6):
            dims.append(b.getFloat())

        x,y,z, x2,y2,z2 = dims

        print("Bounding box", (x,y,z), (x2,y2,z2))

        #skip to texture info
        b.seek(4) # skip "TEXT"
        text_bytes_to_read = b.getInt32()
        text_bytes_to_read2 = b.getInt32()

        textures = []
        texture_count = b.getInt32()

        for i in range(texture_count):
            textures.append(b.getBlob(4))
            print("Texture ID: ", textures[-1])

        print("Total textures: ", len(textures))

        # skip mesh+pointer
        b.seek(8)

        minX = 0
        minZ = 0
        maxX = 0
        maxZ = 0

        meshCount = b.getInt32()
        print("Mesh count: ", meshCount)

        bm = BinaryWalker()

        objM = ObjModel()

        # for each mesh, proceed to decompress and parse
        for i in range(meshCount):

            objM.append_mesh() # create a mesh in the future model

            b.seek(4)  # skip SMSH
            meshWHOLEDATASize = b.getInt32()
            b.seek(4)  # skip data

            meshBlob = b.getBlob(0x20)  # We will ignore this blob for now

            # zlib decompress the blob
            zlibBufferSize = b.getInt32()  # maybe unused in python
            meshZlibSize = b.getInt32()
            meshZlibBlob = b.getBlob(meshZlibSize)
            meshData = zlib.decompress(meshZlibBlob, bufsize=zlibBufferSize)

            # initialize a new binary walker with the info from zlib
            bm.setData(meshData)

            meshChunkLength = bm.getInt32()
            meshVerticesCount = bm.getInt32()
            bm.seek(8) # dont know what this was, but skip it

            print ("Mesh vertices count:", meshVerticesCount)

            for j in range(meshVerticesCount):
                x = -1 * bm.getFloat() / 100.0 # Reverse X axis from MXO model data
                y =  bm.getFloat() / 100.0
                z =  bm.getFloat() / 100.0

                nx = bm.getFloat()
                ny = bm.getFloat()
                nz = bm.getFloat()

                uvX = bm.getFloat()
                uvY = (1.0 - bm.getFloat())  # Reverse DDS V from directX to openGL

                objM.add_vertex(x,y,z)
                objM.add_normal(nx,ny,nz)
                objM.add_uv(uvX, uvY)

            # parse the index for faces
            while(bm.getOffset()!=meshChunkLength+4):
                index = bm.getInt16()
                objM.add_index(index)

            print("Total faces for this mesh:", len(objM.currentMesh.face_index))

        #objM.save_to_obj(file_name.split("/")[-1].replace(".prop", ".model"))
        #objM.save_to_ply(file_name.split("/")[-1].replace(".prop", ".model"))

        return objM.to_obj()



