python ./object_detection/inference.py \
--image_path /work/cvcs_2023_group28/dataset/48938a7c88b492e6.md-barfi-0.jpg \
--output_file_name output.jpg \
--config ./object_detection/publaynet_configs/maskrcnn/maskrcnn_dit_base.yaml \
--opts MODEL.WEIGHTS ./out_sch2/model_0001649.pth
