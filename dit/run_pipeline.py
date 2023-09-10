from sys import argv
from os import listdir, mkdir
from subprocess import run
from os.path import isfile, join, isdir

if len(argv) < 3:
    print("Usage: python eval_pipeline.py <path_to_dataset> <path_to_output>")
    exit(1)

THEMES = [
    "jekyll-theme-architect",
    "jekyll-theme-cayman",
    "jekyll-theme-dinky",
    "jekyll-theme-hacker",
    "jekyll-theme-leap-day",
    "jekyll-theme-merlot",
    "jekyll-theme-midnight",
    "jekyll-theme-minimal",
    "jekyll-theme-modernist",
    "jekyll-theme-primer",
    "jekyll-theme-slate",
    "jekyll-theme-tactile",
    "jekyll-theme-time-machine"
]

path_to_dataset = argv[1]
path_to_output = argv[2]

if not isdir(path_to_dataset):
    print("Error: path_to_dataset is not a directory")
    exit(1)

if not isdir(path_to_output):
    mkdir(path_to_output)

md_files = [f.rstrip(".md") for f in listdir(path_to_dataset) if isfile(join(path_to_dataset, f)) and f.endswith(".md")]

"""
Example image names:
017786122-jekyll-theme-architect-0.jpg
017786122-jekyll-theme-architect-1.jpg

Example pipeline usage:
python pipeline.py 017786122-jekyll-theme-architect-0.jpg 017786122-jekyll-theme-architect-rec.md
"""


# for each MD file, run the pipeline
for md_file in md_files:
    for theme in THEMES:
        # get range of images from listing the dataset directory
        images = [f for f in listdir(path_to_dataset) if isfile(join(path_to_dataset, f)) and f.startswith(md_file + "-" + theme) and f.endswith(".jpg")]
        for f in images:
            image_name = join(path_to_dataset, f)
            output_name = join(path_to_output, f"{md_file}-{theme}-rec.md")
            if isfile(output_name):
                print(f"Skipping {output_name} because it already exists")
                continue
            # run pipeline
            print("python pipeline.py", image_name, output_name)
            run(["python", "pipeline.py", image_name, output_name])

