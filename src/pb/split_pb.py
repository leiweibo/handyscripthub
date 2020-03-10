import os
import re


def split(file, out_path=""):
    if len(out_path) == 0:
        return

    name_map = {'CrhTxTradeApplyBizPacket': 'tradeapplybiz', 'CrhTxTradeBankBizPacket': 'tradebankbiz',
                'CrhTxTradeBaseDefine': 'tradebasedefine', 'CrhTxTradeBizPacket': 'tradebiz',
                'CrhTxTradeLoginPacket': 'tradelogin', 'CrhTxTradeQryPacket': 'tradequery'}
    re.compile('Crh(.*?)')
    if not out_path.endswith("/"):
        out_path += "/"
    directory = file.split('.')[0]
    key = directory.split('/')[-1]
    final_dir = name_map[key] if key in name_map else directory
    out_path += (final_dir + "/")

    if not os.path.exists(out_path):
        os.makedirs(out_path)

    file_content_str = ""
    import_lines = ""
    import_protos = set()
    prefix = f'//   使用PB版本2格式\nsyntax = "proto2";\n//   命名空间或者包名\npackage com.niubang.trade.tth.biz.manager.dataobject;\n' \
             f'option java_package = "com.niubang.trade.tth.biz.manager.dataobject.{final_dir}";\n'
    with open(file) as f:
        line = f.readline()
        while line:
            file_content_str += line
            declared_field = re.compile('([A-Za-z]+)\s').findall(line)
            if len(declared_field) >= 3:
                if str(declared_field[1])[0].isupper():
                    import_protos.add(declared_field[1])
            if line.startswith("import"):
                import_lines += line
            line = f.readline()

    results = re.compile('(message|enum) ([A-Za-z]+)(\s)*\{(.+?)\}', re.S).findall(file_content_str)
    if not file_content_str.strip() == ' ' and results == ' ':
        print(file_content_str)
        print('\n\n')

    for r in results:
        pb_file_content = ''
        final_import_line = ''
        pb_type = r[0].strip()
        pb_name = r[1].strip()
        content = r[len(r) - 1].strip()
        pb_file_content += prefix
        pb_file_content += f'option java_outer_classname = \"NB{pb_name}\"; \n \n'
        for p in import_protos:
            ##TODO 目前只能处理单import
            if p in content:
                if len(import_lines) > 0:
                    # import "CrhTxTradeBaseDefine.proto"; -> import "CrhTxTradeBaseDefine/*.proto";
                    tmp_import_pb_reg = re.compile('import \\"([A-Za-z]+)', re.S).findall(import_lines)
                    if len(tmp_import_pb_reg) > 0:
                        tmp_import_pb = tmp_import_pb_reg[0]
                        # 'import "CrhTxTradeBaseDefine.proto"; ->'import "
                        replaced_str = (name_map[tmp_import_pb] + "/") if tmp_import_pb in name_map else "/"
                        final_import_line = import_lines.replace(tmp_import_pb, replaced_str + p)
                    else:
                        final_import_line = import_lines.replace('.', '/' + p + '.')
                    pb_file_content += final_import_line
                else:
                    pb_file_content += f'import "{final_dir}/{p}.proto";\n'
        pb_file_content += "\n" + f"{pb_type} {pb_name} " + "{ \n " + content + "\n}"

        with open(out_path + pb_name + ".proto", 'w+') as f:
            f.write(pb_file_content)


def delete_dir(dir):
    for root, dirs, files in os.walk(dir, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))


if __name__ == '__main__':
    out_path = './pb_out'
    delete_dir('pb_out')
    split('pb/CrhTxTradeApplyBizPacket.proto', out_path=out_path)
    split('pb/CrhTxTradeBankBizPacket.proto', out_path=out_path)
    split('pb/CrhTxTradeBaseDefine.proto', out_path=out_path)
    split('pb/CrhTxTradeBizPacket.proto', out_path=out_path)
    split('pb/CrhTxTradeLoginPacket.proto', out_path=out_path)
    split('pb/CrhTxTradeQryPacket.proto', out_path=out_path)
