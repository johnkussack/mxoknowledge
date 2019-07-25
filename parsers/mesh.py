class Mesh:

    def __init__(self, vertex_init=0):
        self.vertices = []
        self.normals = []
        self.colors = []
        self.uvs = []
        self.face_index = []

    def add_vertex(self, x, y, z):
        self.vertices.append([x, y, z])
        self.colors.append([255,255,255])

    def add_normal(self,x,y,z):
        self.normals.append([x,y,z])

    def add_uv(self, uvx,uvy):
        self.uvs.append([uvx, uvy])

    def add_index(self, index):
        self.face_index.append(index)