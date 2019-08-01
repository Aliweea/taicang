import cx_Oracle
import numpy as np
import pandas as pd
import csv
import configparser
import sys
import itertools

from sklearn import tree
from imblearn.over_sampling import SMOTE
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import GradientBoostingClassifier 
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split


sys.path.append("..")

from db.database import *


def get_data_form_database():
    ''' 从数据库获取训练数据和测试数据 
    
    :return train_data: 执行sqltrain得到的数据
    :return test_data: 执行sqltest得到的数据

    注意，train_data与test_data的字段相同
    '''
    con, cur = getConnect()
    
    cf = configparser.ConfigParser()
    cf.read("config/model_rent.conf")
    db_columns = cf.get("db", "db_columns")
    db_sqltrain = cf.get("db", "db_sqltrain")
    db_sqltest = cf.get("db", "db_sqltest")
    
    columns = db_columns.split(',')
    sqltrain= db_sqltrain
    sqltest=db_sqltest

    cur.execute(sqltrain)
    rows = cur.fetchall()
    rows = np.array(rows)
    rows = np.nan_to_num(rows)
    train_data = pd.DataFrame(rows, columns=columns)

    cur.execute(sqltest)
    rows = cur.fetchall()
    rows = np.array(rows)
    rows = np.nan_to_num(rows)
    test_data = pd.DataFrame(rows, columns=columns)

    cur.close()
    con.close()

    return train_data, test_data


def workout(rows):
    ''' 处理数据，删除含有字母的行

    :param rows: 需要处理的数据，格式为DataFrame

    :return rows: 处理好的数据，格式为DataFrame
    '''
    rows.dropna()
    length = len(rows)
    i = 0

    def fun_isdigit(aString):
        try:
            _ = float(aString)
            return True
        except ValueError:
            return False

    while (i < length - 1):
        check = True
        str_data = str(rows.iloc[i][1])
        if (fun_isdigit(str_data) == False):
            print(str_data)
            check = False
        str_data = str(rows.iloc[i][2])
        if (fun_isdigit(str_data) == False):
            print(str_data)
            check = False
        str_data = str(rows.iloc[i][4])
        if (fun_isdigit(str_data) == False):
            print(str_data)
            check = False
        str_data = str(rows.iloc[i][5])
        if (fun_isdigit(str_data) == False):
            print(str_data)
            check = False
        str_data = str(rows.iloc[i][6])
        if (fun_isdigit(str_data) == False):
            print(str_data)
            check = False
        if (rows.iloc[i][7] == None):
            rows.iloc[i][7] = 0
        if (check):
            i += 1
        else:
            rows = rows.drop(rows.index[i])
            length = length - 1

    rows = rows.drop(['Unnamed: 0'], axis=1)
    return rows


def accuracy_metric(actual, predicted):
    ''' 计算准确度矩阵, 即tp,fp,tn,fn

    :param actual: 实际样本
    :prarm predicted: 预测样本

    :return tp: 实际为真，预测为真的个数
    :return fp: 实际为假，预测为真的个数
    :return tn: 实际为真，预测为假的个数
    :return fn: 实际为假，预测为假的个数
    '''
    n = len(actual)
    correct = 0
    tp=0
    tn=0
    fp=0
    fn=0
    for i in range(n):
        if actual[i] == predicted[i]:
            correct += 1
            if(actual[i] == 1):
                tp = tp + 1
            else:
                fp = fp + 1
        else:
            if (actual[i] == 1):
                tn = tn + 1
            else:
                fn = fn + 1
    return tp, tn, fp, fn


def fit(model, data, feature_columns=None, label_column="Class"):
    ''' 训练模型，并把训练记录插入数据库

        :param model: 模型名称，当前可选项为 'RF'(随机森林),'DT'(决策树),'GBDT'(梯度决策树),'SVM'(支持向量机), 选择不在其中则为'DT'
        :param data: 训练数据，包含特征和标签，数据格式为DataFrame
        :param features: 特征，格式为list，为None时表示data除label_column以外的所有列
        :param label: 标签，格式为string

        :return clf: 训练好的模型
    '''
    data = data.dropna()
    columns = data.columns.values.tolist()
    if feature_columns is None:
        feature_columns = columns.remove(label_column)

    features = data[feature_columns]
    label = data[label_column]
    
    train_feature, test_feature, train_label, test_label = \
        train_test_split(features, label, test_size=0.2)
    
    oversampler = SMOTE(random_state=0)
    os_features, os_label = oversampler.fit_sample(train_feature, train_label)
    os_features = pd.DataFrame(os_features)
    os_label = pd.DataFrame(os_label)

    if model == 'RF':
        clf = RandomForestClassifier(n_estimators=8)
    elif model == 'DT':
        clf = tree.DecisionTreeClassifier(criterion='entropy')
    elif model == 'GBDT':
        clf = GradientBoostingClassifier(n_estimators=200)
    elif model == 'SVM':
        clf = SVC(kernel='rbf', probability=True)
    else:
        clf = tree.DecisionTreeClassifier(criterion='entropy')

    clf.fit(os_features, os_label.values.ravel())

    pred_label = clf.predict(test_feature)
    test_label = test_label.reshape(-1)
    tp, tn, fp, fn = accuracy_metric(test_label, pred_label)
    # 把训练记录插入数据库
    add_task_log(model, "训练", tp, fp, tn, fn)
    return clf


def predict(model, clf, data, ID_column="ID", feature_columns=None, label_column="Class"):
    ''' 用模型预测，并把结果更新到数据库

        :param model: 模型名称
        :param clf: 训练好的模型，拥有predict(features_data)函数
        :param data: 要预测的数据，包含ID、特征和标签，数据格式为DataFrame
        :param ID_column: data中ID列的名称，格式为string
        :param feature_columns: 特征，格式为list，为None时表示data除ID_column、label_column以外的所有列
        :param label_column: 标签，格式为string
    '''
    data = data.dropna()
    columns = data.columns.values.tolist()
    if feature_columns is None:
        feature_columns = columns.remove(ID_column).remove(label_column)

    data_id = data[ID_column]
    features = data[feature_columns]
    label = data[label_column]

    pred_label = clf.predict(features)
    label = label.reshape(-1)
    tp, tn, fp, fn = accuracy_metric(label, pred_label)
    add_task_log(model, "测试", tp, fp, tn, fn)

    for i in range(0, len(data_id)):
        updata_test_label(data_id[i], pred_label[i])


# 写入测试结果0/1
def updata_test_label(t_id, t_label):
    con, cur = getConnect()

    cf = configparser.ConfigParser()
    cf.read("config/model_rent.conf")
    db_test_table =cf.get("db", "db_test_table")
    db_test_label =cf.get("db", "db_test_label")
    db_id =cf.get("db", "db_test_id")

    # sql = "UPDATE " + repr(db_test_table)+" SET "+ repr(db_test_label) + " = " + repr(t_label) + \
    #         " WHERE "+ repr(db_id) + " = " + repr(t_id)

    sql = "INSERT INTO " + repr(db_test_table) + " ( "+ repr(db_test_label) + " ) VALUES ({}); ".format(repr(t_label)) 

    try:
        cur.execute(sql)
        con.commit()
    except Exception as e:
        con.rollback()
        print(e)
    cur.close()


# 入口
def model_rent(model):
    ''' 训练模型并输出训练结果到数据库

    :param model: 模型名称，当前可选项为 'RF'(随机森林),'DT'(决策树),'GBDT'(梯度决策树),'SVM'(支持向量机), 选择不在其中则为'DT'
    '''
    train_data, test_data = get_data_form_database()
    # train_data = workout(train_data) # 可不需要（若数据无字母）

    cf = configparser.ConfigParser()
    cf.read("config/model_rent.conf")
    db_columns = cf.get("db", "db_columns")
    columns = db_columns.split(',')
    ID = columns[0]
    label = columns[len(columns)-1]
    features = columns.remove(ID).remove(label)

    clf = fit(model, train_data, feature_columns=features, label_column=label)
    predict(model, clf, test_data, ID_column=ID, feature_columns=features, label_column=label)


if __name__ == "__main__":
    if (len(sys.argv) < 1):
        model = 'DT'
    else:
        model = sys.argv[1]
    model_rent(model)