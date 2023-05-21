import sys
from codenarrative.service import scene_service, rendering_service


def main():
    if len(sys.argv) < 2:
        print("Missing parameter - scene filename\n")
        return

    profile_name = ""
    if len(sys.argv) >= 3:
        profile_name = sys.argv[2]

    rendering_service.render(scene_service.read_scene_file(sys.argv[1]), profile_name)


if __name__ == "__main__":
    main()
