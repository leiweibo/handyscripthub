# -*- coding: utf-8 -*- 
import  xdrlib ,sys
import xlrd
def open_excel(file= 'file.xls'):
    try:
        data = xlrd.open_workbook(file)
        return data
    except Exception,e:
        print str(e)
#根据索引获取Excel表格中的数据   参数:file：Excel文件路径     colnameindex：表头列名所在行的所以  ，by_index：表的索引
def excel_table_byindex(file= '20170118.xls',colnameindex=0,by_index=0):
    data = open_excel(file)
    table = data.sheets()[by_index]
    nrows = table.nrows #行数
    ncols = table.ncols #列数
    colnames =  table.row_values(colnameindex) #某一行数据 
    list =[]
    for rownum in range(1,nrows):

         event_id = ''
         event_desc = ''

         row = table.row_values(rownum)
         if row:
             app = {}
             for i in range(len(colnames)):
                app[colnames[i]] = row[i].encode('utf_8')
                if i == 0:
                    event_desc = row[i].encode('utf_8')
                elif i == 2:
                    event_id = row[i].encode('utf_8')
             list.append(app)
             if event_id != '' and event_desc != '':
                print 'public static final String ' + event_id.upper() + '[] = ' + '{ "' + event_id + '"' + ', ' + '"' + event_desc + '" };'
    return list

# #根据名称获取Excel表格中的数据   参数:file：Excel文件路径     colnameindex：表头列名所在行的所以  ，by_name：Sheet1名称
# def excel_table_byname(file= '20170118.xls',colnameindex=0,by_name=u'交易'):
#     data = open_excel(file)
#     table = data.sheet_by_name(by_name)
#     nrows = table.nrows #行数 
#     colnames =  table.row_values(colnameindex) #某一行数据 
#     list =[]
#     for rownum in range(1,nrows):
#          event_id = ''
#          event_desc = ''

#          row = table.row_values(rownum)
#          if row:
#              app = {}
#              for i in range(len(colnames)):
#                 app[colnames[i]] = row[i].encode('utf_8')
#                 if i == 0:
#                     event_desc = row[i].encode('utf_8')
#                 elif i == 2:
#                     event_id = row[i].encode('utf_8')
#              list.append(app)
#              if event_id != '' and event_desc != '':
#                 print 'public static final String ' + event_id.upper() + '[] = ' + '{ "' + event_id + '"' + ', ' + '"' + event_desc + '" };'
#     return list

def main():
    # tables = excel_table_byindex()
    # for row in tables:
    #     print row
    
    for num in range(1,9):
        excel_table_byindex(by_index=num)

   # for row in tables:
   #     print row

if __name__=="__main__":
    main()