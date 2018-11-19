from admm_research.method import AdmmSize, AdmmGCSize
from admm_research.dataset import MedicalImageDataset, segment_transform, augment
from torch.utils.data import DataLoader
from admm_research.arch import get_arch
from admm_research.loss import get_loss_fn
import torch
from admm_research import flags
import warnings

warnings.filterwarnings('ignore')


def test_admm_size():
    root_dir = '../dataset/ACDC-2D-All'
    train_dataset = MedicalImageDataset(root_dir, 'train', transform=segment_transform((200, 200)), augment=augment)
    val_dataset = MedicalImageDataset(root_dir, 'val', transform=segment_transform((200, 200)), augment=None)
    train_loader = DataLoader(train_dataset, batch_size=1, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=1, shuffle=False)
    AdmmSize.setup_arch_flags()
    hparams = flags.FLAGS.flag_values_dict()
    torchnet = get_arch('enet', **{'num_classes': 2})
    # torchnet.load_state_dict(torch.load('/Users/jizong/workspace/DGA1033/checkpoints/weakly/enet_fdice_0.8906.pth',map_location=lambda storage, loc: storage))

    # optim_hparams = {'weight_decay': 0, 'lr': 1e-4, 'amsgrad': True, 'betas': (0.5, 0.999)}
    # size_hparams = {'individual_size_constraint': True, 'eps': 0.5}

    weight = torch.Tensor([0.1, 1])
    criterion = get_loss_fn('cross_entropy', weight=weight)

    test_admm = AdmmSize(torchnet, hparams)

    val_score = test_admm.evaluate(val_loader)
    print(val_score)

    for i, (img, gt, wgt, _) in enumerate(train_loader):
        if gt.sum() == 0 or wgt.sum() == 0:
            continue
        test_admm.reset(img)
        for j in range(10):
            test_admm.update((img, gt, wgt), criterion)


def test_admm_gc_size():
    root_dir = '../dataset/ACDC-2D-All'
    train_dataset = MedicalImageDataset(root_dir, 'train', transform=segment_transform((128, 128)), augment=augment)
    val_dataset = MedicalImageDataset(root_dir, 'val', transform=segment_transform((128, 128)), augment=None)
    train_loader = DataLoader(train_dataset, batch_size=1, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=1, shuffle=False)
    AdmmGCSize.setup_arch_flags()
    hparams = flags.FLAGS.flag_values_dict()
    torchnet = get_arch('enet', **{'num_classes': 2})
    torchnet.load_state_dict(torch.load('/Users/jizong/workspace/DGA1033/checkpoints/weakly/enet_fdice_0.8906.pth',
                                        map_location=lambda storage, loc: storage))

    weight = torch.Tensor([0, 1])
    criterion = get_loss_fn('cross_entropy', weight=weight)

    test_admm = AdmmGCSize(torchnet, hparams)

    val_score = test_admm.evaluate(val_loader)
    print(val_score)

    for i, (img, gt, wgt, _) in enumerate(train_loader):
        if gt.sum() == 0 or wgt.sum() == 0:
            continue
        test_admm.reset(img)
        for j in range(2):
            test_admm.update((img, gt, wgt), criterion)


if __name__ == '__main__':
    test_admm_gc_size()
