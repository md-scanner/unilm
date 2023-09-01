python ./object_detection/inference.py \
--image_path ghscreenshot.png \
--output_file_name output.jpg \
--config ./object_detection/publaynet_configs/maskrcnn/maskrcnn_dit_base.yaml \
--opts MODEL.WEIGHTS model_final.pth
