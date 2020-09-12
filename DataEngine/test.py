from DataEngine.Data import *
from DataEngine.Mysql import *

if __name__ == '__main__':
    print(get_all_columns_with_label(['open','close'], ['601607']))