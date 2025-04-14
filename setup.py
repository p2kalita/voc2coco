from setuptools import setup, find_packages

setup(
    name='voc2coco',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'tqdm',
    ],
    entry_points={
        'console_scripts': [
            'voc2coco = voc2coco.cli:main',
        ],
    },
    author='Your Name',
    description='Convert VOC XML annotations to COCO JSON.',
    python_requires='>=3.6',
)
