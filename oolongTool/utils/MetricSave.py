import math
import torch
from torch.utils.tensorboard import SummaryWriter
import numpy as np
import os
import dill
import time
import copy
import json

class MetricSaverBase(object):
    def __init__(self, adding_attributes=None):
        self._mean_acc = None
        self._best_acc = None
        self._best_loss = None
        self._train_loss = []
        self._train_acc = []
        self._eva_loss = []
        self._eva_acc = []
        if adding_attributes is not None:
            for l in adding_attributes:
                setattr(self, l, None)

    @property
    def best_acc(self):
        if len(self._eva_acc) == 0:
            self._best_acc = 0
        else:
            self._best_acc = np.max(self._eva_acc)
        return self._best_acc
    
    @property
    def mean_acc(self):
        if len(self._eva_acc) == 0:
            self._mean_acc = 0
        else:
            self._mean_acc = np.mean(self._eva_acc)
        return self._mean_acc
    
    @property
    def train_acc(self):
        if len(self._train_acc) == 0:
            return 0
        else:
            return self._train_acc[-1]
    
    @property
    def train_loss(self):
        if len(self._train_loss) == 0:
            return 0
        else:
            return self._train_loss[-1]
    
    @property
    def eva_acc(self):
        if len(self._eva_acc) == 0:
            return 0
        else:
            return self._eva_acc[-1]
    
    @property
    def eva_loss(self):
        if len(self._eva_loss) == 0:
            return 0
        else:
            return self._eva_loss[-1]
    # def save_dict(self, d):
    #     for key, value in d:
    #         setattr(self, key, value)
    
    def add_record(self, epoch_train_acc, epoch_train_loss, epoch_eva_acc=None, epoch_eva_loss=None):
        self._train_acc.append(epoch_train_acc)
        self._train_loss.append(epoch_train_loss)
        if epoch_eva_acc is not None:
            self._eva_acc.append(epoch_eva_acc)
        if epoch_eva_loss is not None:
            self._eva_loss.append(epoch_eva_loss)
    
    def __call__(self, *args, **kwargs):
        self.add_record(*args, **kwargs)
    
    def __repr__(self):
        return "train_acc:{:.4f}, train_loss:{:.4f}, eva_acc:{:.4f}, eva_loss:{:4f} | best_acc:{:.4f},\
 mean_acc:{:.4f}".format(self.train_acc, self.train_loss, self.eva_acc, self.eva_loss, self.best_acc, self.mean_acc)

    def close(self):
        return
    
    def start(self):
        return

    def save(self, dir_name='.', prefix="", suffix=""):
        file_name = prefix + "{:.4f}".format(self.best_acc) + suffix
        dir_name = os.path.join(dir_name, file_name)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
            # print(f"made new {dir_name} here.")
        with open(f'{dir_name}/train_acc.pkl', 'wb') as f:
            dill.dump(self._train_acc, f)
        with open(f'{dir_name}/train_loss.pkl', 'wb') as f:
            dill.dump(self._train_loss, f)
        with open(f'{dir_name}/eva_acc.pkl', 'wb') as f:
            dill.dump(self._eva_acc, f)
        with open(f'{dir_name}/eva_loss.pkl', 'wb') as f:
            dill.dump(self._eva_loss, f)
        ans = {'mean_acc': self.mean_acc,
                'best_acc': self.best_acc}
        with open('{}/{:.4f}.json'.format(dir_name, self.best_acc), 'w') as f:
            json.dump(ans, f)
    
    def EarlyStopping(self, monitor='acc', min_delta=0.01, patience=20, mode='max'):
        assert monitor in ['acc', 'loss'], "your monitor is not right"
        assert mode in ['min', 'max'], "your stopping mode is not right"
        assert isinstance(patience, int) and patience >= 2, "patience must be int and should bigger than two"

        if monitor == 'acc':
            if len(self._eva_acc) < patience:
                return False
            else:
                check_ans = self._eva_acc[-patience:]
        elif monitor == 'loss':
            if len(self._eva_loss) < patience:
                return False
            else:
                check_ans = self._eva_loss[-patience:]
        
        # 获取patience列表中前半和后半的数
        middle = patience // 2
        front_ans = check_ans[:middle]
        rear_ans = check_ans[middle:]
        # 早停的逻辑是：前半结果的极值和后半结果的极值的差值小于min_delta
        if mode == 'max' and (np.max(rear_ans) - np.min(front_ans)) <= min_delta:
                return True
        elif mode == 'min' and (np.max(front_ans) - np.min(rear_ans)) <= min_delta:
            return True
        return False

class TensorBoardSaver(MetricSaverBase):
    def __init__(self, log_dir='runs/', file_name=None, adding_attributes=None, tag='fold_0'):
        super(TensorBoardSaver, self).__init__(adding_attributes)
        self.timestamp = time.strftime('%Y%m%d-%H_%M_%S', time.localtime(time.time()))
        if file_name == None:
            file_name = self.timestamp
        self.dir_name = os.path.join(log_dir, file_name)
        # self.writer = SummaryWriter(dir_name)
        self.tag = tag
    
    def start(self):
        self.writer = SummaryWriter(self.dir_name)

    def add_record(self, epoch_train_acc, epoch_train_loss, epoch_eva_acc=None, epoch_eva_loss=None):
        super().add_record(epoch_train_acc, epoch_train_loss, epoch_eva_acc, epoch_eva_loss)
        tag = self.tag
        # self.writer.add_scalars("train_acc", {tag: epoch_train_acc}, len(self._train_acc))
        # self.writer.add_scalars("train_loss", {tag: epoch_train_loss}, len(self._train_loss))
        # if epoch_eva_acc is not None:
        #     self.writer.add_scalars("eva_acc", {tag: epoch_eva_acc}, len(self._eva_acc))
        # if epoch_eva_loss is not None:
        #     self.writer.add_scalars("eva_loss", {tag: epoch_eva_loss}, len(self._eva_loss))

        # self.writer.add_scalar("train_acc", epoch_train_acc, len(self._train_acc)-1)
        # self.writer.add_scalar("train_loss", epoch_train_loss, len(self._train_loss)-1)
        # if epoch_eva_acc is not None:
        #     self.writer.add_scalar("eva_acc", epoch_eva_acc, len(self._eva_acc)-1)
        # if epoch_eva_loss is not None:
        #     self.writer.add_scalar("eva_loss", epoch_eva_loss, len(self._eva_loss)-1)

        self.writer.add_scalar(f"train_acc/train_acc_{tag}", epoch_train_acc, len(self._train_acc)-1)
        self.writer.add_scalar(f"train_loss/train_loss_{tag}", epoch_train_loss, len(self._train_loss)-1)
        if epoch_eva_acc is not None:
            self.writer.add_scalar(f"eva_acc/eva_acc_{tag}", epoch_eva_acc, len(self._eva_acc)-1)
        if epoch_eva_loss is not None:
            self.writer.add_scalar(f"eva_loss/eva_loss_{tag}", epoch_eva_loss, len(self._eva_loss)-1)
    
    def close(self):
        self.writer.close()

class FoldMetricBase(object):
    def __init__(self,  k_fold=10, saver=MetricSaverBase, dir_name='.', file_name='fold_test', timestamp=True, suffix=None, adding_attributes=None):
        # super(self, FoldMetricBase).__init__(adding_attributes)
        self._fold_metric_saver = []
        self._cur_k = 0
        self._fold_acc = []
        self._k_fold = k_fold

        self.timestamp = time.strftime('%Y%m%d-%H_%M_%S', time.localtime(time.time()))
        self.file_name = file_name
        self.suffix = suffix
        self.dir_name = dir_name

        # self._base_saver = saver(adding_attributes)
        for k in range(k_fold):
            # self._fold_metric_saver.append(copy.deepcopy(self._base_saver))
            assert saver.__name__ in ['TensorBoardSaver', 'MetricSaverBase'], "your saver is not register in the FoldMetricBase, check the version or your spell"
            if saver.__name__ == 'TensorBoardSaver':
                self._fold_metric_saver.append(saver(log_dir=os.path.join(dir_name, file_name, 'runs'), file_name=self.timestamp, tag=f'fold_{k}'))
                if k == 0:
                    self._fold_metric_saver[0].start()
            elif saver.__name__ == 'MetricSaverBase':
                self._fold_metric_saver.append(saver(adding_attributes=adding_attributes))
    
    def gen_path(self, dir_name, file_name, timestamp, suffix):
        if timestamp:
            # _time = time.strftime('%Y%m%d-%H:%M:%S', time.localtime(time.time()))
            _time = self.timestamp
        else:
            _time = ""

        if suffix is None:
            suffix = '{:.4f}'.format(self.mean_acc)

        dir_name = os.path.join(dir_name, file_name, file_name+'-'+suffix+'-'+_time)
        return dir_name

    @property    
    def mean_acc(self):
        if len(self._fold_acc) == 0:
            return 0.00
        else:
            return np.mean(self._fold_acc)
    
    @property
    def cur_k(self):
        return min(len(self._fold_acc), self._cur_k)
    
    @property
    def std(self):
        if len(self._fold_acc) == 0:
            return 0.00
        else:
            return np.std(self._fold_acc)
    
    @property
    def cur_saver(self):
        return self._fold_metric_saver[self._cur_k]
    
    @property
    def best_acc(self):
        if len(self._fold_acc) == 0:
            return 0.00
        else:
            return np.max(self._fold_acc)
    
    def next_fold(self):
        self._fold_metric_saver[self._cur_k].close()
        self._fold_acc.append(self._fold_metric_saver[self._cur_k].best_acc)
        if self._cur_k + 1 >= self._k_fold:
            return
        # 保存当前fold的acc
        # 指向当前fold的指针加1
        self._cur_k += 1
        self._fold_metric_saver[self._cur_k].start()
        # 若运行时制定的fold大于init时指定的fold，增加metric_saver的数量以使得两者匹配，防止因为metricsaver的错误导致程序的中断
        # if self._cur_k >= self._k_fold:
        #     self._k_fold = self._cur_k + 1
        # for i in range(self.cur_k, self._k_fold):
        #     self._fold_metric_saver.append(copy.deepcopy(self._base_saver))
    
    def add_record(self, *args, **kwargs):
        self._fold_metric_saver[self._cur_k].add_record(*args, **kwargs)
    
    def __call__(self, *args, **kwargs):
        self.add_record(*args, **kwargs)
    
    def EarlyStopping(self, *args, **kwargs):
        return self.cur_saver.EarlyStopping(*args, **kwargs)
    
    def save(self):
        dir_name = self.gen_path(self.dir_name, self.file_name, self.timestamp, self.suffix)
        for i in range(self._k_fold):
            self._fold_metric_saver[i].save(dir_name, prefix=f'fold_{i}: ')
        ans = {
           'mean_acc': self.mean_acc,
           'std': self.std,
           'list': self._fold_acc
        }
        with open('{}/{:.4f}.json'.format(dir_name, self.mean_acc), 'w') as f:
            json.dump(ans, f)
        return 'save to {dir_name}'

    def __repr__(self):
        return f"Fold:{self._cur_k}/{self._k_fold} ||" + self._fold_metric_saver[self._cur_k].__repr__() + " || fold_mean_acc:{:.4f}, fold_best_acc:{:.4f}".format(self.mean_acc, self.best_acc)

if __name__ == "__main__":
    # a = MetricBase(adding_attributes=['x'])
    # fold = 10
    fold = 10
    # b = FoldMetricBase(k_fold=fold, adding_attributes=['x'])
    b = FoldMetricBase(k_fold=fold, saver=TensorBoardSaver, dir_name='test_fold', file_name='test_tensorboard', adding_attributes=['x'])
    for _ in range(fold):
        for i in range(100):
            _a, _b, _c, _d = np.random.rand(4)
            b(_a, _b, _c, _d)
            # time.sleep(0.1)
            if b.EarlyStopping(patience=6, min_delta=0.1):
                print(_, i, 'continue !!!')
                break
        b.next_fold()
    b.save()

