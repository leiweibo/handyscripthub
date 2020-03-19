import openpyxl
import re


def read_excel_data(file_name):
    wb = openpyxl.load_workbook(file_name)
    sheet = wb.get_sheet_by_name('协议明细')
    key_col = 5
    value_col = 6
    result = {}
    for row in sheet.rows:
        content_str = ''
        if row[value_col].value and 'decimal' in row[value_col].value.lower():
            datas = re.compile('DECIMAL\((\d*),(\d*)\)').findall(row[value_col].value)
            print(row[key_col].value)
            if len(datas) > 0 and len(datas[0]) >= 2:
                result[row[key_col].value.strip()] = datas
            content_str += f'{row[key_col].value}: {row[value_col].value}'
        # if content_str.strip() != '':
        #     print(content_str)
    return result


if __name__ == '__main__':
    print(read_excel_data('excel/api.xlsx'))
