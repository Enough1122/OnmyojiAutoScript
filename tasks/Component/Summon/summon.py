# This Python file uses the following encoding: utf-8
# @author runhey
# github https://github.com/runhey
import time

import random

from tasks.Component.Summon.assets import SummonAssets
from tasks.base_task import BaseTask
from module.atom.ocr import RuleOcr
from module.base.timer import Timer
from module.logger import logger
import re

# 抽卡结算界面（单抽/十连结果）的「点击继续」按钮没有模板可用，只能用 OCR 兜底。
# 该覆盖层没有返回键，DEFAULT_UNKNOWN_CLOSERS 全部无法命中，识别不到就会一直截图空转。
O_SUMMON_RESULT_CONTINUE = RuleOcr(
    roi=(520, 650, 240, 70), area=(560, 660, 160, 55),
    mode="Full", method="Default", keyword='点击继续', name='summon_result_continue')

class Summon(BaseTask, SummonAssets):


    def summon(self):
        """
        召唤, 就是随机画一个， 划线
        :return:
        """
        self.screenshot()
        random_swipe = random.randint(0, 3)
        target_swipe = None
        match random_swipe:
            case 0: target_swipe = self.S_RANDOM_SWIPE_1
            case 1: target_swipe = self.S_RANDOM_SWIPE_2
            case 2: target_swipe = self.S_RANDOM_SWIPE_3
            case 3: target_swipe = self.S_RANDOM_SWIPE_4
            case _: target_swipe = self.S_RANDOM_SWIPE_1
        self.swipe(target_swipe, interval=0.5)

    def summon_mystery_pattern(self):
        """
        每月神秘图案
        :return:
        """
        # 目前只测试了7月的，其他月份的我是根据截图描的，可能需要调整
        # 一月
        jan = [(400, 119), (406, 525), (862, 123), (864, 521), (402, 121)]
        # 二月、八月
        febAndAug = [(450, 105), (453, 525)]
        # 三月、九月
        marAndSep = [(390, 304), (886, 302)]
        # 四月、十月
        aprAndOct = [(402, 526), (862, 125)]
        # 五月、十一月
        mayAndNov = [(414, 207), (648, 550), (870, 209)]
        # 六月、十二月
        junAndDec = [(413, 138), (850, 133), (856, 226), (415, 239), (416, 140), (531, 136), (535, 590), (791, 586),
                     (760, 131)]
        # 七月
        jul = [(418, 124), (421, 504), (853, 511), (855, 128)]
        # 月份字典
        month_dict = {
            1: jan,
            2: febAndAug,
            3: marAndSep,
            4: aprAndOct,
            5: mayAndNov,
            6: junAndDec,
            7: jul,
            8: febAndAug,
            9: marAndSep,
            10: aprAndOct,
            11: mayAndNov,
            12: junAndDec
        }
        # 获取当前月份
        current_month = time.localtime().tm_mon
        current_pattern = month_dict.get(current_month, None)
        if current_pattern is None:
            logger.warning(f'不支持的月份: {current_month}')
            return
        self.screenshot()
        self.device.draw_adb(current_pattern)



    def summon_one(self,draw_mystery_pattern=False):
        """
        确保在召唤界面,每日召唤一次
        召唤结束后回到 召唤主界面
        :return:
        """
        logger.info('Summon one')
        self.wait_until_appear(self.I_BLUE_TICKET)
        # 只抽一次：外层循环只负责重试 OCR 不确定的门票数，成功抽完必须返回。
        # 历史 bug：logger.info('Summon one success') 缩进在 while True 内，
        # 导致抽完立刻再抽，“每日一抽”变成连续抽卡，并把结算界面留在屏幕上。
        for _ in range(5):
            ticket_info = self.O_ONE_TICKET.ocr(self.device.image)
            # 处理 None 和空字符串
            if ticket_info is None or ticket_info == '':
                ticket_info = 0
            else:
                # 使用正则表达式提取字符串中的数字
                match = re.search(r'\d+', ticket_info)
                if match:
                    ticket_info = int(match.group())
                else:
                    logger.warning(f'Invalid ticket_info value: {ticket_info}, retry OCR')
                    self.screenshot()
                    continue
            if ticket_info <= 0:
                logger.warning('There is no any one blue ticket')
                return
            break
        else:
            logger.warning('Cannot read one-ticket count, skip summon')
            return

        # 某些情况下滑动异常
        self.S_RANDOM_SWIPE_1.name = 'S_RANDOM_SWIPE'
        self.S_RANDOM_SWIPE_2.name = 'S_RANDOM_SWIPE'
        self.S_RANDOM_SWIPE_3.name = 'S_RANDOM_SWIPE'
        self.S_RANDOM_SWIPE_4.name = 'S_RANDOM_SWIPE'
        while 1:
            self.screenshot()
            if self.appear(self.I_ONE_TICKET):
                break
            if self.appear_then_click(self.I_BLUE_TICKET, interval=1):
                continue

        # 画一张票
        time.sleep(0.5)
        confirm_timer = Timer(30).start()
        while 1:
            self.screenshot()
            if self.appear(self.I_SM_CONFIRM, interval=0.6):
                self.ui_click_until_disappear(self.I_SM_CONFIRM)
                break
            if self.appear(self.I_SM_CONFIRM_2, interval=0.6):
                self.ui_click_until_disappear(self.I_SM_CONFIRM_2)
                break
            # 活动版召唤（如「飞驰天地·此心寻义」）点掉免费次数 + 画符后直接进结算覆盖层，
            # 没有单抽/十连确认按钮。这里不处理就会在动画和结算屏上什么都匹配不到，
            # 60s 后触发 GameStuckError（2026-11-03 01:13:06 实测）。
            if self.ocr_appear_click(O_SUMMON_RESULT_CONTINUE, interval=1.0):
                break
            if self.appear(self.I_ONE_TICKET, interval=1):
                # 某些时候会点击到 “语言召唤”
                if self.appear_then_click(self.I_UI_CANCEL, interval=0.8):
                    continue
                if draw_mystery_pattern:
                    self.summon_mystery_pattern()
                else:
                    self.summon()
                continue
            if confirm_timer.reached():
                logger.warning('Summon confirm not found in 30s, stop summon one')
                return
        if not self.wait_summon_result_finish():
            logger.warning('Summon result page did not finish, stop summon one')
            return
        logger.info('Summon one success')

    def wait_summon_result_finish(self, timeout: float = 60) -> bool:
        """等待抽卡结算界面结束，回到召唤主界面。

        单抽/十连的结算界面（「点击继续」）没有模板可匹配，用 OCR 兜底点击；
        识别不到时必须带超时退出，否则一直截图空转会在 60s 后触发 GameStuckError。

        Args:
            timeout: 最长等待时间，单位秒。

        Returns:
            是否回到召唤主界面。
        """
        timer = Timer(timeout).start()
        while not timer.reached():
            self.screenshot()
            if self.appear(self.I_ONE_TICKET, interval=1):
                return True
            if self.appear_then_click(self.I_SM_CONFIRM, interval=0.8):
                continue
            if self.appear_then_click(self.I_SM_CONFIRM_2, interval=0.8):
                continue
            if self.ocr_appear_click(O_SUMMON_RESULT_CONTINUE, interval=1.0):
                continue
            if self.appear_then_click(self.I_UI_CANCEL, interval=0.8):
                continue
            # 活动版召唤页（如「飞驰天地·此心寻义」）没有「单抽」按钮，抽完只会回到
            # 带蓝票大按钮的召唤主界面，I_ONE_TICKET 永远不命中。2026-11-03 01:10:38
            # 的帧上蓝票模板 0.902 命中、单抽模板只有 0.634，因此用蓝票判断已回主界面。
            if self.appear(self.I_BLUE_TICKET):
                return True
        logger.warning('Wait summon result finish timeout')
        return False


    def back_summon_main(self):
        """
        返回召唤主界面
        :return:
        """
        while 1:
            self.screenshot()
            if self.appear(self.I_BLUE_TICKET):
                break
            if self.appear_then_click(self.I_UI_BACK_YELLOW):
                continue
            if self.appear_then_click(self.I_UI_BACK_YELLOW):
                continue

