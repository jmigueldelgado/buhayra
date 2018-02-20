import sys
import bin.ndwi2watermask as n2w

def main(args=None):
    """The main routine."""
    if args is None:
        args = sys.argv[1:]

    try:
        #n2w.ndwi2watermask()
        n2w.rmclouds()

        return 0
    except:
        return 1


if __name__ == "__main__":
    print main()
