import streamlit as st
import xml.etree.ElementTree as ET
import os
import re
import json
from typing import Dict, List
from zipfile import ZipFile
from io import BytesIO
from tqdm import tqdm


def get_label2id(labels_str: str) -> Dict[str, int]:
    labels = labels_str.split()
    return {label: idx + 1 for idx, label in enumerate(labels)}


def get_image_info(annotation_root, extract_num_from_imgid=True):
    path = annotation_root.findtext('path')
    filename = os.path.basename(path) if path else annotation_root.findtext('filename')
    img_name = os.path.basename(filename)
    img_id = os.path.splitext(img_name)[0]
    if extract_num_from_imgid and isinstance(img_id, str):
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
    if label not in label2id:
        raise ValueError(f"Label '{label}' not found in label2id.")
    category_id = label2id[label]

    bndbox = obj.find('bndbox')
    xmin = int(bndbox.findtext('xmin')) - 1
    ymin = int(bndbox.findtext('ymin')) - 1
    xmax = int(bndbox.findtext('xmax'))
    ymax = int(bndbox.findtext('ymax'))

    assert xmax > xmin and ymax > ymin, f"Invalid box: {xmin}, {ymin}, {xmax}, {ymax}"
    o_width = xmax - xmin
    o_height = ymax - ymin

    return {
        'area': o_width * o_height,
        'iscrowd': 0,
        'bbox': [xmin, ymin, o_width, o_height],
        'category_id': category_id,
        'ignore': 0,
        'segmentation': []
    }


def convert_xmls_to_cocojson(annotation_files: List[BytesIO],
                             label2id: Dict[str, int],
                             extract_num_from_imgid: bool = True) -> Dict:
    output_json_dict = {
        "images": [],
        "type": "instances",
        "annotations": [],
        "categories": []
    }

    bnd_id = 1
    for uploaded_file in tqdm(annotation_files):
        tree = ET.parse(uploaded_file)
        root = tree.getroot()

        img_info = get_image_info(root, extract_num_from_imgid)
        img_id = img_info['id']
        output_json_dict['images'].append(img_info)

        for obj in root.findall('object'):
            ann = get_coco_annotation_from_obj(obj, label2id)
            ann.update({'image_id': img_id, 'id': bnd_id})
            output_json_dict['annotations'].append(ann)
            bnd_id += 1

    for label, label_id in label2id.items():
        output_json_dict['categories'].append({
            'supercategory': 'none',
            'id': label_id,
            'name': label
        })

    return output_json_dict


st.title("VOC to COCO Converter 🦊➡️🐻")

st.markdown("Upload VOC XML annotation files and a label list to convert to COCO format.")

labels_file = st.file_uploader("Upload `labels.txt` (space or newline separated labels)", type=['txt'])

uploaded_xmls = st.file_uploader("Upload Annotation XML files", type=["xml"], accept_multiple_files=True)

extract_id = st.checkbox("Extract numeric ID from filename", value=True)

if labels_file is not None:
    labels_text = labels_file.read().decode('utf-8')
    label2id = get_label2id(labels_text)
    st.success(f"{len(label2id)} labels loaded: {', '.join(label2id.keys())}")
else:
    label2id = None

if uploaded_xmls and label2id:
    if st.button("Convert to COCO JSON"):
        with st.spinner("Converting..."):
            try:
                coco_json = convert_xmls_to_cocojson(
                    annotation_files=uploaded_xmls,
                    label2id=label2id,
                    extract_num_from_imgid=extract_id
                )
                output_json_str = json.dumps(coco_json, indent=2)
                st.success("Conversion successful!")

                st.download_button(
                    label="Download COCO JSON",
                    data=output_json_str,
                    file_name="output_coco.json",
                    mime="application/json"
                )
            except Exception as e:
                st.error(f"Error during conversion: {e}")
else:
    st.warning("Please upload both labels and XML files.")
