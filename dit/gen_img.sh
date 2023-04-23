python ./object_detection/inference.py \                                                          13s   layoutlmv3
--image_path ~/gits/48938a7c88b492e6.md-base-0.jpg \
--output_file_name output.jpg \
--config ./object_detection/publaynet_configs/maskrcnn/maskrcnn_dit_base.yaml \
--opts MODEL.WEIGHTS https://layoutlm.blob.core.windows.net/dit/dit-fts/publaynet_dit-b_mrcnn.pth
