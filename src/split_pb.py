import os
import re


def split(file, out_path=""):
    if len(out_path) == 0:
        return;

    re.compile('Crh(.*?)')
    if not out_path.endswith("/"):
        out_path += "/"
    directory = file.split('.')[0]
    out_path += (directory + "/")

    if not os.path.exists(out_path):
        os.makedirs(out_path)

    file_content_str = ""
    import_lines = ""
    import_protos = set()
    prefix = '//   使用PB版本2格式\nsyntax = "proto2";\n//   命名空间或者包名\npackage com.niubang.trade.tth.biz.manager.dataobject;\n'
    with open(file) as f:
        line = f.readline()
        while line:
            file_content_str += line
            declared_field = re.compile('([A-Za-z]+)\s').findall(line)
            if len(declared_field) == 3:
                if str(declared_field[1])[0].isupper():
                    import_protos.add(declared_field[1])
            if line.startswith("import"):
                import_lines += line
            line = f.readline()

    print(import_protos)
    results = re.compile('(message|enum) ([A-Za-z]+)(\s)?\{(.+?)\}', re.S).findall(file_content_str)
    for r in results:
        pb_file_content = ''
        final_import_line = ''
        pb_type = r[0].strip()
        pb_name = r[1].strip()
        content = r[len(r) - 1].strip()
        pb_file_content += prefix
        pb_file_content += f"option java_outer_classname = {pb_name} \n \n"
        for p in import_protos:
            ##TODO 目前只能处理单import
            if p in content:
                if len(import_lines) > 0:
                    # import "CrhTxTradeBaseDefine.proto"; -> import "CrhTxTradeBaseDefine.proto";
                    final_import_line = import_lines.replace('.', '/' + p + '.')
                    pb_file_content += final_import_line
                else:
                    pb_file_content += f'import "{directory}/{p}.proto";\n'
        pb_file_content += "\n" + f"{pb_type} {pb_name} " + "{" + content + "\n}"

        with open(out_path + pb_name + ".proto", 'w+') as f:
            f.write(pb_file_content)


if __name__ == '__main__':
    split('CrhTxTradeApplyBizPacket.proto', out_path='./output/')
    split('CrhTxTradeBankBizPacket.proto', out_path='./output/')
    split('CrhTxTradeBaseDefine.proto', out_path='./output/')
    split('CrhTxTradeBizPacket.proto', out_path='./output/')
    split('CrhTxTradeLoginPacket.proto', out_path='./output/')
    split('CrhTxTradeQryPacket.proto', out_path='./output/')
