
from Feature.pre_process_data import process_data
def DecisionTree(X, y):
    # y_cls = data[['zhangdie']].shift(-1)
    # from sklearn.model_selection import train_test_split
    # X_cls_train, X_cls_test, y_cls_train, y_cls_test = train_test_split(X, y, test_size=0.3, random_state=432, stratify=y)
    X_cls_train = X.iloc[:int(len(X)//10*10) ,:].fillna(0)
    X_cls_test = X.iloc[int(len(X)//10*7): ,:].fillna(0)
    # X_cls_train = X.iloc[:int(len(X)//10*7) ,:].fillna(0)
    # X_cls_test = X.iloc[int(len(X)//10*7): ,:].fillna(0)
    y_cls_train = y[:int(len(y)//10*10)].shift(-1).fillna(0)
    y_cls_test = y[int(len(y)//10*7):].shift(-1).fillna(0)

    print (X_cls_train.shape, y_cls_train.shape)
    print (X_cls_test.shape, y_cls_test.shape)

    from sklearn.tree import DecisionTreeClassifier
    clf = DecisionTreeClassifier(criterion='gini', max_depth=3, min_samples_leaf=6)
    clf = clf.fit(X_cls_train, y_cls_train)
    y_cls_pred = clf.predict(X_cls_test)
    right = 0
    error = 0
    for i in range(len(y_cls_test)):
        if y_cls_pred[i] == y_cls_test.tolist()[i]:
            right += 1
        else:
            error += 1
    print("准确率：%s"%round(right/(right + error), 4))

if __name__ == '__main__':
    X, y = process_data(type='C')
    DecisionTree(X, y)