import cx_Oracle
import configparser


def getConnect():
    ''' 根据配置 config/database.conf 连接数据库

        :param con: 数据库连接会话
        :param cur: 游标
    '''
    cf = configparser.ConfigParser()
    cf.read("config/database.conf")
    db_name = cf.get("db", "db_name")
    db_pw = cf.get("db", "db_pw")
    db_host = cf.get("db", "db_host")
    con = cx_Oracle.connect(db_name, db_pw, db_host)
    cur = con.cursor()
    return con, cur


def add_task_log(model, task, tp, fp, tn, fn):
    ''' 将训练结果或测试结果写入数据库的log表中

        :param model: 模型名称
        :param task: 任务，“训练”或“测试”
        :param tp: 实际为真，预测为真的个数
        :param fp: 实际为假，预测为真的个数
        :param tn: 实际为真，预测为假的个数
        :param fn: 实际为假，预测为假的个数
    '''
    cf = configparser.ConfigParser()
    cf.read("config/database.conf")
    log_table =cf.get("log", "log_table")
    log_model =cf.get("log", "log_model")
    log_task = cf.get("log", "log_task")
    log_total = cf.get("log", "log_total")
    log_tp = cf.get("log", "log_tp")
    log_fp = cf.get("log", "log_fp")
    log_tn = cf.get("log", "log_tn")
    log_fn = cf.get("log", "log_fn")
    con, cur = getConnect()

    sql = "INSERT INTO " + repr(log_table) + "( " + repr(log_model) + ", " + "," + repr(log_task) \
            + "," + repr(log_total) + "," + repr(log_tp) + ", " + repr(log_fp) + "," + repr(log_tn) \
            + "," + repr(log_fn) + ") VALUES ({},{},{},{},{},{},{});". \
            format(repr(model), repr(task), repr(tp+fp+tn+fn), repr(tp), repr(fp), repr(tn), repr(fn))

    try:
        cur.execute(sql)
        con.commit()
    except Exception as e:
        con.rollback()
        print(e)
    cur.close()
    con.close()
