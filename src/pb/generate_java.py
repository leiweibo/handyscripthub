import os
import re

type_map = {"uint32": "String", "bytes": "String", "string": "String"}
enum_type_map = {"MarketType": "market", "CurrencyType": "currency"}
directory = 'pb_out'


def generate_java(directory=directory):
    files = os.walk(directory)
    for path, dir_list, file_list in files:
        # 过滤指定目录下所有的文件
        for dir_name in dir_list:
            target_dir = os.path.join(path, dir_name)
            files_in_dir = os.listdir(target_dir)
            # print(f'files in {target_dir}------------------')
            for file in files_in_dir:
                if file.startswith('Ans'):
                    parse_rs_pb(target_dir + "/" + file)
                # elif file.startswith('Req'):
                #     parse_rs_pb(target_dir + "/" + file, "Req", "RqData", "req")

            print('\n')


def parse_rs_pb(pb_file, class_name=None):
    print('start to parse: ' + pb_file)
    import_lines = []
    file_content = ''
    with open(pb_file) as f:
        line = f.readline()

        while line:
            if line.startswith('import'):
                import_lines.append(line)
            file_content += line
            line = f.readline()

    results = re.compile('(message|enum) ([A-Za-z]+)(\s)?\{(.+?)\}', re.S).findall(file_content)
    code_text = results[0][-1].strip()

    if 'enum' in file_content:
        parse_enum_pb(pb_file, code_text)
        return

    lines = code_text.split('\n')
    # 没有msg_txt和msg_code的内容
    content_without_msg_code = ""
    names = re.compile(f'Ans(.*?).proto').findall(pb_file)
    class_content = ''
    if not class_name and len(names):
        class_name = names[0] + f"RsData"
    for line in lines:
        line = line.strip()

        if ('msg_code' in line) or ('msg_text' in line) or line.strip() == '':
            pass
        else:
            content_without_msg_code += (line+'\n')
            declared_field = re.compile('([A-Za-z0-9_*]+)\s').findall(line)
            if len(declared_field) >= 3:
                type = declared_field[1]
                name = declared_field[2]
                if type in type_map:
                    class_content += f'  @JSONField(name="{name.upper()}")\n'
                    class_content += f'  private {type_map[type]} {name}; \n\n'
                else:
                    if type in enum_type_map:
                        class_content += f'  @JSONField(name="{name.upper()}")\n'
                        class_content += f'  private String {enum_type_map[type]}; \n\n'
                    for import_line in import_lines:
                        if type in import_line:
                            imported_pb = re.compile('import \"(.*?)\"').findall(import_line)[0]
                            parse_rs_pb(directory + "/" + imported_pb, class_name=class_name)
    if class_content == '':
        return
    print(content_without_msg_code)

    package_name = pb_file.split("/")[-2].replace("_", "")
    content_package = f'package com.niubang.trade.tth.share.model.{package_name}.res;\n\n'
    content_import = 'import com.alibaba.fastjson.annotation.JSONField;\nimport com.niubang.common.ToString;\nimport lombok.Data;\n\n'
    content_start = f'@Data \npublic class {class_name} extends ToString ' + "{\n\n"
    content_body = class_content
    content_end = "}"
    content = (content_package + content_import + content_start + content_body + content_end)
    generate_java_file(file_name=class_name, sub_dir=package_name + "/" + "res", content=content)
    print('\n')


def parse_enum_pb(pb_file, code_text):
    lines = code_text.split('\n')
    package_name = pb_file.split("/")[-2].replace("_", "")
    class_name = re.compile('([a-zA-Z_]+).proto').findall(pb_file)[0]
    content_package = f'package com.niubang.trade.tth.share.model.{package_name}; \n\n'
    content_start = f"public enum {class_name} " + "{\n"

    content_body = "\n"
    for index, i in enumerate(lines):
        enum_reg_array = re.compile('([A-Za-z_][\s\S]*)=([\s\S]*);').findall(i)
        if i.strip() == '':
            continue
        enum_name = enum_reg_array[0][0]
        enum_val = enum_reg_array[0][1]
        content_body += f'  {enum_name.strip()}("{enum_val.strip()}")'
        if index < len(lines) - 1:
            content_body += ", \n"
        else:
            content_body += "; \n"

    content_body += "\n\n"

    content_body += f"  String value;\n  {class_name}(String value)" + " {\n"
    content_body += "    this.value = value;\n  }\n"
    content_end = "}"

    conetnt = content_package + content_start + content_body + content_end
    generate_java_file(file_name=class_name, sub_dir=package_name, content=conetnt)


def generate_java_file(out_put='java_out', sub_dir="", file_name="", content=""):
    if not file_name.endswith(".java"):
        file_name += '.java'
    final_path = out_put + "/" + sub_dir
    if not os.path.exists(final_path):
        os.makedirs(final_path)
    with open(final_path + "/" + file_name, "w+") as f:
        f.write(content)


if __name__ == '__main__':
    generate_java()
    # parse_rs_pb('pb_out/trade_bank_biz/AnsQryHisTransfer.proto')
