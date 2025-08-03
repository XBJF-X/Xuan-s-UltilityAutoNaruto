from datetime import timedelta

from utils.core.Task.BaseTask import BaseTask


class RenWuJiHuiSuo(BaseTask):

    def _execute(self):
        self.logger.info(f"开始执行")
        try:
            # 确定在主场景
            if not self.home():
                raise self.StepFailedError("无法回到[主场景]")
            self.logger.info("进入[奖励]界面")
            # 点击奖励图标
            self.click_and_wait({
                "type": "ELEMENT",
                "name": "主场景-奖励"
            })
            # 确认奖励界面出现
            self.detect_and_wait({
                "type": "SCENE",
                "name": "奖励"
            })
            self.logger.info("跳转至[任务集会所]")
            # 点击完成集会所任务-立刻前往
            if not self.click_and_search(
                    [
                        {"type": "ELEMENT", "name": "完成集会所任务-立刻前往"}
                    ],
                    [
                        {
                            "swipe": {
                                "start_coordinate": [1506, 340],
                                "end_coordinate": [344, 340],
                                "duration": 1
                            }
                        }
                    ],
                    2
            ):
                self._update_next_execute_time()
                raise self.EndEarly("跳转至[任务集会所]失败，可能已经完成")
            # 确认任务集会所界面出现
            self.detect_and_wait({
                "type": "SCENE",
                "name": "任务集会所"
            })
            self.logger.info("开始领取任务奖励")
            # 点掉所有的可领取
            while self.click_and_wait(
                    {
                        'type': "ELEMENT",
                        'name': "任务集会所-可领取"
                    },
                    wait_time=1.5
            ):
                # 如果少于3个，则点击领取会直接弹出恭喜你获得弹窗
                if self.detect_and_wait({
                    "type": "ELEMENT",
                    "name": "任务集会所-恭喜你获得"
                }, wait_time=0):
                    # 随便点一下，关掉弹窗
                    self.click_and_wait({
                        'type': "COORDINATE",
                        'coordinate': [800, 700]
                    })
                    # 这个时候不需要检测有没有一键领取所有奖励的弹窗了，可以直接下一次领取了
                    continue
                # 假如可领取的多于等于3个，会出现让你确认是否一键领取的弹窗，我们直接看看能不能点击确认
                # 能点击确认的话就说明出现了弹窗，那就按照多于三个的逻辑来
                if self.click_and_wait({
                    'type': "ELEMENT",
                    'name': "任务集会所-一键领取所有奖励-确定"
                }):
                    # 出现恭喜你获得弹窗
                    if self.detect_and_wait({
                        'type': "ELEMENT",
                        'name': "任务集会所-恭喜你获得"
                    }, wait_time=0):
                        # 随便点一下，关掉弹窗
                        self.click_and_wait({
                            'type': "COORDINATE",
                            'coordinate': [800, 700]
                        })
                        # 可以直接结束奖励领取的循环了
                        self.logger.info("一键领取所有奖励")
                        break

            self.logger.info("开始接取任务")
            # 先看看是不是已经领完了所有任务了
            if self.detect_and_wait({
                'type': "ELEMENT",
                'name': "任务集会所-今天所有任务已经领完"
            }):
                self._update_next_execute_time()
                raise self.EndEarly("今日任务已经领完，提前退出执行")

            task_sum = 0

            while not self.detect_and_search(
                    [
                        {'type': "ELEMENT", 'name': "任务集会所-任务栏满了"},
                        {'type': "ELEMENT", 'name': "任务集会所-今天所有任务已经领完"}
                    ],
                    [],
                3
            ):
                # 点掉所有的接取按钮，直到出现任务栏已满的提示
                while self.click_and_wait({
                    'type': "ELEMENT",
                    'name': "任务集会所-接取"
                }, wait_time=1.5):
                    if not self.click_and_search(
                            [
                                {'type': "ELEMENT", 'name': "任务集会所-接取-推荐小队"},
                                {'type': "COORDINATE", 'coordinate': [1224, 572]}
                            ],
                            [],
                            1
                    ):
                        raise self.StepFailedError("安排任务忍者失败")
                    # 出战
                    if not self.click_and_wait({
                        'type': "ELEMENT",
                        'name': "任务集会所-接取-出战"
                    }):
                        raise self.StepFailedError("出战失败")
                    # 检查任务栏是否已满
                    if self.detect_and_search(
                            [
                                {'type': "ELEMENT", 'name': "任务集会所-任务栏满了"},
                                {'type': "ELEMENT", 'name': "任务集会所-今天所有任务已经领完"}
                            ],
                            [],
                            5
                    ):
                        self._update_next_execute_time(delta=timedelta(hours=2))
                        raise self.EndEarly("任务栏已满/今日任务已经领完")
                    else:
                        task_sum += 1
                        self.logger.info(f"已接取 {task_sum} 个任务")
                if self.click_and_wait({
                    'type': "ELEMENT",
                    'name': "任务集会所-超影免费"
                }):
                    self.logger.info("刷新任务列表")
                else:
                    # 能接取的都接了，无法刷新，可以退出执行了
                    self._update_next_execute_time(delta=timedelta(hours=2))
                    raise self.EndEarly("无法刷新，提前退出执行")
            self._update_next_execute_time(delta=timedelta(hours=2))
        except self.StepFailedError as e:
            self.logger.error(e)
        except self.EndEarly as e:
            self.logger.warning(e)
        finally:
            self.home()
            self.logger.info(f"执行完毕")
            self.callback(self)
