from binarywalker import *
from objmodel import *
import zlib
import sys

class MgaParser:

    @staticmethod
    def parse_file(file_name):

        with open(file_name, "rb") as f:
            data = f.read()

        objM = ObjModel()
        bm = BinaryWalker()
        b = BinaryWalker()
        b.setData(data)

        b.seek(0x11)  # dunno this header yet!!!


        while(not b.reachedEnd()):

            if b.bytesRemaining()<=10: #DOH!
                break


            header = b.getBlob(6)
            objectLength = b.getInt32()
            objData = b.getBlob(objectLength)

            bm.setData(objData)
            verticesCount = bm.getInt32()
            triangleCount = bm.getInt32()

            print("Vertices count: ", verticesCount)
            print("Triangles count: ", triangleCount)

            objM.append_mesh()  # create a mesh in the future model

            unknownIndex = bm.getInt32()
            unknownIndex2 = bm.getInt32()
            blobToSkip = 0
            verticesRemaining = 0
            stuff = bytearray()

            #### THIS IS A MESS!!!!! , but a start point

            if unknownIndex == 1:
                verticesRemaining = 0
                bm.seek(4)
                blobToSkip = unknownIndex2*16
                bm.seek(blobToSkip)
            elif unknownIndex == 2:
                verticesRemaining = 4
                bm.seek(5)
                blobToSkip = 13
                bm.seek(blobToSkip)
            elif unknownIndex == 3:
                verticesRemaining = 16
                bm.seek(4)
                blobToSkip = unknownIndex2*7
                bm.seek(blobToSkip)
            elif unknownIndex == 4:
                verticesRemaining = 12

                if unknownIndex2 == 3:
                    bm.seek(6)
                    blobToSkip = unknownIndex2*28
                elif unknownIndex2 ==2:
                    blobToSkip = 18
                else:
                    print("Not known subindex before vertices data:", hex(unknownIndex))
                    sys.exit(1)
                    break

                stuff = bm.getBlob(blobToSkip)
                for s in range(len(stuff)):
                    if stuff[s]==0x33:
                        verticesRemaining = 20
                        break
            elif unknownIndex == 6:
                verticesRemaining = 16
                bm.seek(5)
                blobToSkip = unknownIndex2 *16
                bm.seek(blobToSkip)
            else:
                print("Not known subindex before vertices data:", hex(unknownIndex))
                sys.exit(1)
                break


            print(hex(bm.getInt32()))
            bm.seek(-4)

            for i in range(verticesCount):
                x = -1 * bm.getFloat() / 100.0  # Reverse X axis from MXO model data
                y = bm.getFloat() / 100.0
                z = bm.getFloat() / 100.0

                nx = bm.getFloat()
                ny = bm.getFloat()
                nz = bm.getFloat()

                if(verticesRemaining!=0):
                    bm.seek(12)

                uvX = bm.getFloat()
                uvY = (1.0 - bm.getFloat())  # Reverse DDS V from directX to openGL

                objM.add_vertex(x, y, z)
                objM.add_normal(nx, ny, nz)
                objM.add_uv(uvX, uvY)

                if (verticesRemaining != 0):
                    bm.seek(verticesRemaining-12)

            for i in range(triangleCount):
                index = bm.getInt16()
                objM.add_index(index)



            return objM.to_obj()



