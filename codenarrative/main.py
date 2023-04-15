import sys
import service.scene
import service.redering


def main():
    if len(sys.argv) < 2:
        print("Missing parameter - scene filename\n")
        return

    profile_name = ""
    if len(sys.argv) >= 3:
        profile_name = sys.argv[2]

    service.redering.render(service.scene.read_scene_file(sys.argv[1]), profile_name)


if __name__ == "__main__":
    main()
