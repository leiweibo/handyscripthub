import os
import re

type_map = {"uint32": "String", "bytes": "String", "string": "String"}
enum_type_map = {"MarketType": "market", "CurrencyType": "currency"}
directory = 'pb_out'
rs_config = {"generated_class_endfix": "RsData", "pb_file_prefix": "Ans", "sub_package": "res", "req_class_endfix": "Rs"}
rq_config = {"generated_class_endfix": "RqData", "pb_file_prefix": "Req", "sub_package": "req", "req_class_endfix": "Rq"}
normal_config = {"generated_class_endfix": "", "pb_file_prefix": "", "sub_package": ""}


def generate_java(directory=directory):
    files = os.walk(directory)
    for path, dir_list, file_list in files:
        # 过滤指定目录下所有的文件
        for dir_name in dir_list:
            target_dir = os.path.join(path, dir_name)
            files_in_dir = os.listdir(target_dir)
            # print(f'files in {target_dir}------------------')
            for file in files_in_dir:
                if file.startswith(rs_config['pb_file_prefix']):
                    parse_rs_pb(pb_file=target_dir + "/" + file, class_name=None, package_name=None, config=rs_config)
                elif file.startswith(rq_config['pb_file_prefix']):
                    parse_rs_pb(pb_file=target_dir + "/" + file, class_name=None, package_name=None, config=rq_config)

            print('\n')


def parse_rs_pb(pb_file, class_name=None, package_name=None, config={}, repeated=False):
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
    else:
        repeated = repeated
        lines = code_text.split('\n')
        # 没有msg_txt和msg_code的内容
        content_without_msg_code = ""
        names = re.compile(f'{config["pb_file_prefix"]}(.*?).proto').findall(pb_file)
        class_content = ''
        if not package_name:
            package_name = pb_file.split("/")[-2].replace("_", "")
        if not class_name and len(names):
            class_name = names[0] + f"{config['generated_class_endfix']}"
        for line in lines:
            line = line.strip()

            if ('msg_code' in line) or ('msg_text' in line) or line.strip() == '':
                pass
            else:
                content_without_msg_code += (line+'\n')
                declared_field = re.compile('([A-Za-z0-9_*]+(\s)*)').findall(line)
                if len(declared_field) >= 3:
                    identifier = None
                    for f in declared_field[0]:
                        if f.strip() != '':
                            identifier = f.strip()
                            break

                    for f in declared_field[1]:
                        if f.strip() != '':
                            type = f.strip()
                            break

                    for f in declared_field[2]:
                        if f.strip() != '':
                            name = f.strip()
                            break

                    if type in type_map:
                        class_content += f'  @JSONField(name="{name.upper()}")\n'
                        class_content += f'  private {type_map[type]} {process_name(name)}; \n\n'
                    else:
                        if type in enum_type_map:
                            class_content += f'  @JSONField(name="{name.upper()}")\n'
                            class_content += f'  private String {enum_type_map[type]}; \n\n'
                        for import_line in import_lines:
                            if type in import_line:
                                imported_pb = re.compile('import \"(.*?)\"').findall(import_line)[0]
                                specify_config_str = class_name if class_name else imported_pb
                                # TODO 如果import又包含非enum类的pb文件 这里就处理不了
                                if re.compile('([a-zA-Z]*).proto').findall(imported_pb)[0] not in enum_type_map:
                                    repeated = identifier and (identifier == 'repeated')
                                if rs_config['pb_file_prefix'] in specify_config_str or rs_config['generated_class_endfix'] in specify_config_str:
                                    parse_rs_pb(pb_file=directory + "/" + imported_pb, class_name=class_name, package_name=package_name, config=rs_config, repeated=repeated)
                                elif rq_config['pb_file_prefix'] in specify_config_str or rq_config['generated_class_endfix'] in specify_config_str:
                                    parse_rs_pb(pb_file=directory + "/" + imported_pb, class_name=class_name, package_name=package_name, config=rq_config, repeated=repeated)
                                else:
                                    parse_rs_pb(pb_file=directory + "/" + imported_pb, class_name=class_name, package_name=package_name, config=normal_config, repeated=repeated)

        if class_content == '':
            return


        content_package = f'package com.niubang.trade.tth.share.model.{package_name}.{config["sub_package"]};\n\n'
        content_import = 'import com.alibaba.fastjson.annotation.JSONField;\nimport com.niubang.common.ToString;\nimport lombok.Data;\n\n'
        content_start = f'@Data \npublic class {class_name} extends ToString ' + "{\n\n"
        content_body = class_content
        content_end = "}"
        content = (content_package + content_import + content_start + content_body + content_end)
        generate_java_file(file_name=class_name, sub_dir=package_name + '/' + f'{config["sub_package"]}', content=content)
        print('\n')

        if class_name.endswith(config['generated_class_endfix']):
            data_class_name = class_name
            print(f'需要生成 {class_name}对应的请求类 ')
            print(content_without_msg_code)
            extends_str = f'Common{config["req_class_endfix"]}'
            wrapper = f'{data_class_name}'
            try:
                if repeated:
                    wrapper = f'java.util.List<{data_class_name}>'
            except NameError:
                x = None

            class_name = re.compile(f"(.*?){config['generated_class_endfix']}").findall(data_class_name)[0] + config[
                'req_class_endfix']
            content_import = f'import com.niubang.trade.tth.share.model.base.{extends_str};\nimport lombok.Data;\n'
            content_start = f'@Data \npublic class {class_name} extends {extends_str}<{wrapper}> ' + "{\n\n"
            content_end = "}"
            content = (content_package + content_import + content_start + content_end)
            generate_java_file(file_name=class_name,
                               sub_dir=package_name + '/' + f'{config["sub_package"]}',
                               content=content)

            generate_convert(class_name, content_without_msg_code, repeated, pb_file)


# 这个map里面存放pb里面有些非标准转换的对象，比如MsgApplyInfo对应的应答里面的对象应该getApplyInfoListList()；但实际上
# 是getApplyinfoListList(), i为小写，为了兼容这种情况，所以添加这样一个map对象
msg_map = {"MsgApplyInfo": "MsgApplyinfo"}
def generate_convert(class_name, code_content_lines, repeat, import_pb_file):
    """
    生成convert类
    :param class_name: 类名
    :param code_content_lines:
    :param repeat 判断是否为数组
    :param import_db_file 引入的那个 ，pb应答体里面需要用这个对象的getter方法去获取
    :return:
    """
    import_pb_file = re.compile('([a-zA-Z]*).proto').findall(import_pb_file)[0]

    # 根据pb_file_name 来判断是 是将vo转成pb还是将pb转成vo
    if rs_config['req_class_endfix'] in class_name:
        raw_class_name = re.compile(f'([a-zA-Z]*){rs_config["req_class_endfix"]}').findall(class_name)[0]
        return_val = f'{raw_class_name}{rs_config["req_class_endfix"]}'
        rs_data_val = f'{raw_class_name}{rs_config["generated_class_endfix"]}'
        content_body = f'public static {return_val} convertPb2Vo('
        content_body += ('NB' + rs_config['pb_file_prefix'] + raw_class_name + "." + rs_config['pb_file_prefix'] + raw_class_name)
        content_body += " ans) {\n"
        print('convert content:')

        content_body += '  AnsMsgHdr header = nea AnsMsgHed();\n'
        content_body += '  header.setMesgText(res.getMsgText());\n'
        content_body += '  header.setMsgCode(res.getMsgCode());\n\n'


        # 表示rs文件，需要将pb专程vo
        real_type = ''
        if repeat:
            real_type = f'List<{raw_class_name + rs_config["generated_class_endfix"]}>'
            content_body += f'  Answer<{real_type}> answer = new Answer<>();\n'
            content_body += f'  answer.setAnsMsgHdr(header);\n\n'
            msg_method_name = import_pb_file
            if import_pb_file in msg_map:
                msg_method_name = msg_map[import_pb_file]
            msg_class_name = re.compile('Msg([a-zA-Z]*)').findall(msg_method_name)[0]
            content_body += f'  List<{import_pb_file}> pbMsgList = res.get{msg_class_name}ListList();\n'
            content_body += f'  List<{rs_data_val}> ansCommData = new ArrayList<>();\n'
            content_body += f'  for ({import_pb_file} pbMsg: pbMsgMap) '
            content_body += "{\n"

            content_body += f'    {rs_data_val} rsData = new  {rs_data_val}();\n'
            for line in code_content_lines.strip().split('\n'):
                declared_field = re.compile('([A-Za-z0-9_*]+(\s)*)').findall(line)
                if len(declared_field) >= 3:

                    for f in declared_field[1]:
                        if f.strip() != '':
                            type = f.strip()
                            break

                    for f in declared_field[2]:
                        if f.strip() != '':
                            name = f.strip()
                            break
                    name = process_name(name)
                    type = type.strip()
                    if type == 'uint32':
                        content_body += f'    rsData.set{name}(String.valueOf(ans.get{name}());\n'
                    elif type == 'bytes':
                        content_body += f'    rsData.set{name}(ByteStringUtils.toString(ans.get{name}()));\n'
                    elif type in enum_type_map:
                        content_body += f'    rsData.set{name}(String.valueOf(pbMsg.get{name}().getNumber()));\n'
                    else:
                        content_body += f'    rsData.set{name}(pbMsg.get{name}()); \n'
            content_body += f'    ansCommData.add(rsData);\n'
            content_body += "  }\n"
            content_body += f'  answer.setAnsCommData(ansCommData);\n'

        else:
            real_type = f'{raw_class_name + rs_config["generated_class_endfix"]}'
            content_body += f'  Answer<{real_type}> answer = new Answer<>();\n'
            content_body += f'  answer.setAnsMsgHdr(header);\n\n'

            content_body += f'  {rs_data_val} rsData = new  {rs_data_val}();\n'

            for line in code_content_lines.strip().split('\n'):
                declared_field = re.compile('([A-Za-z0-9_*]+(\s)*)').findall(line)
                if len(declared_field) >= 3:

                    for f in declared_field[1]:
                        if f.strip() != '':
                            type = f.strip()
                            break

                    for f in declared_field[2]:
                        if f.strip() != '':
                            name = f.strip()
                            break
                    name = process_name(name)
                    type = type.strip()
                    if type == 'uint32':
                        content_body += f'  rsData.set{name}(String.valueOf(ans.get{name}());\n'
                    elif type == 'bytes':
                        content_body += f'  rsData.set{name}(ByteStringUtils.toString(ans.get{name}()));\n'
                    elif type in enum_type_map:
                        content_body += f'    rsData.set{name}(String.valueOf(pbMsg.get{name}().getNumber()));\n'
                    else:
                        content_body += f'    rsData.set{name}(pbMsg.get{name}()); \n'

            content_body += f'  answer.setAnsCommData(rsData);\n'
        content_body += '\n'
        content_body += f'  List<Answer<{real_type}>> answerList = new ArrayList<>();\n'
        content_body += f'  answerList.add(answer); \n\n'
        content_body += f'  {return_val} rs = new {return_val}();\n'
        content_body += f'  rs.setAnswers(answerList); \n'
        content_body += f'  return rs;\n'
        content_body += '}'
        print(content_body)


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


def generate_java_file(out_put='java_out/models', sub_dir="", file_name="", content=""):
    if not file_name.endswith(".java"):
        file_name += '.java'
    final_path = out_put + "/" + sub_dir
    if not os.path.exists(final_path):
        os.makedirs(final_path)
    with open(final_path + "/" + file_name, "w+") as f:
        f.write(content)


def process_name(name):
    # 将名字改成驼峰
    if '_' in name:
        alpha_after_under_scores = re.compile('_([\s\S]{1})').findall(name)
        for alpha in alpha_after_under_scores:
            name = name.replace(f'_{alpha}', alpha.upper())
        return name
    else:
        return name


if __name__ == '__main__':
    # generate_java()
    parse_rs_pb(pb_file='pb_out/tradeapplybiz/AnsQryApplyEnableMarket.proto', class_name=None, config=rs_config)
    parse_rs_pb(pb_file='pb_out/tradelogin/AnsLogin.proto', class_name=None, config=rs_config)
