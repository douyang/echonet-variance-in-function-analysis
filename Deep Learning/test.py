import echonet
import torch
import tqdm

train_dataset = echonet.datasets.Echo(split = "train", target_type = "SmallIndex")

train_dataloader = torch.utils.data.DataLoader(train_dataset)
val_dataset = echonet.datasets.Echo(split = "val", target_type = "SmallIndex")
val_dataloader = torch.utils.data.DataLoader(val_dataset, num_workers = 5, shuffle = True)
dataloaders = {'train':train_dataloader, 'val':val_dataloader}
with open("log.csv", 'w') as output:
    for epoch in range(10):
        for phase in dataloaders.keys():
            total = 0
            n = 0
            with torch.set_grad_enabled(phase == "train"):
                with tqdm.tqdm(total = len(dataloaders[phase])) as progressbar:
                    for i, (x, outcome) in enumerate(dataloaders[phase]):
                        print(i, x.shape, outcome.shape, outcome)
                        print()
                        print()
                        print()