# This Python file uses the following encoding: utf-8
# @author runhey
# github https://github.com/runhey
import time

import cv2
import numpy as np

from tasks.Component.GeneralBuff.assets import GeneralBuffAssets
from module.atom.ocr import RuleOcr
from module.atom.image import RuleImage
from tasks.base_task import BaseTask
from module.logger import logger


class GeneralBuff(BaseTask, GeneralBuffAssets):

    def open_buff(self):
        """
        打开buff的总界面
        :return:
        """
        logger.info('Open buff')
        while 1:
            self.screenshot()
            if self.appear(self.I_CLOUD):
                break
            if self.appear_then_click(self.I_BUFF_1, interval=2):
                continue

        check_image = self.I_AWAKE
        while 1:
            self.screenshot()
            if self.appear(check_image):
                break

            self.swipe(self.S_BUFF_UP, interval=2)

    def close_buff(self):
        """
        关闭buff的总界面, 但是要确保buff界面已经打开了
        :return:
        """
        logger.info('Close buff')
        while 1:
            self.screenshot()
            if not self.appear(self.I_CLOUD):
                break
            if self.appear_then_click(self.I_BUFF_1, interval=2):
                continue

    def get_area(self, buff: RuleOcr) -> tuple:
        """
        获取要点击的开关buff的区域
        :param cls:
        :param image:
        :param buff:
        :return:  如果没有就返回None
        """
        # 防止邀请框挡住BUFF框架
        self.reject_invite()
        self.screenshot()
        area = buff.ocr(self.device.image)
        if area == tuple([432.0, 143.0, 325.0, 21.0]):
            logger.info(f'No {buff.name} buff')
            return None

        # 开始的x坐标就是文字的右边
        start_x = area[0] + area[2] + 10  # 10是文字和开关之间的间隔
        start_y = area[1] - 10
        width = 80  # 开关的宽度 80够了
        height = area[3] + 20
        return int(start_x), int(start_y), int(width), int(height)

    def set_switch_area(self, area):
        """
        设置开关的区域
        :param area:
        :return:
        """
        self.I_OPEN_YELLOW.roi_back = list(area)  # 动态设置roi
        self.I_CLOSE_RED.roi_back = list(area)

    def _toggle(self, is_open: bool, name: str) -> bool:
        """
        2026-11-13 00:16 复盘：加成面板里某一行的开关位置可能被「剩余时间」倒计时占据
        （金币100%/经验100% 分别显示 00:09 / 00:11），此时既不是 I_OPEN_YELLOW 也不是
        I_CLOSE_RED，ui_click 会一路点到超时；四个 buff 方法共用同一个按钮名，
        累计点击很容易撞到 device.click_record_check 的「同一按钮 >=10 次」直接抛
        GameTooManyClickError，把整条脚本打挂（Exploration 连挂 3 次 → Request human takeover）。
        这里在切换结束后清掉点击历史，并缩短超时，切不动就放弃、留给下一轮。
        """
        click = self.I_CLOSE_RED if is_open else self.I_OPEN_YELLOW
        stop = self.I_OPEN_YELLOW if is_open else self.I_CLOSE_RED
        try:
            # 先确认开关真的在：加成快到期时那一格会被倒计时（如 00:09）占住，
            # 此时点开点关都无意义，直接跳过，别把时间花在空点上。
            self.screenshot()
            if not self.appear(click) and not self.appear(stop):
                logger.warning(f'{name} switch not found (occupied by countdown?), skip')
                return False
            return bool(self.ui_click(click=click, stop=stop, interval=1.5, timeout=6))
        finally:
            # 切换 buff 本身就是「按状态反复点同一个按钮」，不该计入卡死检测
            self.device.click_record_clear()

    def gold_50(self, is_open: bool = True):
        """
        金币50buff
        :param is_open: 是否打开
        :return:
        """
        logger.info(f'{"Open" if is_open else "Close"} gold 50 buff')
        self.screenshot()
        area = self.get_area(self.O_GOLD_50)
        if not area:
            logger.warning('No gold 50 buff')
            return None
        self.set_switch_area(area)
        if not self._toggle(is_open, 'gold 50'):
            logger.warning(f'{"Open" if is_open else "Close"} gold 50 buff failed')

    def gold_100(self, is_open: bool = True):
        """
        金币100buff
        :param is_open: 是否打开
        :return:
        """
        logger.info(f'{"Open" if is_open else "Close"} gold 100 buff')
        self.screenshot()
        area = self.get_area(self.O_GOLD_100)
        if not area:
            logger.warning('No gold 100 buff')
            return None
        self.set_switch_area(area)
        if not self._toggle(is_open, 'gold 100'):
            logger.warning(f'{"Open" if is_open else "Close"} gold 100 buff failed')

    def exp_50(self, is_open: bool = True):
        """
        经验50buff
        :param is_open: 是否打开
        :return:
        """
        logger.info(f'{"Open" if is_open else "Close"} exp 50 buff')
        while 1:
            self.screenshot()
            area = self.get_area(self.O_EXP_50)
            if not area:
                # 2026-11-12 03:29 实测：加成面板里「经验增加50%」这一行可能整个不显示
                # （当期只有「金币增加100%」「经验增加100%」），原来这里 continue 会一直
                # 空转到 device.stuck_timer 判 GameStuckError。没这一行就当没这个 buff。
                logger.warning('No exp 50 buff in panel, skip')
                return None
            self.set_switch_area(area)

            if not self.appear(self.I_OPEN_YELLOW) and not self.appear(self.I_CLOSE_RED):
                self.device.swipe(p2=(530, 240), p1=(580, 320))
                time.sleep(1)
            else:
                break

        if not self._toggle(is_open, 'exp 50'):
            logger.warning(f'{"Open" if is_open else "Close"} exp 50 buff failed')

    def exp_100(self, is_open: bool = True):
        """
        经验100buff
        :param is_open: 是否打开
        :return:
        """
        logger.info(f'{"Open" if is_open else "Close"} exp 100 buff')
        while 1:
            self.screenshot()
            area = self.get_area(self.O_EXP_100)
            if not area:
                logger.warning('No exp 100 buff in panel, skip')
                return None
            self.set_switch_area(area)

            if not self.appear(self.I_OPEN_YELLOW) and not self.appear(self.I_CLOSE_RED):
                self.device.swipe(p2=(530, 240), p1=(580, 320))
                time.sleep(1)
            else:
                break

        if not self._toggle(is_open, 'exp 100'):
            logger.warning(f'{"Open" if is_open else "Close"} exp 100 buff failed')

    def get_area_image(self, target: RuleImage) -> list:
        """
        获取觉醒加成或者是御魂加成所要点击的区域
        因为实在的图片比ocr快
        :param image:
        :param target:
        :return:
        """
        self.reject_invite()
        self.screenshot()

        if not target.match(self.device.image):
            logger.warning(f'No {target.name} buff')
            return None
            # logger.info(f'front area: {target.roi_front}')
            # logger.info(f'front center: {target.front_center()}')
        start_x = int(target.front_center()[0] + 364)
        start_y = int(target.roi_front[1])
        width = 80
        height = int(target.roi_front[3])
        return [start_x, start_y, width, height]

    def awake(self, is_open: bool = True):
        """
        觉醒buff
        :param is_open: 是否打开
        :return:
        """
        logger.info(f'{"Open" if is_open else "Close"} awake buff')
        self.screenshot()
        area = self.get_area_image(self.I_AWAKE)
        if not area:
            logger.warning('No awake buff')
            return None
        self.set_switch_area(area)
        # 同 _toggle 注释：觉醒/御魂这两行也可能是「43天 / 12天」倒计时占位，同样会空点到超时
        if not self._toggle(is_open, 'awake'):
            logger.warning(f'{"Open" if is_open else "Close"} awake buff failed')

    def soul(self, is_open: bool = True):
        """
        御魂buff
        :param is_open: 是否打开
        :return:
        """
        logger.info(f'{"Open" if is_open else "Close"} soul buff')
        self.screenshot()
        area = self.get_area_image(self.I_SOUL)
        if not area:
            logger.warning('No soul buff')
            return None
        self.set_switch_area(area)
        if not self._toggle(is_open, 'soul'):
            logger.warning(f'{"Open" if is_open else "Close"} soul buff failed')

    def reject_invite(self):
        from tasks.Component.GeneralInvite.assets import GeneralInviteAssets as gia
        while 1:
            self.screenshot()
            if not (self.appear(gia.I_I_REJECT_1) or self.appear(gia.I_I_REJECT_2) or self.appear(gia.I_I_REJECT_3)):
                break
            if self.appear(gia.I_I_REJECT_3):
                self.click(gia.I_I_REJECT_3, 6)
                continue
            if self.appear(gia.I_I_REJECT_2):
                self.click(gia.I_I_REJECT_2, 6)
                continue
            if self.appear(gia.I_I_REJECT_1):
                self.click(gia.I_I_REJECT_1, 6)
                continue


if __name__ == '__main__':
    from module.config.config import Config
    from module.device.device import Device

    c = Config('oas1')
    d = Device(c)
    t = GeneralBuff(c, d)

    t.open_buff()
    # t.screenshot()
    #
    t.awake(is_open=True)
    t.soul(is_open=True)
    t.gold_50(is_open=False)
    t.gold_100(is_open=False)
    t.exp_50(is_open=True)
    t.exp_100(is_open=True)
