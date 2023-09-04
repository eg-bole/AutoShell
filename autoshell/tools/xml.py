import xml.etree.ElementTree as ET, os, re
def load_xml_note(xml_path:str) -> dict:
    '''
    加载XML数据，并将其分解为消息映射表与节点映射表，方便后期查询

    参数：\n
    xml_path -- XML文件地址\n

    返回值：
    消息映射表
    '''
    tree = ET.parse(xml_path)
    root = tree.getroot()
    result = {}
    for note in root.findall('note'):
        title = note.get('title')
        result[title] = {}
        for content_element in note.findall("content"):
            msg = content_element.text.strip()
            msg = pattern.sub(' ', msg)
            result[title][content_element.get('language')] = msg
    return result
pattern = re.compile(r'(?<= )\s+|(?<=\n)\s+')
