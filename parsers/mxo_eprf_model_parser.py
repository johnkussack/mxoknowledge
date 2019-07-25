from binarywalker import *
from objmodel import *
import zlib

class EprfParser:

    @staticmethod
    def parse_file(file_name):

        with open(file_name, "rb") as f:
            data = f.read()
        b = BinaryWalker()
        b.setData(data)

        # parsing start
        b.seekToStr("MESH")

        parsing = True
        bm = BinaryWalker()
        objM = ObjModel()

        while parsing:
            meshLength = b.getInt32()
            b.seek(4) # ignore size

            meshData = b.getBlob(meshLength)


            if meshLength>=100:
                objM.append_mesh()

                bm.setData(meshData)
                bm.seek(4) # size not wanted
                bm.seek(4) # info not wanted
                bm.seek(4) # should be FFFFFFFF
                bm.seek(4) # size not wanted

                verticesCount = bm.getInt32()
                triangleCount = bm.getInt32()
                unknown = bm.getInt32()

                for i in range(verticesCount ):
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

                for i in range(triangleCount):
                    for j in range(3):
                        index = bm.getInt16()
                        objM.add_index(index)


            check = b.getBlob(4)
            if (check != bytearray("MESH",'ascii')):
                print("Finishing parsing: Meshes: ", len(objM.meshes))
                parsing = False

        # export
        return objM.to_obj()