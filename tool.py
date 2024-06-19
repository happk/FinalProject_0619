## Year的類別
# 方便跨年份的計算
from functools import total_ordering
@total_ordering
class YearMonth:
    # 定義一個初始化方法，接受一個年份和一個月份
    def __init__(self, year, month):
        # 檢查年份和月份是否合法，如果不合法，拋出異常
        if not isinstance(year, int) or not isinstance(month, int):
            raise TypeError("year and month must be integers")
        if not 1 <= month <= 12:
            raise ValueError("month must be between 1 and 12")
        # 把年份和月份設置為屬性
        self.year = year
        self.month = month
        
    def __int__(self):
        return self.year * 12 + self.month

    # 定義一個__str__方法，讓它只顯示年份和月份
    def __str__(self):
        return f"{self.year}{self.month:02d}"

    # 定義一個__add_or_sub__方法，讓它可以支持加法和減法運算
    def __add_or_sub__(self, other, sign):
        # 檢查另一個對象是否是一個整數或一個YearMonth對象，如果不是，拋出異常
        if not isinstance(other, (int, YearMonth)):
            raise TypeError(f"can only {sign:+} an integer or a YearMonth to/from a YearMonth")
        # 如果另一個對象是一個YearMonth對象，就把它轉換成月份數
        if isinstance(other, YearMonth):
            other = other.to_month()
        # 把另一個對象視為月份數，並根據符號決定是增加還是減少自己的月份數，得到新的月份數
        new_month = self.to_month() + (sign * other)
        # 用除法和取餘數的方法，把新的月份數轉換成年份和月份
        new_year, new_month = divmod(new_month - 1, 12)
        # 創建一個新的年月對象，並返回它
        return YearMonth(new_year, new_month + 1)

    # 定義一個__add__方法，讓它調用__add_or_sub__方法
    def __add__(self, other):
        return self.__add_or_sub__(other, 1)

    # 定義一個__sub__方法，讓它調用__add_or_sub__方法
    def __sub__(self, other):
        return self.__add_or_sub__(other, -1)
    
    # 定義等於操作符 ==
    def __eq__(self, other):
        if not isinstance(other, YearMonth):
            raise TypeError("can only compare YearMonth with YearMonth")
        return self.to_month() == other.to_month()
    
    # 定義小於操作符 <
    def __lt__(self, other):
        if not isinstance(other, YearMonth):
            raise TypeError("can only compare YearMonth with YearMonth")
        return self.to_month() < other.to_month()

    # 定義一個to_month方法，讓它可以返回自己的月份數
    def to_month(self):
        # 用年份乘以12，再加上月份，得到月份數
        return int(self.year * 12 + self.month)

## YearMonth的迭代器
# 定義一個函數，接受兩個YearMonth對象，返回一個YearMonth對象列表
def yearmonth_range(start, end):
    # 確保 start 和 end 是 YearMonth 對象
    if not isinstance(start, YearMonth) or not isinstance(end, YearMonth):
        raise TypeError("start and end must be YearMonth objects")
    current = start
    while current <= end:
        yield current
        # 使用自定義的 __add__ 方法，將 current 增加一個月
        current = current + 1 

## 優雅的輸出紀錄器v1.5
import sys
import traceback
from datetime import datetime

class DualWriter:
    def __init__(self, file_name, mode='a', timestamp=False):
        self.file_name = file_name
        self.mode = mode
        self.timestamp = timestamp
        self.file = None
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        self.at_start_of_line = True

    def __enter__(self):
        self.file = open(self.file_name, self.mode)
        sys.stdout = self
        sys.stderr = self
        return self

    def __exit__(self, exc_type, exc_value, tb):
        if exc_type is not None:
            self.handle_exception(exc_type, exc_value, tb)
        sys.stdout = self.original_stdout
        sys.stderr = self.original_stderr
        if self.file:
            self.file.close()

    def write(self, message):
        if self.timestamp and self.at_start_of_line:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            padding = ' ' * (len(timestamp) + 3)
            message = message.replace('\n', '\n' + padding)
            message = f"{timestamp} - {message}"
        try:
            self.original_stdout.write(message)
            if self.file:
                self.file.write(message)
                self.file.flush()
        except Exception as e:
            self.handle_exception(type(e), e, e.__traceback__)
        finally:
            self.at_start_of_line = message.endswith('\n')

    def handle_exception(self, exc_type, exc_value, tb):
        error_message = ''.join(traceback.format_exception(exc_type, exc_value, tb))
        if self.timestamp:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            error_message = f"{timestamp} - {error_message}"
        self.original_stderr.write(error_message)
        if self.file:
            self.file.write(error_message)
            self.file.flush()

    def flush(self):
        self.original_stdout.flush()
        self.original_stderr.flush()
        if self.file:
            self.file.flush()


## 生成文件名
import os
from datetime import datetime
def generate_file_name(file_name, check_path="."):
    """
    生成唯一的文件名。

    Parameters:
    - file_name (str): 文件名的格式，将在日期后加上计数器。
    - check_path (str, optional): 检查文件存在性的路径，默认为当前工作目录。

    Returns:
    str: 生成的文件路径。
    """
    
    # 獲取當前日期
    today = datetime.now().strftime("%y%m%d")
    # 設置計數器
    counter = 1

    # 文件明格式：當前日期_xxx_文件序號.txt
    file_name_format = f"{today}-{file_name}-{counter}"
    file_path = os.path.join(check_path, file_name_format)
    
    # 檢查文件是否存在，若存在則更改文件序號 +1
    while os.path.exists(file_path):
        counter += 1
        file_name_format = f"{today}-{file_name}-{counter}"
        file_path = os.path.join(check_path, file_name_format)

    return file_path