# This Python file uses the following encoding: utf-8
# @author runhey
# github https://github.com/runhey
import time
import numpy as np
import random
from enum import Enum
from cached_property import cached_property
from datetime import timedelta, datetime

from tasks.Component.SwitchSoul.switch_soul import SwitchSoul
from tasks.Component.GeneralRoom.general_room import GeneralRoom
from tasks.Component.GeneralInvite.general_invite import GeneralInvite
from tasks.Component.ReplaceShikigami.replace_shikigami import ReplaceShikigami
from tasks.Exploration.assets import ExplorationAssets
from tasks.Exploration.config import ChooseRarity, AutoRotate, AttackNumber, UpType, UserStatus
from tasks.Component.GeneralBattle.general_battle import GeneralBattle
from tasks.GameUi.game_ui import GameUi
from tasks.GameUi.page import page_shikigami_records, page_main, page_exploration, page_realm_raid, page_summon
import tasks.Exploration.page as pages
from tasks.RealmRaid.script_task import ScriptTask as RealmRaidScriptTask
from tasks.RealmRaid.assets import RealmRaidAssets
from tasks.MemoryScrolls.assets import MemoryScrollsAssets
from tasks.Utils.config_enum import ShikigamiClass

from module.logger import logger
from module.base.timer import Timer
from module.exception import RequestHumanTakeover, TaskEnd, GameStuckError
from module.atom.image_grid import ImageGrid
from module.atom.animate import RuleAnimate
from module.base.utils import load_image

class Scene(Enum):
    UNKNOWN = 0  #
    WORLD = 1  # 探索大世界
    ENTRANCE = 2  # 入口弹窗
    MAIN = 3  # 探索里面
    BATTLE_PREPARE = 4  # 战斗准备
    BATTLE_FIGHTING = 5  # 战斗中
    TEAM = 6  # 组队




class BaseExploration(GameUi, GeneralBattle, GeneralRoom, GeneralInvite, ReplaceShikigami, SwitchSoul, ExplorationAssets,
                       RealmRaidAssets, MemoryScrollsAssets):
    minions_cnt = 0
    # 小绘卷满 50 的自检节流：任务在 28 章连打时 MemoryScrolls 常被排程饿死（优先级最低，Filter 规则里
    # 排在 Exploration 之后），exploration 的 next_run 就永远没人改到明天，于是 50 片之后还在刷。
    # 这里自己每 N 分钟去绘卷页看一次，满了就按 memory_scrolls_finish.next_exploration_time 排明天。
    scrolls_checked_at = 0.0
    scrolls_full = False
    SCROLLS_CHECK_INTERVAL = 900

    @cached_property
    def _config(self):
        self.config.exploration.general_battle_config.lock_team_enable = True
        limit_time = self.config.exploration.exploration_config.limit_time
        self.limit_time: timedelta = timedelta(
            hours=limit_time.hour,
            minutes=limit_time.minute,
            seconds=limit_time.second
        )
        return self.config.model.exploration

    @cached_property
    def _match_end(self):
        return RuleAnimate(self.I_SWIPE_END)

    def is_swipe_unchanged(self, before_image, after_image, threshold: float = 15) -> bool:
        # 对比滑屏前后中上部背景区域(避开顶部跑马灯、下方小怪挑战图标及最右侧浮动鬼火)，变化很小说明地图已滑到尽头。
        swipe_check_roi = (250, 140, 800, 90)
        before = self.I_SWIPE_END.corp(before_image, swipe_check_roi)
        after = self.I_SWIPE_END.corp(after_image, swipe_check_roi)
        diff = np.mean(np.abs(before.astype(np.int16) - after.astype(np.int16)))
        logger.info(f'Swipe end area diff: {diff:.2f}')
        return diff <= threshold

    def get_current_scene(self, reuse_screenshot: bool = True) -> Scene:
        if not reuse_screenshot:
            self.screenshot()

        if self.appear(self.I_CHECK_EXPLORATION) and not self.appear(self.I_E_SETTINGS_BUTTON):
            return Scene.WORLD
        elif self.appear(self.I_E_EXPLORATION_CLICK):
            return Scene.ENTRANCE
        elif self.appear(self.I_E_SETTINGS_BUTTON) or self.appear(self.I_E_AUTO_ROTATE_ON) or self.appear(self.I_E_AUTO_ROTATE_OFF):
            return Scene.MAIN
        elif self.is_in_prepare():
            return Scene.BATTLE_PREPARE
        elif self.is_in_battle():
            return Scene.BATTLE_FIGHTING
        elif self.is_in_room() or self.appear(self.I_CREATE_ENSURE):
            return Scene.TEAM

        logger.info("Unknown scene")
        return Scene.UNKNOWN

    def pre_process(self):
        explorationConfig = self._config
        if explorationConfig.switch_soul_config.enable:
            self.goto_page(page_shikigami_records)
            self.run_switch_soul(explorationConfig.switch_soul_config.switch_group_team)

        if explorationConfig.switch_soul_config.enable_switch_by_name:
            self.goto_page(page_shikigami_records)
            self.run_switch_soul_by_name(explorationConfig.switch_soul_config.group_name,
                                         explorationConfig.switch_soul_config.team_name)

        # 开启加成
        con = self.config.exploration.exploration_config
        if con.buff_gold_50_click or con.buff_gold_100_click or con.buff_exp_50_click or con.buff_exp_100_click:
            self.goto_page(page_main)
            self.open_buff()
            if con.buff_gold_50_click:
                self.gold_50()
            if con.buff_gold_100_click:
                self.gold_100()
            if con.buff_exp_50_click:
                self.exp_50()
            if con.buff_exp_100_click:
                self.exp_100()
            self.close_buff()

        # 探索页面（大地图始终处于主线/玩法 tab 之一，裸 page_exploration 永远被 prio 60 的 tab 页遮蔽、
        # 无法作为当前页抵达，故直接进入主线 tab）
        self.goto_page(pages.page_mainline)

    def post_process(self):
        self.wait_until_stable(self.I_UI_BACK_RED)
        if self.appear(self.I_UI_BACK_RED):
            self.ui_click_until_disappear(self.I_UI_BACK_RED)
        self.goto_page(page_main)
        con = self._config.exploration_config
        if con.buff_gold_50_click or con.buff_gold_100_click or con.buff_exp_50_click or con.buff_exp_100_click:
            self.open_buff()
            self.gold_50(is_open=False)
            self.gold_100(is_open=False)
            self.exp_50(is_open=False)
            self.exp_100(is_open=False)
            self.close_buff()
        self.set_next_run(task='Exploration', success=True, finish=False)
        raise TaskEnd

    # 打开指定的章节：
    def open_expect_level(self):
        # 选关依赖主线 tab 右侧的章节列表（I_E_EXPLORATION_CLICK + 章节名 OCR）。
        # 探索大地图常驻「主线/玩法」之一，若停在玩法 tab 不选回主线，右边会是御魂/今日掉落等模块名，
        # I_E_EXPLORATION_CLICK 不出现、OCR 交集为空 → 一直滑屏卡死。故进选关前无条件确保主线 tab。
        self.goto_page(pages.page_mainline)

        swipeCount = 0
        while 1:
            # 探索的 config
            explorationConfig = self.config.exploration

            # 判断有无目标章节
            self.screenshot()
            # 获取当前章节名
            results = self.O_E_EXPLORATION_LEVEL_NUMBER.detect_and_ocr(self.device.image)
            text1 = [result.ocr_text for result in results]
            # https://github.com/runhey/OnmyojiAutoScript/issues/1540
            text1 = [text.replace("名", "第").replace("书", "第") for text in text1]
            # 判断当前章节有无目标章节
            result = set(text1).intersection({explorationConfig.exploration_config.exploration_level})
            # 有则跳出检测
            if self.appear(self.I_E_EXPLORATION_CLICK) or result and len(result) > 0:
                break
            if self.appear_then_click(self.I_UI_CONFIRM, interval=1):
                continue
            if self.appear_then_click(self.I_UI_CONFIRM_SAMLL, interval=1):
                continue
            self.device.click_record_clear()
            self.swipe(self.S_SWIPE_LEVEL_DOWN)
            swipeCount += 1
            debug_info = f"Swiped {swipeCount} times, current exploration level: {text1}"
            logger.info(debug_info)
            if swipeCount >= 15:
                raise GameStuckError(
                    f"Swiped too many times ({swipeCount}), seems stuck in exploration level selection"
                )
            time.sleep(1)

        # 选中对应章节
        while 1:
            self.screenshot()
            if self.appear_then_click(self.I_UI_CONFIRM, interval=1):
                continue
            if self.appear_then_click(self.I_UI_CONFIRM_SAMLL, interval=1):
                continue
            self.O_E_EXPLORATION_LEVEL_NUMBER.keyword = explorationConfig.exploration_config.exploration_level
            if self.ocr_appear_click(self.O_E_EXPLORATION_LEVEL_NUMBER):
                self.wait_until_appear(self.I_E_EXPLORATION_CLICK, wait_time=3)
            if self.appear(self.I_E_EXPLORATION_CLICK):
                break
            if self.is_in_room():
                break

        return True

    # 候补：
    def enter_settings_and_do_operations(self):
        # 打开设置
        while 1:
            self.screenshot()
            if self.appear(self.I_E_OPEN_SETTINGS):
                logger.info("Open settings")
                break
            if self.is_in_battle():
                logger.warning('Opening settings failed due to now in battle')
                return
            if (self.appear_then_click(self.I_UI_CONFIRM, interval=1)
                    or self.appear_then_click(self.I_UI_CONFIRM_SAMLL, interval=1)):
                continue
            if self.click(self.C_CLICK_SETTINGS, interval=2):
                continue

        # 候补出战数量识别
        self.screenshot()
        if not self.appear(self.I_E_OPEN_SETTINGS):
            logger.warning('Opening settings failed due to now in battle')
            return
        cu, res, total = self.O_E_ALTERNATE_NUMBER.ocr(self.device.image)
        if cu >= 40:
            logger.info("Alternate number is enough")
            self.ui_click_until_disappear(self.I_E_SURE_BUTTON)
            return
        else:
            self.add_shiki()

    # 添加式神
    def add_shiki(self, screenshot=True):
        if screenshot:
            self.screenshot()
            if not self.appear(self.I_E_OPEN_SETTINGS):
                logger.warning('Opening settings failed due to now in battle')
                return

        # 先点候补式神区域，再切换稀有度，避免点击失败
        self.click(self.C_CLICK_STANDBY_TEAM)

        choose_rarity = self._config.exploration_config.choose_rarity
        rarity = ShikigamiClass.N if choose_rarity == ChooseRarity.N else ShikigamiClass.MATERIAL
        self.switch_shikigami_class(rarity)

        # 移动至未候补的狗粮
        while 1:
            # 慢一点
            time.sleep(0.5)
            self.screenshot()
            if not self.appear(self.I_E_OPEN_SETTINGS):
                logger.warning('Opening settings failed due to now in battle')
                return
            if self.appear(self.I_E_RATATE_EXSIT):
                self.swipe(self.S_SWIPE_SHIKI_TO_LEFT)
            else:
                break
        while 1:
            # 候补出战数量识别
            self.screenshot()
            if not self.appear(self.I_E_OPEN_SETTINGS):
                logger.warning('Opening settings failed due to now in battle')
                return
            cu, res, total = self.O_E_ALTERNATE_NUMBER.ocr(self.device.image)
            if cu >= 40:
                break
            self.swipe(self.S_SWIPE_SHIKI_TO_LEFT_ONE)
            # 慢一点
            time.sleep(0.5)
            self.screenshot()
            self.click(self.L_ROTATE_1)
            self.device.click_record_clear()

        self.appear_then_click(self.I_E_SURE_BUTTON)

    # 找up按钮
    def search_up_fight(self, up_type: UpType = None):
        if up_type is None:
            up_type = self._config.exploration_config.up_type
        
        # 1. 如果选择了特定的 UP 类型 (比如达摩)
        if up_type != UpType.ALL:
            match up_type:
                case UpType.EXP:
                    find_flag = self.I_UP_EXP
                case UpType.COIN:
                    find_flag = self.I_UP_COIN
                case UpType.DARUMAA:
                    find_flag = self.I_UP_DARUMA
                case _:
                    find_flag = self.I_UP_EXP
            
            # 尝试寻找 UP 图标
            if self.appear(find_flag):
                # 获取 UP 图标的坐标和中心点
                x, y, w, h = find_flag.roi_front
                x_center, y_center = find_flag.front_center()
                
                logger.info(f'Found up type: {up_type} at {find_flag.roi_front}')

                # 缩小搜索范围 (ROI)
                # 原来左右各扩 160-200，太宽了容易甚至把隔壁怪算进来
                # 现在改为左右各扩 50-80，强制只找垂直线附近的战斗图标
                roi_back_y = max(0, y - 300)      # 向上找300像素
                roi_back_h = y - 20 - roi_back_y  #直到UP图标上方20像素截止
                
                # 左右范围缩窄：防止误触旁边的怪
                roi_back_x = max(0, x - 60)       
                roi_back_w = min(1280, x + w + 60) - roi_back_x
                
                logger.info(f'Searching sword icon in narrowed area: {roi_back_x, roi_back_y, roi_back_w, roi_back_h}')
                
                matches = self.I_NORMAL_BATTLE_BUTTON.match_all(
                    image=self.device.image,
                    threshold=0.9,
                    roi=[roi_back_x, roi_back_y, roi_back_w, roi_back_h]
                )
                
                if matches:
                    distances = []
                    for match in matches:
                        # 这里假设 match[1], match[2] 是 x, y
                        x_match = match[1] + match[3] / 2  # 战斗图标中心 X
                        y_match = match[2] + match[4] / 2  # 战斗图标中心 Y
                        
                        # 这样能完美避开“距离很近但属于隔壁怪”的情况
                        x_diff = abs(x_center - x_match)
                        y_diff = abs(y_center - y_match)
                        weighted_distance = (x_diff * 3) + y_diff
                        
                        distances.append((weighted_distance, match))
                    
                    # 按加权距离排序，取最正对着的一个
                    distances.sort(key=lambda x: x[0], reverse=False)
                    match = distances[0][1]
                    
                    roi_front = list(match[1:])  # x,y,w,h
                    self.I_NORMAL_BATTLE_BUTTON.roi_front = roi_front
                    logger.info(f"Target locked: sword at {roi_front} (aligned with UP icon)")
                    return self.I_NORMAL_BATTLE_BUTTON
            # 没找到 UP 图标或对应战斗图标，返回 None 让外层逻辑去处理(滑动或退出)
            return None

        # 2. 如果是默认情况 (UpType.ALL)，则只要有怪就打
        self.I_NORMAL_BATTLE_BUTTON.roi_back = (0, 0, 1279, 719)
        if self.appear(self.I_NORMAL_BATTLE_BUTTON):
            return self.I_NORMAL_BATTLE_BUTTON
            
        return None

    # 突破票只在每轮探索开始时探一次：探索过程中票数根本不会变（票只来自突破胜利和日常，
    # 都不在探索里发生），中途反复跳去突破页只会白花 6 秒并把地图进度重置。
    ticket_probed: bool = False
    ticket_probe_last: int = -1

    def read_realm_raid_ticket(self) -> int:
        """跳去突破页读一次突破票，失败返回 -1。

        2026-11-11 起探索大地图右上角已经不再显示突破票：
        O_REALM_RAID_NUMBER 读到的是顶部跑马灯的数字（实测稳定 247），
        O_REALM_RAID_NUMBER1 会把 21/30 读成 122/30。
        突破页的 O_NUMBER(1143,13,80,39) 读数一直准确（20/30、21/30、19/30）。
        """
        try:
            # 从探索大地图直接走 page_exploration -> page_realm_raid，不经庭院，
            # 省一次来回；回来同理走 page_realm_raid -> page_exploration。
            self.goto_page(page_realm_raid)
            cu, res, total = self.O_NUMBER.ocr(self.device.image)
            logger.info(f'[TicketProbe] raid page: {cu}/{total}')
            self.goto_page(page_exploration)
            return cu
        except Exception as e:
            logger.warning(f'[TicketProbe] raid page unreachable ({e}), fall back to world map ocr')
            try:
                self.goto_page(page_exploration)
            except Exception:
                pass
            return -1

    def probe_scrolls_full(self) -> None:
        """自己去看小绘卷是否满 50；满了就把探索排到明天并当场结束本轮。

        为什么要探索自己管这件事：负责查绘卷的 MemoryScrolls 在
        ConfigManual.SCHEDULER_PRIORITY 里排在最后一个，而 schedule_rule=Filter
        就是照那张表排序的。Exploration 一开跑就长期占队首，MemoryScrolls
        永远选不上（2026-11-11 从 14:25 一直被饿到 18:57），exploration 的
        next_run 就没人改到明天，于是 50 片之后还在继续刷。

        代价是要绕一趟召唤页的绘卷面板（约 15 秒）再回来，探索地图进度会重置，
        所以用 SCROLLS_CHECK_INTERVAL 节流。
        """
        finish_con = self.config.memory_scrolls.memory_scrolls_finish
        if not finish_con.auto_finish_exploration:
            return
        # 只在单人模式自检：组队时队长跑回召唤页会把队友晾在副本里，成员更是不能乱走
        if self._config.exploration_config.user_status != UserStatus.ALONE:
            return
        now = time.time()
        if self.scrolls_checked_at and now - self.scrolls_checked_at < self.SCROLLS_CHECK_INTERVAL:
            return
        self.scrolls_checked_at = now

        try:
            self.goto_page(page_summon)
            if not self.wait_until_appear(self.I_MS_ENTER, wait_time=10):
                logger.warning('[ScrollsProbe] memory scrolls entry not found, skip this check')
                return
            scroll_timer = Timer(15)
            scroll_timer.start()
            while 1:
                self.screenshot()
                if self.appear(self.I_MS_FRAGMENT_S):
                    break
                # 周年庆等时期会使用双绘卷
                if self.appear_then_click(self.I_MS_DOUBLE_SCROLLS_ENTER, interval=1):
                    continue
                if self.appear_then_click(self.I_MS_ENTER, interval=1):
                    continue
                if scroll_timer.reached():
                    logger.warning('[ScrollsProbe] memory scrolls panel never showed up, skip this check')
                    return
        except Exception as e:
            logger.warning(f'[ScrollsProbe] open memory scrolls failed ({e}), skip this check')
            return

        full = self.appear(self.I_MS_FRAGMENT_S_50, threshold=0.95)
        logger.info(f'[ScrollsProbe] small memory scrolls full: {full}')
        if not full:
            try:
                self.goto_page(page_exploration)
            except Exception:
                pass
            return

        logger.info('Small Memory Scrolls fragments reached 50, end exploration and plan tomorrow')
        self.scrolls_full = True
        if self.appear(self.I_RED_CLOSE):
            self.ui_click_until_disappear(self.I_RED_CLOSE)
        if self.appear(self.I_UI_CANCEL):
            self.ui_click_until_disappear(self.I_UI_CANCEL)
        if self.appear(self.I_UI_CANCEL_SAMLL):
            self.ui_click_until_disappear(self.I_UI_CANCEL_SAMLL)
        self.goto_page(page_main)
        con = self._config.exploration_config
        if con.buff_gold_50_click or con.buff_gold_100_click or con.buff_exp_50_click or con.buff_exp_100_click:
            self.open_buff()
            self.gold_50(is_open=False)
            self.gold_100(is_open=False)
            self.exp_50(is_open=False)
            self.exp_100(is_open=False)
            self.close_buff()
        self.custom_next_run(task='Exploration',
                             custom_time=finish_con.next_exploration_time,
                             time_delta=1)
        raise TaskEnd

    def activate_realm_raid(self, con_scrolls, con) -> None:
        # 判断是否开启突破票检测
        if not con_scrolls.scrolls_enable:
            return
        # 优先去突破页读真票数；读不到才退回大地图 OCR（旧逻辑，可能误读成 247 / 122）
        cu = self.ticket_probe_last
        if not self.ticket_probed:
            cu = self.read_realm_raid_ticket()
            self.ticket_probed = True
            if cu >= 0:
                self.ticket_probe_last = cu
        if cu < 0:
            if self.appear(self.I_E_EXPLORATION_CLICK) and self.appear(self.I_EXP_CREATE_TEAM):
                cu, res, total = self.O_REALM_RAID_NUMBER1.ocr(self.device.image)
            else:
                cu, res, total = self.O_REALM_RAID_NUMBER.ocr(self.device.image)
            logger.info(f'[TicketProbe] world map ocr: {cu}/{total}')
        # 判断突破票数量
        if cu < con_scrolls.scrolls_threshold:
            return

        # 关闭加成
        if self.appear(self.I_RED_CLOSE):
            self.ui_click_until_disappear(self.I_RED_CLOSE)
        if self.appear(self.I_UI_CANCEL):
            self.ui_click_until_disappear(self.I_UI_CANCEL)
        if self.appear(self.I_UI_CANCEL_SAMLL):
            self.ui_click_until_disappear(self.I_UI_CANCEL_SAMLL)
        self.goto_page(page_main)
        if con.buff_gold_50_click or con.buff_gold_100_click or con.buff_exp_50_click or con.buff_exp_100_click:
            self.open_buff()
            self.gold_50(is_open=False)
            self.gold_100(is_open=False)
            self.exp_50(is_open=False)
            self.exp_100(is_open=False)
            self.close_buff()

        # 设置下次执行行时间
        logger.info("RealmRaid and Exploration  set_next_run !")
        next_run = datetime.now() + con_scrolls.scrolls_cd
        self.set_next_run(task='Exploration', success=False, finish=False, target=next_run)
        self.set_next_run(task='RealmRaid', success=False, finish=False, server=False, target=datetime.now())
        self.set_next_run(task='MemoryScrolls', success=False, finish=False, target=datetime.now())
        raise TaskEnd

    #
    def check_exit(self) -> bool:
        # True 表示要退出这个任务
        if self.minions_cnt >= self._config.exploration_config.minions_cnt:
            logger.info('Minions count is enough, exit')
            return True
        if datetime.now() - self.start_time >= self.limit_time:
            logger.info('Exploration time limit out')
            return True
        # 满了会直接 raise TaskEnd 出去；没满或跳过则继续看突破票
        self.probe_scrolls_full()
        self.activate_realm_raid(self._config.scrolls, self._config.exploration_config)
        return False

    def quit_explore(self):
        logger.info('Quit explore')
        self.device.click_record_remove(self.S_SWIPE_BACKGROUND_RIGHT.name)
        boss_timer = Timer(15)
        boss_timer.start()
        # click_yellow_button = 0 #用于保证只点一次左上返回按钮，不要直接触发连点回到主界面
        
        while 1:
            self.screenshot()
            
            # 探索章节标题界面
            if self.appear(self.I_UI_BACK_YELLOW) and self.appear(self.I_E_EXPLORATION_CLICK):
                break
            # 探索大世界界面
            if self.appear(self.I_CHECK_EXPLORATION) and not self.appear(self.I_E_SETTINGS_BUTTON):
                break
  
            # 防止BOSS打完箱子刚落地，脚本就手快点退出了
            if self.appear_then_click(self.I_BATTLE_REWARD, interval=1.5):
                logger.info("Found battle reward during exit, picking it up.")
                boss_timer.reset()
                continue

            if boss_timer.reached():
                logger.warning('Exit timeout, force clicking back button')
                boss_timer.reset()
                self.click(self.I_UI_BACK_BLUE)
                continue

            if self.appear_then_click(self.I_E_EXIT_CONFIRM, interval=0.8):
                continue
            if self.appear(self.I_BACK_YOLLOW):
                self.screenshot()
                # https://github.com/runhey/OnmyojiAutoScript/issues/1935
                if not self.appear(self.I_BACK_YOLLOW) or self.appear(self.I_E_EXPLORATION_CLICK):
                    continue
                is_main = (
                        self.appear(self.I_E_SETTINGS_BUTTON)
                        or self.appear(self.I_E_AUTO_ROTATE_ON)
                        or self.appear(self.I_E_AUTO_ROTATE_OFF)
                )
                if is_main and self.click(self.I_BACK_YOLLOW, interval=3.5):
                    continue
            
            if self.appear(self.I_EXPLORATION_TITLE) or self.appear(self.I_CHECK_EXPLORATION):
                continue

    def _hook_special_reward(self) -> bool:
        if self.appear(self.I_STATISTICS) and not self.appear(self.I_REWARD) and not self.appear(self.I_WIN):
            if self.appear_then_click(self.I_CONFIRM_CLOSE_DIFF_SOUL):
                return True
            self.click(self.C_RANDOM_CLICK, interval=1.5)
        return False

    def fire(self, button) -> bool:
        self.ui_click_until_disappear(button, interval=3)
        self.screenshot()
        if (self.appear(self.I_E_SETTINGS_BUTTON) or
                self.appear(self.I_E_AUTO_ROTATE_ON) or
                self.appear(self.I_E_AUTO_ROTATE_OFF)):
            # 如果还在探索说明，这个是显示滑动导致挑战按钮不在范围内
            logger.warning('Fire button disappear, but still in exploration')
            return False
        self.run_general_battle(self._config.general_battle_config)
        self.minions_cnt += 1
        return True

    def wait_world_stable(self) -> bool:
        """
        # 打开右边箭头 and https://github.com/runhey/OnmyojiAutoScript/pull/1589/
        https://github.com/runhey/OnmyojiAutoScript/issues/1588
        @return:
        """
        while 1:
            scene = self.get_current_scene(reuse_screenshot=False)
            if scene == Scene.WORLD and self.appear(self.I_EXP_ARROW_RIGHT):
                return True
            if scene == Scene.ENTRANCE:
                logger.warning('World scene unstable, possibly transient frame after paper doll collection')
                return False
            if self.appear_then_click(self.I_EXP_ARROW_LEFT, interval=2):
                continue


if __name__ == "__main__":
    from module.config.config import Config
    from module.device.device import Device

    config = Config('oas1')
    device = Device(config)
    t = BaseExploration(config, device)
    t.screenshot()

    # IMAGE_FILE = r"C:\Users\萌萌哒\Desktop\QQ20240818-163854.png"
    # image = load_image(IMAGE_FILE)
    # t.device.image = image
    while 1:
        # print(t.search_up_fight(UpType.EXP))
        t.screenshot()
        print(t.get_current_scene())
    from PIL import Image
    # Image.fromarray(t.device.image.astype(np.uint8)).show()
