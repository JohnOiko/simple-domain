import tensorflow as tf
import torch


def train(model, device, train_loader, optimizer, criterion, gradient_accumulation_steps, epochs, val_loader=None):
    for epoch in range(epochs):
        batches_num = len(train_loader)
        print(f'Epoch {epoch + 1}/{epochs}')
        pbar = tf.keras.utils.Progbar(batches_num)

        # Set training mode
        model.train()
        for batch_idx, (data, target) in enumerate(train_loader):
            data, target = data.to(device), target.to(device)

            # Compute loss and perform backpropagation
            output = model(data)
            train_loss = criterion(output, target)
            train_loss.backward()

            # Optimize and reset accumulated gradients after gradient_accumulation_steps batches
            if batch_idx % gradient_accumulation_steps == 0:
                optimizer.step()
                optimizer.zero_grad()

            pbar.update(batch_idx, values=[("loss", train_loss.item())])

        mean_val_loss = evaluate(model, device, val_loader, criterion)
        pbar.update(batches_num, values=[('val_loss', mean_val_loss)])

    return model


def evaluate(model, device, dataloader, criterion):
    # Set evaluation mode
    model.eval()
    total = 0
    running_loss = 0.0
    with torch.no_grad():
        for batch_idx, (data, target) in enumerate(dataloader):
            data, target = data.to(device), target.to(device)

            output = model(data)
            loss = criterion(output, target)
            total += target.size(0)
            running_loss = running_loss + loss.item()

    return running_loss / batch_idx
