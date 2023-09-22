import numpy as np
# 计算iou
intersection = np.logical_and(result1, result2)
union = np.logical_or(result1, result2)
iou_score = np.sum(intersection) / np.sum(union)
print('IoU is %s' % iou_score)
# 计算miou
def miou(y_true, y_pred):
    cm = confusion_matrix(y_true.reshape(-1), y_pred.reshape(-1), labels=[0,1, 2, 3, 4, 5])
    # print(cm)
    MIoU = np.diag(cm) / (np.sum(cm, axis=1) + np.sum(cm, axis=0) -np.diag(cm))
    MIoU = np.nanmean(MIoU)
    return MIoU
# 计算总体精度

def Pixel_Accuracy(self):
    Acc = np.diag(self.confusion_matrix).sum() / self.confusion_matrix.sum()
    return Acc

def Pixel_Accuracy_Class(self):
    Acc = np.diag(self.confusion_matrix) / self.confusion_matrix.sum(axis=1)
    Acc = np.nanmean(Acc)
    return Acc

def Mean_Intersection_over_Union(self):
    MIoU = np.diag(self.confusion_matrix) / (
                np.sum(self.confusion_matrix, axis=1) + np.sum(self.confusion_matrix, axis=0) -
                np.diag(self.confusion_matrix))
    MIoU = np.nanmean(MIoU)
    return MIoU
# 计算fwiou
def Frequency_Weighted_Intersection_over_Union(self):
    freq = np.sum(self.confusion_matrix, axis=1) / np.sum(self.confusion_matrix)
    iu = np.diag(self.confusion_matrix) / (
                np.sum(self.confusion_matrix, axis=1) + np.sum(self.confusion_matrix, axis=0) -
                np.diag(self.confusion_matrix))

    FWIoU = (freq[freq > 0] * iu[freq > 0]).sum()
    
    # cm = self.confusion_matrix
    # freq = np.sum(cm[1:], axis = 1) / np.sum(cm[1:])
    # iu = np.diag(cm) / (np.sum(cm, axis=1) + np.sum(cm, axis=0) - np.diag(cm))
    # FWIoU = (freq[freq > 0] * iu[freq > 0]).sum()
    
    return FWIoU
