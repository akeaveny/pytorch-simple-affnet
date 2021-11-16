import os

import numpy as np
import random

import torch
from torch.utils.tensorboard import SummaryWriter

import sys
sys.path.append('../')

import config

from model.maskrcnn import maskrcnn
from model import model_utils
from training import train_utils
from eval import eval_utils

from dataset.coco import coco_dataset_loaders


def main():

    # Init random seeds.
    random.seed(config.RANDOM_SEED)
    np.random.seed(config.RANDOM_SEED)
    torch.manual_seed(config.RANDOM_SEED)
    torch.cuda.manual_seed(config.RANDOM_SEED)

    # Setup Tensorboard.
    print('\nsaving run in .. {}'.format(config.TRAINED_MODELS_DIR))
    if not os.path.exists(config.TRAINED_MODELS_DIR):
        os.makedirs(config.TRAINED_MODELS_DIR)
    writer = SummaryWriter(f'{config.TRAINED_MODELS_DIR}')

    # Load the Model.
    print()
    model = maskrcnn.ResNetMaskRCNN(pretrained=config.IS_PRETRAINED, num_classes=config.COCO_NUM_CLASSES)
    model.to(config.DEVICE)

    # Load the dataset.
    train_loader, val_loader = coco_dataset_loaders.load_coco_train_datasets()

    # Construct an optimizer.
    params = [p for p in model.parameters() if p.requires_grad]
    optimizer = torch.optim.SGD(params, lr=config.LEARNING_RATE, weight_decay=config.WEIGHT_DECAY, momentum=config.MOMENTUM)
    lr_scheduler = torch.optim.lr_scheduler.MultiStepLR(optimizer, milestones=config.MILESTONES, gamma=config.GAMMA)

    # Main training loop.
    num_epochs = config.NUM_EPOCHS
    for epoch in range(0, num_epochs):
        print()

        if epoch < config.EPOCH_TO_TRAIN_FULL_DATASET:
            is_subsample = True
        else:
            is_subsample = False

        # train & val for one epoch
        model, optimizer = train_utils.train_one_epoch(model, optimizer, train_loader, config.DEVICE, epoch, writer, is_subsample=is_subsample)
        model, optimizer = train_utils.val_one_epoch(model, optimizer, val_loader, config.DEVICE, epoch, writer, is_subsample=is_subsample)
        # update learning rate.
        lr_scheduler.step()

        # checkpoint_path
        CHECKPOINT_PATH = config.MODEL_SAVE_PATH + 'maskrcnn_epoch_' + np.str(epoch) + '.pth'
        train_utils.save_checkpoint(model, optimizer, epoch, CHECKPOINT_PATH)
        print(f'saved model to {CHECKPOINT_PATH} ..')

if __name__ == "__main__":
    main()