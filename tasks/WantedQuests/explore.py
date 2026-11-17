import time
from time import sleep

from cached_property import cached_property

from module.atom.animate import RuleAnimate
from module.atom.image import RuleImage
from module.base.timer import Timer
from module.logger import logger
from tasks.Exploration.base import BaseExploration, Scene
from tasks.Exploration.version import HighLight


class ExploreWantedBoss(Exception):
    # 出现一种情况，要求的怪是仅仅最后的Boss，其他小怪不是
    pass


class WQExplore(BaseExploration, HighLight):
    _cnt_exploration: int = 0

    @cached_property
    def _match_end(self):
        return RuleAnimate(self.I_SWIPE_END)

    def explore(self, goto: RuleImage, num: int):
        logger.info(f'Start exploring with number: {num}')
        explore_init = False
        explore_only_boss: bool = True
        _cnt_exploration = 0
        search_fail_cnt = 0
        search_fail_timer = Timer(3.2)  # 这里设置的时间一定要大于S_SWIPE_BACKGROUND_RIGHT滑动的时间
        last_swipe_at = 0.0  # 上一次真正执行滑动的时刻，用来避免 interval 未到时的空滑被误判成地图到头
        # https://github.com/runhey/OnmyojiAutoScript/pull/1697 云景阆苑 皮肤
        from tasks.Component.Costume.config import MainType
        if self.config.model.global_game.costume_config.costume_main_type == MainType.COSTUME_MAIN_13:
            self.TEMPLATE_GIF.match = self.TEMPLATE_GIF.match_with_multi_scale
            logger.info("Costume '云景阆苑' detected, enable multi-scale matching for highlight")
        else:
            self.TEMPLATE_GIF.match = self.TEMPLATE_GIF.match_origin
        while 1:
            self.screenshot()
            if self.appear(self.I_UI_BACK_YELLOW) and self.appear(self.I_E_EXPLORATION_CLICK):
                break
            if self.appear_then_click(goto, interval=2):
                continue

        while 1:
            scene = self.get_current_scene(reuse_screenshot=False)
            # 进入探索
            if scene == Scene.ENTRANCE:
                if _cnt_exploration >= num:
                    logger.info('Execution exploration end')
                    # --退出到探索大世界--
                    self.ui_click(self.I_UI_BACK_YELLOW, stop=self.I_CHECK_EXPLORATION, interval=4, timeout=20)
                    if explore_only_boss:
                        raise ExploreWantedBoss
                    break
                # 20s 上限，超时点返回键清 stuck timer 并让主循环重判场景。
                if not self.ui_click(self.I_E_EXPLORATION_CLICK, stop=self.I_E_SETTINGS_BUTTON, timeout=20):
                    logger.warning('WQ explore ENTRANCE ui_click timeout, back to world')
                    self.appear_then_click(self.I_UI_BACK_YELLOW, interval=1)
                continue
            # 探索大世界
            elif scene == Scene.WORLD:
                self.wait_until_stable(
                    self.I_CHECK_EXPLORATION,
                    timer=Timer(limit=0.5, count=2),
                    timeout=Timer(2, count=10)
                )
                curr_scene = self.get_current_scene(reuse_screenshot=False)
                if curr_scene == Scene.WORLD and _cnt_exploration >= num:
                    logger.info('All Done')
                    break
                continue
            # 探索里面
            elif scene == Scene.MAIN:
                # if not explore_init:
                #     count = 0
                #     while count < 5:
                #         if self.appear(self.I_E_AUTO_ROTATE_ON):
                #             break
                #         if self.appear(self.I_E_AUTO_ROTATE_OFF, interval=1.5):
                #             self.click(self.I_E_AUTO_ROTATE_OFF)
                #             count += 1
                #     explore_init = True
                #     continue
                # 小纸人
                if self.appear(self.I_BATTLE_REWARD):
                    if self.ui_get_reward(self.I_BATTLE_REWARD):
                        continue
                # boss
                if self.appear(self.I_BOSS_BATTLE_BUTTON):
                    if self.fire(self.I_BOSS_BATTLE_BUTTON):
                        logger.info(f'Boss battle, minions cnt {self.minions_cnt}')
                        _cnt_exploration += 1
                        explore_only_boss = False
                    continue
                # 小怪
                if self.appear(self.TEMPLATE_GIF) and self.fire(self.TEMPLATE_GIF):
                    explore_only_boss = False
                    logger.info(f'Fight, minions cnt {self.minions_cnt}')
                    continue
                # 向后拉,寻找怪
                if search_fail_timer.reached():
                    search_fail_timer.reset()
                    if self._match_end.stable(self.device.image, refresh_after_stable=True):
                        _cnt_exploration += 1
                        self.quit_explore()
                        continue
                    # 这里不用 swipe(interval=3)：interval 未到时 swipe() 会静默跳过，
                    # 空滑的画面差异会被下面的到头判定误读。自己控制节奏，保证每次比较前真滑过。
                    if time.time() - last_swipe_at < 3.0:
                        continue
                    before_swipe = self.device.image
                    self.swipe(self.S_SWIPE_BACKGROUND_RIGHT)
                    last_swipe_at = time.time()
                    # 单次滑动不该计入连点，滑完立刻摘掉，避免累积到 10 次抛 GameTooManyClickError
                    self.device.click_record_remove(self.S_SWIPE_BACKGROUND_RIGHT.name)
                    # 滑动后复核画面：地图已到最右边界时，原逻辑会一直滑到自己被判连点
                    sleep(0.3)
                    self.screenshot()
                    unchanged = self.is_swipe_unchanged(before_swipe, self.device.image)
                    if unchanged:
                        sleep(0.3)
                        self.screenshot()
                        unchanged = self.is_swipe_unchanged(before_swipe, self.device.image)
                    if unchanged and self.get_current_scene() == Scene.MAIN:
                        logger.info('Wanted explore reached right boundary, quit exploration')
                        _cnt_exploration += 1
                        self.quit_explore()
                    continue
                if not search_fail_timer.started():
                    search_fail_timer.start()
            elif scene == Scene.BATTLE_PREPARE:
                self.ui_click_until_disappear(self.I_PREPARE_HIGHLIGHT, interval=0.5)
            elif scene == Scene.UNKNOWN:
                continue


if __name__ == '__main__':
    from module.config.config import Config
    from module.device.device import Device
    from tasks.WantedQuests.assets import WantedQuestsAssets

    config = Config('oas1')
    device = Device(config)
    t = WQExplore(config, device)
    t.explore(goto=WantedQuestsAssets.I_GOTO_1, num=2)
