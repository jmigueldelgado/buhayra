import sys

def main():
    """The main routine."""

    if sys.argv[1] is None:
        print("an argument is needed, for example: cleanup or get_scenes")
    elif sys.argv[1]=="getscenes":
        import buhayra.scenes as scenes
        scenes.getscenes()
    elif sys.argv[1]=="rmclouds":
        print("remove clouds\n")
        import ndwi2watermask.cloudmask as clouds
        clouds.rmclouds()
    elif sys.argv[1]=="sar":
        print("processing sar scene and thresholding\n")
        import sar2watermask.sar as sar
        sar.sar2w()
    elif sys.argv[1]=="ndwi":
        print("processing scene and computing ndwi\n")
        import ndwi2watermask.ndwi as n2w
        n2w.ndwi2watermask()
    elif sys.argv[1]=="test":
        print("tests environment\n")
        import ndwi2watermask.ndwi as n2w
        n2w.test_one_ndwi()
    elif sys.argv[1]=="another test":
        print("tests environment\n")
        print("test!!!!\n")
    else:
        print('please provide one of "rmclouds", "getscenes" or "ndwi"')


if __name__ == "__main__":
    print(main())
