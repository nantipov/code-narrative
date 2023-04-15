# code-narrative

## Build

```shell
$ pip3 install -r requirements.txt
```

## Run

```shell
$ python3 codenarrative/main.py examples/scene1.yaml 
```

## Notes
```shell
$ ffmpeg -framerate 5 -i %05d.png -c:v libx264 -vf fps=5 -pix_fmt yuv420p out.mp4
```

```shell
$ pip install black
$ black codenarrative/
```