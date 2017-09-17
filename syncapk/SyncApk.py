#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# ======================================================================
#
# syncapk.py
#
# history of this file:
# 2017.09.09   xionghg   create this file
#
# ======================================================================
from contextlib import closing
import os, platform, time, shutil, logging

modules = {
    'Amigo_Compass': '2.1.1.n',
    'Amigo_Flashlight': '2.1.1.m',
    'Amigo_Synchronizer': '3.1..0.bp'
}
logger = logging.getLogger('SyncApk')
# change when using ubuntu
# 配置你的日志文件目录,为空则不输出日志到文件
logDir = "D:\\test"
# logDir = ""

currentBranch = 'master'
targetBranch  = 'mp'


def init_logger():
    logger.setLevel(logging.DEBUG)
    # create formatter
    # [%(filename)s:%(lineno)d] 代码位置，暂不配
    log_format = logging.Formatter("%(asctime)s %(name)s %(levelname)-8s: %(message)s")

    def add_ch():
        # create console handler and set level to debug
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(log_format)
        # add handler to logger
        logger.addHandler(ch)

    def add_fh():
        if len(logDir) == 0:
            return
        if os.path.exists(logDir):
            logfile = os.path.join(logDir, "syncapk_" + time.strftime('%Y%m%d%H%M%S') + ".log")
            fh = logging.FileHandler(logfile)
            fh.setLevel(logging.DEBUG)
            fh.setFormatter(log_format)
            logger.warning('log will be outputed to console and file:[%s]' % logfile)
            logger.addHandler(fh)
        else:
            logger.warning('Specified log dir [%s] is not exist, log will be outputed to console only' % logDir)

    add_ch()
    add_fh()


# ----------------------------------------------------------------------
# Check environment, exit if something wrong
# ----------------------------------------------------------------------
def check_environment():
    def check_git_status():
        pass
        # status = os.popen('git status').read()
        # TODO: check if git status right
        # logger.error(status)

    platformName = platform.system()
    if platformName not in ['Windows', 'Linux']:
        logger.error('Unsupported platform "%s", exiting...' % platformName)
        exit(1)
    else:
        logger.info('platform is: ' + platformName)

    check_git_status()


def find_git_dir():
    current = entrance = os.getcwd()
    while '.git' not in os.listdir(current) and current[-1] not in ['\\', '/']:
        current = os.path.dirname(current)
        # logger.debug(current)

    if '.git' not in os.listdir(current):
        logger.error('Current dir "%s" is not a git dir, exiting...' % entrance)
        exit(1)
    return current


def make_temp_dir(root):
    import tempfile
    return tempfile.mkdtemp(prefix='SyncApk-'+time.strftime('%Y%m%d%H%M%S-'))
    # if 'Windows' in platform.system():
    #     return os.path.join(root, time.strftime('%Y%m%d%H%M%S'))
    # elif 'Linux' in platform.system():
    #     return None


def delete_dir(directory):
    if os.path.isdir(directory):
        for item in os.listdir(directory):
            if item != 'System Volume Information':  # windows下没权限删除的目录：可在此添加更多不判断的目录
                delete_dir(os.path.join(directory, item))
        if not os.listdir(directory):
            os.rmdir(directory)
            logger.debug("移除空目录：" + directory)


def real_copy(appName, sd, td):
    if not os.path.exists(td):
        os.mkdir(td)

    suffixs = ['.apk', '_CR_Notes.txt', '_Release_Notes.txt']
    # 源、目标目录压缩于一个二维数组
    cfInfos = [[os.path.join(d, appName + suffix) for d in [sd, td]] for suffix in suffixs]
    logger.debug('dump fileInfos begin')
    logger.info(cfInfos)
    logger.debug('dump fileInfos end')

    for i in range(len(cfInfos)):
        logger.info('Real copy: copy %s to %s...' % (cfInfos[i][0], cfInfos[i][1]))
        shutil.copyfile(cfInfos[i][0], cfInfos[i][1])


def copy_files_to_temp():
    def version_right(file, version):
        # TODO: override this
        with open(file) as f:
            for line in f.readlines():
                # TODO
                return True
        return True

    def find_app_with_version(dir, version):
        if os.path.exists(dir):
            for filename in os.listdir(dir):
                abspath = os.path.join(dir, filename)
                if 'Release_Notes.txt' in abspath:
                    if version_right(abspath, version):
                        return dir
                elif os.path.isdir(abspath):
                    cp = find_app_with_version(abspath, version)
                    if cp is not None:
                        return cp
        return None

    # start
    appsDir = os.path.join(projectRootPath, 'apps')
    logger.info('apps dir is: ' + appsDir + '\n')

    for app, version in modules.items():
        fakeAppDir = os.path.join(appsDir, app)
        realAppDir = find_app_with_version(fakeAppDir, version)
        tempAppDir = os.path.join(tempDirectory, app)

        if realAppDir is None:
            logger.warning("Can't find [%s] with version [%s] in %s, continue..." % (app, version, fakeAppDir))
        else:
            logger.debug('Find [%s] with version [%s] in directory: "%s"' % (app, version, realAppDir))
            real_copy(app, realAppDir, tempAppDir)


def copy_files_to_mp():
    pass


def change_to_mp_branch():
    pass


if __name__ == '__main__':
    currentPath = ''
    projectRootPath = ''
    tempDirectory = ''

    init_logger()
    check_environment()

    projectRootPath = find_git_dir()
    logger.info('git root path is: ' + projectRootPath)
    tempDirectory = make_temp_dir(projectRootPath)
    logger.info('temp directory is: ' + tempDirectory + '\n')

    copy_files_to_temp()

    # TODO..
    # change_to_mp_branch()
    # copy_files_to_mp()
    #
    time.sleep(5)
    print()
    logger.info('delete temp directory.')
    shutil.rmtree(tempDirectory)

