import subprocess
import pandas as pd
import os

# import remove_sequences_with_X

methods = ['pse.py','acc.py','nac.py']
encodes_pse = ["PC-PseAAC","SC-PseAAC","PC-PseAAC-General","SC-PseAAC-General"]
encodes_acc = ["AC","CC","ACC",]    # "PDT"不被接受 <-報錯: Error: the protein method parameter can only be ['AC', 'CC', 'ACC']
encodes_nac = ["Kmer","DR","DP"]
cps = ["cp_13", "cp_14", "cp_19"]
#輸入路徑
est_1500 = "C:/Downloads/Pse-in-One-2.0/mydata/est_1500c.mfa" # 脂肪酶 (酯鍵酶) 的序列 (挑出1500筆)
pep_1500 = "C:/Downloads/Pse-in-One-2.0/mydata/pep_1500c.mfa" # 蛋白酶 (胜肽鍵酶) 的序列 (挑出1500筆).
# 輸出路徑 >> 之後要修改為寫在函數內，由調用的原始資料位置決定
output_folder = "C:/Downloads/Pse-in-One-2.0/mydata/output"
#pse-in-one路徑
pse_folder = "C:/Downloads/Pse-in-One-2.0"
# 虛擬環境路徑
venv = os.environ.copy()
venv["PATH"] = "C:/Downloads/Pse-in-One-2.0/venv;" + venv["PATH"]

venv_python = "C:/Downloads/Pse-in-One-2.0/venv/python.exe"

# def merge_csv(csv1, csv2, output_folder):
#     # 取得csv檔案名(不含副檔名)
#     name_csv1 = os.path.splitext(os.path.basename(csv1))[0]
#     name_csv2 = os.path.splitext(os.path.basename(csv2))[0]
#     # input_folder = os.path.dirname(input)

#     # 讀取CSV檔案
#     csv1 = pd.read_csv(csv1, header=None)
#     csv2 = pd.read_csv(csv2, header=None)

#     # 為兩個資料集添加標記（1或0）
#     csv1.insert(0, 'Label', 1)
#     csv2.insert(0, 'Label', 0)

#     # 合併兩個資料集
#     merged_csv = pd.concat([csv1, csv2], ignore_index=True)

#     # 寫入合併後的CSV檔案
#     output = f'{output_folder}/merge_{name_csv1}_{name_csv2}.csv'
#     merged_csv.to_csv(output, header=False, index=False)
#     return output 

def merge_csv(csv1, csv2, label='',output_folder=[]):
    # 取得csv檔案名(不含副檔名)
    name_csv1 = os.path.splitext(os.path.basename(csv1))[0]
    name_csv2 = os.path.splitext(os.path.basename(csv2))[0]

    # 如果輸出資料夾不指定，則設定為csv1的資料夾
    if output_folder == []:
        output_folder = os.path.dirname(csv1)
        os.makedirs(output_folder, exist_ok=True)

    # 讀取CSV檔案
    csv1 = pd.read_csv(csv1, header=None)
    csv2 = pd.read_csv(csv2, header=None)

    # 合併兩個資料集
    merged_csv = pd.concat([csv1, csv2], ignore_index=True,axis=1)

    # 為這個特徵組合添加label
    if not label:
        pass    # 如果沒有指定label，則不添加 
    else:
        merged_csv.insert(0, 'Label', label)

    # 寫入合併後的CSV檔案
    output = f'{output_folder}/merge_{name_csv1}_{name_csv2}.csv'
    merged_csv.to_csv(output, header=False, index=False)
    return output 

# 提取特徵值
def ExtractFeatures(input,method,encode,parameter=[],output_name=""):
    # 未輸入parameter時的預設值
    if method == 'pse.py':
        if parameter == []:
            parameter = ['-lamada','2','-w','0.1']
    elif method == 'acc.py':
        if encode == "PDT":
            if parameter == []:
                parameter = ['-lamada', '1']
        else:
            if parameter == []:
                parameter = ['-lag', '1']   # -lag 系統未有默認值，在此設定為1
    elif method == 'nac.py':
        if encode == "Kmer":
            if parameter == []:
                parameter = ['-k', '1'] # -k 系統未有默認值，在此設定為1
        elif encode == "DR":
            if parameter == []:
                parameter = ['-max_dis', '3']
        elif encode == "DP":
            if parameter == []:
                parameter = ['-max_dis', '3', '-cp', 'cp_13']    # -cp 系統未有默認值，在此設定為cp_13

    # 執行檔路徑
    PyExeFile = f'{pse_folder}/{method}'
    # 取得input檔案名(不含副檔名) 與 所在資料夾名
    input_name = os.path.splitext(os.path.basename(input))[0]
    input_folder = os.path.dirname(input)

    
    
    # 輸出檔案名
    if output_name == "":
        output_folder = f'{input_folder}/output'
        os.makedirs(output_folder, exist_ok=True)
        # 將parameter串接成字串(_分隔)
        name_parameter = '_'.join([param.lstrip('-') for param in parameter]) 
        output = f'{output_folder}/{input_name}_{method}_{encode}_{name_parameter}.csv'
    else:
        output = output_name
   
    # 執行pse-in-one
    ## stdout=subprocess.PIPE：這將子進程的標準輸出（stdout）重定向到一個管道，這意味著您可以捕獲子進程的輸出，而不是將其打印到終端。通過使用 subprocess.PIPE，您可以在Python中訪問子進程的標準輸出，並以字符串的形式獲取它。
    ## stderr=subprocess.PIPE：這將子進程的標準錯誤輸出（stderr）也重定向到一個管道，類似於 stdout=subprocess.PIPE。這允許您捕獲子進程的錯誤消息，以便在需要時進行處理。
    ## text=True：這個參數指定子進程的輸出應以文本模式處理，這意味著輸出將被解釋為字符串而不是字節。如果將 text 設置為 True，則 subprocess.run 返回的結果中的 stdout 和 stderr 屬性將包含文本字符串，而不是字節字符串。這在處理文本數據時非常有用。
    result = subprocess.run([venv_python, PyExeFile, input, output, 'Protein', encode ,'-f','csv'] + parameter,cwd=pse_folder, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        print(result.stderr)
    else:
        print(result.stdout)
    # 回傳輸出檔案路徑
    return output

# 提取2個分類 + 合併特徵值
def ExFeature_2_merge(input1,input2,method,encode,parameter=[]):
    csv1 = ExtractFeatures(input1,method,encode,parameter)
    csv2 = ExtractFeatures(input2,method,encode,parameter)
    result_name = merge_csv(csv1, csv2)

    return result_name

# main
def main():
    for method in methods:
        if method == 'pse.py':
            for encode in encodes_pse:
                ExFeature_2_merge(est_1500,pep_1500,method,encode)
        elif method == 'acc.py':
            for encode in encodes_acc:
                ExFeature_2_merge(est_1500,pep_1500,method,encode)
        elif method == 'nac.py':
            for encode in encodes_nac:
                ExFeature_2_merge(est_1500,pep_1500,method,encode)
def main2():
    for k in range(2,4):
        ExFeature_2_merge(est_1500,pep_1500,'nac.py','Kmer',['-k',str(k)])

if __name__ == '__main__':
    main2()





    
