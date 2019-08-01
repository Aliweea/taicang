# taicang_data

the data analysis project of Taicang city.


## Spider

### community
spider/community.py：爬取小区的房源、租房房源、价格等信息
config/spider_community.conf: 相应的配置文件
*调用方式：*
python community.py start end
start是起始页数，end是终止页数

### rent
spider/rent.py：爬取小区房屋的具体信息，如房屋朝向、户型、建筑年限、租金等。
config/spider_rent.conf：相应的配置文件
*调用方式：*
python rent.py start end
start是起始页数，end是终止页数

### complaint
spider/complaint.py：爬取投诉信息，没有具体要求，只是一个出版，没有配置文件。结果写入文件中。
*调用方式：*
python complaint


## Model

### rent
model/model_rent.py：从租房和非租房信息中识别租房，从租房和群租房中识别群住房。具体功能可通过配置文件改变。
config/model_rent.conf：相应的配置文件。

1、从租房和非租房信息中识别租房
db_sqltrain可以设置为
```
SELECT
	a.ID,
	a.JZWID,
	a.FWDZID,
	a.FWQK,
	a.SSPCS,
	a.SSZRQ,
	a.SSZRMJ,
	a.JZZ_PCS,
	c.MIRCODE,
	DECODE( a.FWQK, '21', 1, '22', 1, '9', 1, 0 ) CLASS 
FROM
	TB_SYFW_JBXX a
	LEFT JOIN LS_FENXI_SHUI b ON a.DZQC = b.MIADR
	LEFT JOIN CL_GDOCGXSL20190219 c ON b.MICODE = c.MICODE 
WHERE
	a.DEL_FLAG = '0' 
	AND a.SFZX = 0
```
db_sqltest 可以直接从训练数据表拿数据

2、从租房和群租房中识别群住房
db_sqltrain可以设置为
```
SELECT
	a.ID,
	a.JZWID,
	a.FWDZID,
	a.FWQK,
	a.SSPCS,
	a.SSZRQ,
	a.SSZRMJ,
	a.JZZ_PCS,
	c.MIRCODE,
    a.SFQZF 
FROM
	TB_SYFW_JBXX a
	LEFT JOIN LS_FENXI_SHUI b ON a.DZQC = b.MIADR
	LEFT JOIN CL_GDOCGXSL20190219 c ON b.MICODE = c.MICODE 
WHERE
	a.DEL_FLAG = '0' 
	AND a.SFZX = 0 
    AND a.FWQK in ('21', '22', '9') 
```
db_sqltest 可以直接从训练数据表拿数据

*调用方式：*
python model_rent.py model_name
model_name可选为'RF'(随机森林),'DT'(决策树),'GBDT'(梯度决策树),'SVM'(支持向量机), 选择不在其中则为'DT'


## References


## NOTE

- 默认使用一个数据库，其配置文件为 config/database.conf

- conf文件的格式是gbk

- 先在数据库创建需要的表，主键为自增长的ID*(当前无ID，需要后续添加)*


## 遇到的问题

### 1.ORA-12170: TNS:Connect timeout occurred

解决过程：确认数据库连接配置正确

### 2.ORA-00911: invalid character

解决过程：
1.查看拼接的sql，确认sql正确无误，字符串要用单引号，数字无引号。
2.sql语句是否有分号。
3.如存在中文则可能是编码问题。
