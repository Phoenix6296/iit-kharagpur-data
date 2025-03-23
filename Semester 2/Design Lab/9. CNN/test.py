import argparse
import torch
import torch.nn as nn
from torchvision import datasets, transforms, models
from torch.utils.data import DataLoader
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import itertools

def get_args():
    parser = argparse.ArgumentParser(description='Evaluate AlexNet on CIFAR-10')
    parser.add_argument('--model_path', type=str, required=True, help='Path to the trained model weights (alexnet.pth)')
    parser.add_argument('--model_name', type=str, required=True, help='Name of the model for the report')
    return parser.parse_args()

def load_model(model_path, device):
    # Load AlexNet, modify for CIFAR10 (10 classes)
    model = models.alexnet(weights=True)
    num_ftrs = model.classifier[6].in_features
    model.classifier[6] = nn.Linear(num_ftrs, 10)
    model = model.to(device)
    # Load trained weights
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.eval()
    return model

def load_test_data():
    # Resize images to match the input size for AlexNet (resize -> center crop to 224)
    test_transforms = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        # Use ImageNet normalization if using a pretrained AlexNet
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                             std=[0.229, 0.224, 0.225])
    ])
    test_dataset = datasets.CIFAR10(root='./data', train=False, download=True, transform=test_transforms)
    test_loader = DataLoader(test_dataset, batch_size=128, shuffle=False, num_workers=2)
    return test_loader, test_dataset.classes

def plot_confusion_matrix(cm, classes, title='Confusion matrix', cmap=plt.cm.Blues):
    """
    This function prints and plots the confusion matrix.
    """
    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.colorbar()
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=45)
    plt.yticks(tick_marks, classes)

    # Normalize the confusion matrix.
    cm_normalized = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]

    thresh = cm.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j, i, f"{cm[i, j]}\n({cm_normalized[i, j]:.2f})",
                 horizontalalignment="center",
                 color="white" if cm[i, j] > thresh else "black")
    
    plt.ylabel('True label')
    plt.xlabel('Predicted label')
    plt.tight_layout()

def evaluate(model, test_loader, device):
    all_preds = []
    all_labels = []
    
    with torch.no_grad():
        for inputs, labels in test_loader:
            inputs = inputs.to(device)
            outputs = model(inputs)
            _, preds = torch.max(outputs, 1)
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.numpy())
    
    acc = accuracy_score(all_labels, all_preds)
    cls_report = classification_report(all_labels, all_preds, digits=4)
    cm = confusion_matrix(all_labels, all_preds)
    return acc, cls_report, cm

def generate_pdf_report(model_name, cls_report, cm, classes):
    report_filename = f"{model_name}_report.pdf"
    
    with PdfPages(report_filename) as pdf:
        # Page 1: Classification Report
        plt.figure(figsize=(8.5, 11))
        plt.axis('off')
        plt.title(f"{model_name} - Classification Report", fontsize=16)
        plt.text(0.01, 0.5, cls_report, fontsize=12, family='monospace')
        pdf.savefig()   # saves the current figure into a pdf page
        plt.close()

        # Page 2: Confusion Matrix
        plt.figure(figsize=(8, 6))
        plot_confusion_matrix(cm, classes, title=f"{model_name} - Confusion Matrix")
        pdf.savefig()
        plt.close()
        
    print(f"Report saved as {report_filename}")

def main():
    args = get_args()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    # Load the model
    model = load_model(args.model_path, device)
    
    # Load test data
    test_loader, class_names = load_test_data()
    
    # Evaluate the model
    accuracy, cls_report, cm = evaluate(model, test_loader, device)
    
    # Print evaluation metrics to console
    print(f"Accuracy: {accuracy:.4f}")
    print("Classification Report:")
    print(cls_report)
    
    # Generate PDF report
    generate_pdf_report(args.model_name, cls_report, cm, class_names)

if __name__ == '__main__':
    main()