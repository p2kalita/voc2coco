# voc2coco/converter.py

import os
import json
import xml.etree.ElementTree as ET
import re
from typing import Dict, List
from tqdm import tqdm


def get_label2id(labels_path: str) -> Dict[str, int]:
    with open(labels_path, 'r') as f:
        labels_str = re.split(r'[\s,]+', f.read().strip())
    labels_ids = list(range(1, len(labels_str)+1))
    return dict(zip(labels_str, labels_ids))


def get_annpaths(ann_dir_path: str = None,
                 ann_ids_path: str = None,
                 ext: str = '',
                 annpaths_list_path: str = None) -> List[str]:
    if annpaths_list_path is not None:
        with open(annpaths_list_path, 'r') as f:
            return f.read().split()

    ext_with_dot = '.' + ext if ext != '' else ''
    with open(ann_ids_path, 'r') as f:
        ann_ids = f.read().split()
    return [os.path.join(ann_dir_path, aid+ext_with_dot) for aid in ann_ids]


def get_image_info(annotation_root, extract_num_from_imgid=True):
    path = annotation_root.findtext('path')
    filename = os.path.basename(path) if path else annotation_root.findtext('filename')
    img_name = os.path.basename(filename)
    img_id = os.path.splitext(img_name)[0]
    if extract_num_from_imgid:
        img_id = int(re.findall(r'\d+', img_id)[0])

    size = annotation_root.find('size')
    width = int(size.findtext('width'))
    height = int(size.findtext('height'))

    return {
        'file_name': filename,
        'height': height,
        'width': width,
        'id': img_id
    }


def get_coco_annotation_from_obj(obj, label2id):
    label = obj.findtext('name')
    assert label in label2id, f"Error: {label} is not in label2id!"
    category_id = label2id[label]
    bndbox = obj.find('bndbox')
    xmin = int(float(bndbox.findtext('xmin'))) - 1
    ymin = int(float(bndbox.findtext('ymin'))) - 1
    xmax = int(float(bndbox.findtext('xmax')))
    ymax = int(float(bndbox.findtext('ymax')))
    assert xmax > xmin and ymax > ymin, f"Box size error!: ({xmin}, {ymin}, {xmax}, {ymax})"
    return {
        'area': (xmax - xmin) * (ymax - ymin),
        'iscrowd': 0,
        'bbox': [xmin, ymin, xmax - xmin, ymax - ymin],
        'category_id': category_id,
        'ignore': 0,
        'segmentation': []
    }


def convert_xmls_to_cocojson(annotation_paths: List[str],
                             label2id: Dict[str, int],
                             output_jsonpath: str,
                             extract_num_from_imgid: bool = True):
    output_json_dict = {
        "images": [],
        "type": "instances",
        "annotations": [],
        "categories": []
    }
    bnd_id = 1
    print('Start converting!')
    for a_path in tqdm(annotation_paths):
        ann_tree = ET.parse(a_path)
        ann_root = ann_tree.getroot()
        img_info = get_image_info(ann_root, extract_num_from_imgid)
        img_id = img_info['id']
        output_json_dict['images'].append(img_info)

        for obj in ann_root.findall('object'):
            ann = get_coco_annotation_from_obj(obj, label2id)
            ann.update({'image_id': img_id, 'id': bnd_id})
            output_json_dict['annotations'].append(ann)
            bnd_id += 1

    for label, label_id in label2id.items():
        output_json_dict['categories'].append({
            'supercategory': 'none', 'id': label_id, 'name': label
        })

    with open(output_jsonpath, 'w') as f:
        json.dump(output_json_dict, f, indent=2)
