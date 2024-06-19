import numpy as np
import pandas as pd
from tool import YearMonth,yearmonth_range
from textdistance import levenshtein

amino_acids_dict = {
    'A': 0,  # 丙氨酸
    'R': 1,  # 精氨酸
    'N': 2,  # 天門冬氨酸
    'D': 3,  # 天冬氨酸
    'C': 4,  # 半胱氨酸
    'E': 5,  # 谷氨酸
    'Q': 6,  # 谷氨酰胺
    'G': 7,  # 甘氨酸
    'H': 8,  # 組氨酸
    'I': 9,  # 異亮氨酸
    'L': 10, # 亮氨酸
    'K': 11, # 賴氨酸
    'M': 12, # 蛋氨酸
    'F': 13, # 苯丙氨酸
    'P': 14, # 脯氨酸
    'S': 15, # 絲氨酸
    'T': 16, # 蘇氨酸
    'W': 17, # 色氨酸
    'Y': 18, # 酪氨酸
    'V': 19, # 纈氨酸
    '': 20   # 空白字符
}

class ProEvoEnv():
    def __init__(self, init_sequence, dataset, ym_start, ym_end):
        self.sequence = init_sequence
        self.dataset = dataset
        self.ym_start = ym_start
        self.ym_end = ym_end
        self.ym = ym_start
        
        self.step = 0
        
    def mutate_sequence(self, operations_index, mutation_positions_index, amino_acid_index):
            amino_acid = list(amino_acids_dict.keys())[amino_acid_index]
            if mutation_positions_index > len(self.sequence):
                mutation_positions_index = len(self.sequence)-1
            
            if operations_index == 0:   # 插入
                self.sequence = self.sequence[:mutation_positions_index] + amino_acid + self.sequence[mutation_positions_index:]
            elif operations_index == 1: # 刪除
                self.sequence = self.sequence[:mutation_positions_index] + self.sequence[mutation_positions_index+1:]
            elif operations_index == 2: # 替換
                self.sequence = self.sequence[:mutation_positions_index] + amino_acid + self.sequence[mutation_positions_index+1:]
                
    def sequence_to_onehot(self, max_length=1275):
        sequence = self.sequence
        # 確保序列長度不超過 max_length
        sequence = sequence[:max_length]
        # 若序列長度不足 max_length，則在後面以0填充
        padded_sequence = sequence + (' ' * (max_length - len(sequence)))
        # 創建一個零矩陣
        one_hot = np.zeros((max_length, len(amino_acids_dict)), dtype=int)
        for i, amino_acid in enumerate(padded_sequence):
            one_hot[i, amino_acids_dict.get(amino_acid, 0)] = 1
        return one_hot
    
    def sequence_to_index(self, max_length=1275):
        sequence = self.sequence
        # 確保序列長度不超過 max_length
        sequence = sequence[:max_length]
        # 若序列長度不足 max_length，則在後面以0填充
        padded_sequence = sequence + (' ' * (max_length - len(sequence)))
        list = [amino_acids_dict.get(amino_acid, 0) for amino_acid in padded_sequence]
        
        return np.array(list) 
        
    def state_now(self):
        ym_now = self.ym
        dataset = self.dataset
        
        dataset_now = dataset[dataset['year']*12 + dataset['month'] == ym_now.to_month()]
        feature_now = dataset_now[['f{}'.format(i) for i in range(35)]].to_numpy()
        feature_now_mean = feature_now.mean(axis=0)
        
        return feature_now_mean
    
    def state_last(self):
        ym = self.ym - 1
        dataset = self.dataset
        
        dataset_last = dataset[dataset['year']*12 + dataset['month'] == ym.to_month()]
        if dataset_last.empty:
            return np.zeros(35)
        feature_last = dataset_last[['f{}'.format(i) for i in range(35)]].to_numpy()
        
        return feature_last.mean(axis=0)
    
    def state(self):
        return np.concatenate([self.state_now(), self.state_last()])
    
    def get_reward(self):
            ym_now = self.ym
            ym_next = ym_now + 1
            dataset = self.dataset
            sequence = self.sequence

            dataset_next = dataset[(dataset['year'] * 12 + dataset['month']) == ym_next.to_month()]
            sequence_next = dataset_next['sequence'].to_list()

            # 計算粗略相似性
            similarity_scores = [sum(a == b for a, b in zip(sequence, seq_next)) for seq_next in sequence_next]
            max_similarity = max(similarity_scores)

            # 找到最相近序列的索引
            closest_indices = [i for i, score in enumerate(similarity_scores) if score == max_similarity]

            # 計算最相近序列的 Levenshtein Distance
            ld_values = [levenshtein(sequence, sequence_next[i]) for i in closest_indices]
            ld_min = min(ld_values)

            score = 0
            next = False
            
            # 根據 ld_min 設置 score
            
            if ld_min == 0:
                if ym_next == self.ym_end:
                    score = 500
                    next = True
                else:
                    score = 50
                    next = True
                
            elif ld_min <= 2:
                if ym_next == self.ym_end:
                    score = 100
                    next = True
                else:
                    score = 5
                    next = True
            elif ld_min <= 5:
                score = -1
            elif ld_min <= 10:
                score = -3
            else:
                score = -10
                
            return score, ld_min, next
    
    def go_next(self):
        if self.ym < self.ym_end-1:
            self.ym += 1
            self.step += 1
            return False # 表示還沒結束
        else:
            return True # 表示已經結束，且不往下一步                
    
    def reset(self, init_sequence):
        self.ym = self.ym_start
        self.step = 0
        self.sequence = init_sequence
        return 
            
            

    # def get_reward(self):
    #     ym_now = self.ym
    #     ym_next = ym_now + 1
    #     dataset = self.dataset
    #     sequence = self.sequence
        
    #     dataset_next = dataset[dataset['year']*12 + dataset['month'] == ym_next.to_month()]
        
    #     sequence_next = dataset_next['sequence'].to_list()
        
    #     ld_list = [levenshtein(sequence, sequence_next) for sequence_next in sequence_next]
    #     ld_min = min(ld_list)
        
    #     # 根據 ld_min 設置 score
    #     if ld_min == 0:
    #         score = 50
    #     elif ld_min < 3:
    #         score = 5
    #     elif ld_min < 10:
    #         score = -1
    #     else:
    #         score = -10
            
    #     return score, ld_min
    