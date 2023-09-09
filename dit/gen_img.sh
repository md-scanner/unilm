python ./object_detection/inference.py \
--image_path ../../lorem-markdownum-dataset/017786122-jekyll-theme-cayman-0.jpg \
--output_file_name output.jpg \
--config ./object_detection/publaynet_configs/maskrcnn/maskrcnn_dit_base.yaml \
--opts MODEL.WEIGHTS model_final.pth
