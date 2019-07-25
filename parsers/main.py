from mxo_packmap_extractor import *
from mxo_dss_parser import *
from mxo_prop_model_parser import *
from mxo_eprf_model_parser import *
from mxo_iprf_model_parser import *
from mxo_moa_model_parser import *
from mxo_mga_model_parser import *

output_folder = "./output/"

def save_file(data, full_path, source_extensions ,desired_ext):

    full_path = full_path.lower().split("/")[-1]
    for s in source_extensions:
        full_path = full_path.replace(".%s" % s, ".%s" % desired_ext)
    with open(output_folder + full_path,"wb+") as f:
        f.write(data)

def parse_textures():
    dss_textures = [
    "../res/img/texture.txa",
    "../res/img/succubus_int.txa",
    "../res/img/sphinx_metal.txa",
    "../res/img/dt_apt03_livflrdtl.txa",
    "../res/img/tm_0000_0000.txb",
    "../res/img/SWmap_slums_barrens.txb",
    "../res/img/tutorial_v2_minimap.txb",
        "./extracted/metro_map.txa",

    ]

    for t in dss_textures:
        raw_data = DssParser.parse_file(t)
        save_file(raw_data, t, ["txa", "txb"], "dds")


""" ###### Run the prop exporter ####"""
def parse_props():

    props = [
        "../res/prop/van_wheelless.prop",
        "../res/prop/succubus.prop",
        "./extracted/fire_ext01.prop",
    ]

    for p in props:
        raw_data = PropParser.parse_file(p)
        save_file(bytearray(raw_data,"ascii"), p, ["prop"], "obj")


def parse_eprfs():

    eprfs = ["../res/building/sl_church01.eprf",
    "../res/building/street_1l_10x10end.eprf",
    "./extracted/sl_projects02_s09_big_facade.eprf"
    ]

    for e in eprfs:
        raw_data = EprfParser.parse_file(e)
        save_file(bytearray(raw_data,"ascii"), e, ["eprf"], "obj")

def parse_iprfs():

    iprfs = ["../res/building/null_01x01_ext_wood.iprf",

    ]

    for i in iprfs:
        raw_data = IprfParser.parse_file(i)
        save_file(bytearray(raw_data,"ascii"), i, ["iprf"], "obj")


def parse_moas():

    moas = ["./extracted/temp_switch.moa",

    ]

    for m in moas:
        raw_data = MoaParser.parse_file(m)
        #save_file(bytearray(raw_data,"ascii"), m, ["moa"], "txt")

def parse_mgas():

    mgas = ["./extracted/MorphHead.mga",

    ]

    for m in mgas:
        raw_data = MgaParser.parse_file(m)
        save_file(bytearray(raw_data,"ascii"), m, ["mga"], "obj")

def extract_files():
    packmap_save_path = "../res/packmap_save/packmap_save.lta"
    packmap_path = "../packmaps/"
    key = "02000040"
    output_path = "./extracted/"

    PackmapExtractor.extract_file(key, packmap_save_path,packmap_path,output_path)

extract_files()
#parse_textures()
#parse_props()
#parse_eprfs()
#parse_moas()
#parse_mgas()