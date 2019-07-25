from mesh import *

class ObjModel:

    def __init__(self):
        self.meshes = []
        self.currentMesh = None
        self.total_vertices = 0

    def append_mesh(self):
        self.meshes.append(Mesh())
        self.currentMesh = self.meshes[-1]

    def add_vertex(self, x, y, z):
        self.currentMesh.add_vertex(x, y, z)

    def add_normal(self,x,y,z):
        self.currentMesh.add_normal(x, y, z)

    def add_uv(self, uvx,uvy):
        self.currentMesh.add_uv(uvx,uvy)

    def add_index(self, index):
        self.currentMesh.add_index(index)

    def save_to_ply(self):
        total_faces = 0
        total_vertices = 0

        for m in self.meshes:
            total_faces += len(m.face_index)
            total_vertices += len(m.vertices)

        total_faces/=3

        data = []

        header = """ply
                format ascii 1.0
                """

        header += "element vertex %s\n" % total_vertices
        header += """property float x
        property float y
        property float z
        property float nx
        property float ny
        property float nz
        property uchar red
        property uchar green
        property uchar blue
        """


        header+="""element face %s
                property list uchar int vertex_index
            """  % (total_faces)

        header+="end_header"

        data.append(header)
        vertices = []
        faces = []
        prev_vertices = 0

        for mi in range(len(self.meshes)):

            m = self.meshes[mi]
            if mi>0:
                prev_vertices+=len(self.meshes[mi-1].vertices)

            for i in range(len(m.vertices)):
                v_pos = " ".join([format(k, ".4f") for k in m.vertices[i]])
                v_norm = " ".join([format(k, ".4f") for k in m.normals[i]])
                v_col = " ".join(map(str, m.colors[i]))

                line = "%s %s %s" % (v_pos, v_norm, v_col)
                vertices.append(line)

            for f in range(0,int(len(m.face_index)),3):
                a,b,c = m.face_index[f:f+3]
                line = "3 %s %s %s" % (a+prev_vertices,b+prev_vertices,c+prev_vertices)
                faces.append(line)

        data+=vertices
        data+=faces

        return "\n".join(data)

    def to_obj(self):


        data = []
        data.append("mtllib  ./material.mtl")

        prev_vertices = 0

        for mi in range(len(self.meshes)):
            m = self.meshes[mi]
            if mi > 0:
                prev_vertices += len(self.meshes[mi - 1].vertices)

            vertices = []
            uvs = []
            normals = []
            faces = []

            group_tag = "o mesh_%s" % (mi)
            data.append(group_tag)
            data.append("usemtl mesh_%s" % (mi))

            for v in m.vertices:
                vertices.append( "v %s" % " ".join(format(k, ".3f") for k in v))

            for uv in m.uvs:
                uvs.append( "vt %s" % " ".join(map(str, uv)))

            for n in m.normals:
                normals.append( "vn %s" % " ".join(format(k, ".3f") for k in n))

            for f in range(0, int(len(m.face_index)),3):
                a, b, c = m.face_index[f:f + 3]
                line = "f %s %s %s" % (a+prev_vertices+1,b+prev_vertices+1,c+prev_vertices+1)
                faces.append(line)

            data+=vertices
            data+=uvs
            data+=normals
            data+=faces


        return "\n".join(data)


