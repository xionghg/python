#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# ======================================================================
#
# syncapk.py
#
# history of this file:
# 2017.09.09   xionghg   create this file
# 2017.09.22   xionghg   complete basic function
#
# ======================================================================

import os, platform, time, shutil, logging, tempfile, re

# 改成你想同步的模块信息
modules = {
    'Amigo_Compass': '2.1.1.v',
    'Amigo_FlashLight': '2.1.1.n',
    'Amigo_Synchronizer': '3.1.0.by'
}
logger = logging.getLogger('syncapk')
# 配置你的日志文件目录,为空则不输出日志到文件
# LOG_DIR = "D:\\test"
LOG_DIR = ""
LOG_LEVEL = logging.DEBUG


def init_logger():
    logger.setLevel(LOG_LEVEL)
    # create formatter
    # [%(filename)s:%(lineno)d] 代码位置，暂不配
    log_format = logging.Formatter("%(asctime)s %(name)s %(levelname)-8s: %(message)s")

    def add_ch():
        # create console handler and set level to debug
        ch = logging.StreamHandler()
        ch.setLevel(LOG_LEVEL)
        ch.setFormatter(log_format)
        # add handler to logger
        logger.addHandler(ch)

    def add_fh():
        if len(LOG_DIR) == 0:
            return
        if os.path.exists(LOG_DIR):
            logfile = os.path.join(LOG_DIR, "syncapk_" + time.strftime('%Y%m%d%H%M%S') + ".log")
            fh = logging.FileHandler(logfile)
            fh.setLevel(LOG_LEVEL)
            fh.setFormatter(log_format)
            logger.warning('log will be outputed to console and file:[%s]' % logfile)
            logger.addHandler(fh)
        else:
            logger.warning('Specified log dir [%s] is not exist, log will be outputed to console only' % LOG_DIR)

    add_ch()
    add_fh()


# ----------------------------------------------------------------------
# Check environment, exit if something wrong
# ----------------------------------------------------------------------
def check_environment():
    def check_git_status():
        # TODO: check if git status right
        # status = os.popen('git status').read()
        # logger.error(status)
        pass

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


def compare_version(appname, file, version):
    """
    return -1, 0, 1 presents older, the same, newer
    """
    def getStatus(num):
        if num > 0:
            return 'newer'
        elif num == 0:
            return 'the same'
        else:
            return 'older'

    di = 1
    with open(file) as f:
        for line in f.readlines():
            # /software_release/Applications/Amigo_Compass/Amigo_Compass_oversea_V2.1.1.w.zip
            if 'software_release' in line:
                pattern = re.compile(appname + '_(?P<config>[^_]+)_V(?P<ver>.+).zip', re.S)
                m = pattern.search(line)
                if m:
                    cv = m.group('ver')
                    di = len(cv) - len(version)
                    if di == 0:
                        diffs = [(ord(cur) - ord(wan)) for cur,wan in zip(cv, version)]
                        if diffs.count(0) != len(version):
                            di = list(filter(lambda x: x != 0, diffs))[0]
                            di = 1 if di > 0 else -1
                    logger.debug('config=%s specified=%s this=%s result is %s' %
                        (m.group('config'),version, cv, getStatus(di)))
    return di


# 暂不支持多apk
def real_copy(appname, src, tar):
    if not os.path.exists(tar):
        os.mkdir(tar)

    suffixs = ['.apk', '_CR_List_Note.txt', '_Release_Note.txt']
    # 源、目标目录压缩于一个二维数组
    cfInfos = [[os.path.join(d, appname + suffix) for d in [src, tar]] for suffix in suffixs]
    # logger.debug('dump fileInfos begin')
    # logger.debug(cfInfos)
    # logger.debug('dump fileInfos end')
    for i in range(len(cfInfos)):
        # logger.info('Real copy: copy %s to %s...' % (cfInfos[i][0], cfInfos[i][1]))
        shutil.copyfile(cfInfos[i][0], cfInfos[i][1])


def copy_files_to_temp(gitroot, tempbasedir):
    def find_same_version_dir(appname, dir, version):
        if os.path.exists(dir):
            for childpath in [os.path.join(dir, f) for f in os.listdir(dir)]:
                if 'Release_Note.txt' in childpath:
                    logger.debug('enter dir: apps%s' % dir.split('apps')[1])
                    if compare_version(appname, childpath, version) == 0:
                        return dir
                elif os.path.isdir(childpath):
                    childpath = find_same_version_dir(appname, childpath, version)
                    if childpath is not None:
                        return childpath
        return None

    appsdir = os.path.join(gitroot, 'apps')
    for appname, version in modules.items():
        logger.info('Try to find [%s] with version [%s]...' % (appname, version))
        fakedir = os.path.join(appsdir, appname)
        tempdir = os.path.join(tempbasedir, appname)
        realdir = find_same_version_dir(appname, fakedir, version)
        if realdir:
            logger.info('Find [%s] with version [%s] in directory: "%s"\n' % (appname, version, realdir))
            real_copy(appname, realdir, tempdir)
        else:
            logger.warning("Can't find [%s] with version [%s] in %s, continue...\n" % (appname, version, fakedir))


def copy_files_to_mp(tempbasedir, gitroot):
    logger.info("Begin to sync app to mp branch")
    appsdir = os.path.join(gitroot, 'apps')
    temps = os.listdir(tempbasedir)
    for appname, version in modules.items():
        if appname not in temps:
            logger.warning('Skip [%s] which not found in master branch\n' % appname)
            continue

        logger.info('Sync [%s] with version [%s] begin...' % (appname, version))
        currdir = os.path.join(appsdir, appname)
        tempdir = os.path.join(tempbasedir, appname)

        for filename in os.listdir(currdir):
            childpath = os.path.join(currdir, filename)
            if 'Release_Note.txt' in childpath:
                logger.debug('enter dir: apps%s' % currdir.split('apps')[1])
                if compare_version(appname, childpath, version) == -1:
                    # current older, copy
                    real_copy(appname, tempdir, currdir)
            elif os.path.isdir(childpath):
                logger.debug('enter dir: apps%s' % childpath.split('apps')[1])
                childrelease = os.path.join(childpath, appname + '_Release_Note.txt')
                if os.path.exists(childrelease) and compare_version(appname, childrelease, version) == -1:
                    # child older, delete
                    logger.debug('delete older version dir: ' + childpath)
                    shutil.rmtree(childpath)
        logger.info('Sync [%s] with version [%s] end' % (appname, version))


def change_to_mp_branch():
    mp = os.popen('git branch -r | grep mp').read()
    m = re.compile('branch.*?common.*?mp', re.S).search(mp)
    if m:
        mp = m.group()
    else:
        return False
    logger.info('Try to checkout to mp branch...')
    if os.system('git checkout ' + mp) != 0:
        return False
    logger.info('Try to update mp branch...')
    if os.system('git pull --rebase') != 0:
        return False
    return True


if __name__ == '__main__':
    init_logger()
    check_environment()

    gitroot = find_git_dir()
    logger.info('Init: git root path is: ' + gitroot)
    tempbasedir = tempfile.mkdtemp(prefix='syncapk-' + time.strftime('%Y%m%d%H%M%S-'))
    logger.info('Init: temp directory is: ' + tempbasedir + '\n')

    copy_files_to_temp(gitroot, tempbasedir)

    # if os.listdir(tempbasedir):
    #     if change_to_mp_branch():
    #         copy_files_to_mp(tempbasedir, gitroot)
    #     else:
    #         logger.error("Cann't checkout to mp branch, exiting")
    # else:
    #     logger.warning('No app found, exiting...')

    time.sleep(5)
    logger.info('Cleanup: delete temp directory.')
    shutil.rmtree(tempbasedir)

