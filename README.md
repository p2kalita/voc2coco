# Install the CLI tool locally
pip install -e .

# Run it
voc2coco --ann_dir ./Annotations --ann_ids ./train.txt --labels ./labels.txt --output coco_train.json --extract_num_from_imgid
