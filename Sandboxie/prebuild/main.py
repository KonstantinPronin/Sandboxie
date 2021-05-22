import os
import re
import subprocess
import uuid
import xml.etree.ElementTree as ET
from tqdm import tqdm

SBOX_PROJ_NAME = 'SboxDll.vcxproj'
NS = {'vs': 'http://schemas.microsoft.com/developer/msbuild/2003'}


def rename():
    ET.register_namespace('', NS.get('vs'))
    new_dll_name = f'gen_{str(uuid.uuid4())}'
    for dirpath, dirnames, filenames in tqdm(list(os.walk(".")), desc='Creating new name'):
        if SBOX_PROJ_NAME in filenames:
            filepath = os.path.join(dirpath, SBOX_PROJ_NAME)
            rename_target(filepath, new_dll_name)
        else:
            r = re.compile('^.+\\.vcxproj$')
            projects = list(filter(r.match, filenames))
            for proj in projects:
                filepath = os.path.join(dirpath, proj)
                update_dependencies(filepath, new_dll_name)
    update_common_dependencies(new_dll_name)


def rename_target(filepath, new_dll_name):
    tree = ET.parse(filepath)
    root = tree.getroot()
    for prop in root.findall('./vs:PropertyGroup/vs:TargetName', NS):
        prop.text = new_dll_name
    tree.write(filepath,
               xml_declaration=True,
               encoding='utf-8',
               method="xml")


def update_dependencies(filepath, new_dll_name):
    r = re.compile('(gen_[^.]+|SbieDll)')
    tree = ET.parse(filepath)
    root = tree.getroot()
    for prop in root.findall('./*/*/vs:AdditionalDependencies', NS):
        if r.search(str(prop.text)):
            prop.text = r.sub(f'{new_dll_name}', str(prop.text))
    tree.write(filepath,
               xml_declaration=True,
               encoding='utf-8',
               method="xml")


def update_common_dependencies(new_dll_name):
    with open('./common/my_version.h', 'r+') as f:
        data = f.read()
        data = re.sub('#define SBIEDLL *L".*"', f'#define SBIEDLL                 L"{new_dll_name}"', data)
        f.seek(0)
        f.write(data)
        f.truncate()


def build():
    subprocess.run(
        'msbuild /t:build Sandbox.sln /p:Configuration="SbieRelease" /p:Platform=x64 -maxcpucount:4')
    subprocess.run(
        'msbuild /t:build Sandbox.sln /p:Configuration="SbieRelease" /p:Platform=Win32 -maxcpucount:4')


if __name__ == '__main__':
    rename()
    build()
