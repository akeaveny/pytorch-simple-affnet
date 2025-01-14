import unittest

import numpy as np

import cv2

import torch
from torch.utils import data

import sys
sys.path.append('../../')

import config

from dataset.coco import coco_dataset
from dataset.coco import coco_dataset_utils


class COCODatasetTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(COCODatasetTest, self).__init__(*args, **kwargs)

        # Load COCO dataset.
        dataset = coco_dataset.COCODataSet(
            dataset_dir=config.COCO_ROOT_DATA_PATH,
            split=config.COCO_VAL_SPLIT,
            is_train=True,
        )

        # create dataloader.
        self.data_loader = torch.utils.data.DataLoader(dataset, batch_size=1, shuffle=True)
        print(f'Selecting {len(self.data_loader)} images ..')

    def test_maskrcnn_dataloader(self):
        print('\nVisualizing Ground Truth Data for AffNet ..')

        # loop over dataset.
        for i, (image, target) in enumerate(self.data_loader):
            print(f'\n{i}/{len(self.data_loader)} ..')

            # format data.
            image = np.squeeze(np.array(image)).transpose(1, 2, 0)
            image = np.array(image * (2 ** 8 - 1), dtype=np.uint8)
            image, target = coco_dataset_utils.format_target_data(image, target)
            
            # RGB.
            cv2.imshow('rgb', cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

            # Bounding Box.
            bbox_img = coco_dataset_utils.draw_bbox_on_img(image=image,
                                                           obj_ids=target['obj_ids'],
                                                           boxes=target['obj_boxes'],
                                                           )
            cv2.imshow('bbox', cv2.cvtColor(bbox_img, cv2.COLOR_BGR2RGB))

            # Binary Masks.
            binary_mask = coco_dataset_utils.get_segmentation_masks(image=image,
                                                                    obj_ids=target['obj_ids'],
                                                                    binary_masks=target['obj_binary_masks'],
                                                                    )

            color_binary_mask = coco_dataset_utils.colorize_obj_mask(binary_mask)
            color_binary_mask = cv2.addWeighted(bbox_img, 0.35, color_binary_mask, 0.65, 0)
            cv2.imshow('binary_mask', cv2.cvtColor(color_binary_mask, cv2.COLOR_BGR2RGB))

            # show plots.
            cv2.waitKey(0)

if __name__ == '__main__':
    # unittest.main()

    # run desired test.
    suite = unittest.TestSuite()
    suite.addTest(COCODatasetTest("test_maskrcnn_dataloader"))
    runner = unittest.TextTestRunner()
    runner.run(suite)

