# code-narrative

Composes code typing footage

## Build
```shell
$ pip3 install -r requirements.txt
```

## Run
```shell
$ ./codenarrative.sh examples/scene1.yaml 
```

## Notes
```shell
$ ffmpeg -framerate 5 -i %05d.png -c:v libx264 -vf fps=5 -pix_fmt yuv420p out.mp4
```

```shell
$ pip install black
$ black codenarrative/
```

Build mappings over keyboard typing audio file
```shell
$ ./key_click_mapper.sh
```

## Usage

```yaml
```
