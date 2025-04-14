# voc2coco/cli.py

import argparse
from .converter import get_label2id, get_annpaths, convert_xmls_to_cocojson

def main():
    parser = argparse.ArgumentParser(description='Convert VOC XML annotations to COCO JSON.')
    parser.add_argument('--ann_dir', type=str, help='Path to annotation XML files directory.')
    parser.add_argument('--ann_ids', type=str, help='Path to annotation IDs file.')
    parser.add_argument('--ann_paths_list', type=str, help='Path to full annotation paths list.')
    parser.add_argument('--labels', type=str, required=True, help='Path to label list.')
    parser.add_argument('--output', type=str, default='output.json', help='Output JSON path.')
    parser.add_argument('--ext', type=str, default='xml', help='File extension of annotations.')
    parser.add_argument('--extract_num_from_imgid', action='store_true', help='Extract number from image ID.')

    args = parser.parse_args()
    label2id = get_label2id(args.labels)
    ann_paths = get_annpaths(args.ann_dir, args.ann_ids, args.ext, args.ann_paths_list)
    convert_xmls_to_cocojson(ann_paths, label2id, args.output, args.extract_num_from_imgid)
