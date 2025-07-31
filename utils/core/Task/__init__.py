from .ChongQiYouXi import ChongQiYouXi
from .DengLuJiangLi import DengLuJiangLi
from .FengRaoZhiJian import FengRaoZhiJian
from .GaoJiRenZheZhaoMu import GaoJiRenZheZhaoMu
from .GengDuoWanFa import GengDuoWanFa
from .GouMaiTiLi import GouMaiTiLi
from .HaoYouTiLi import HaoYouTiLi
from .HuoYueDuJiangLi import HuoYueDuJiangLi
from .JinBiZhaoCai import JinBiZhaoCai
from .MaoXianFuBen import MaoXianFuBen
from .MeiRiFenXiang import MeiRiFenXiang
from .MeiRiShengChang import MeiRiShengChang
from .MeiYueQianDao import MeiYueQianDao
from .MeiZhouShengChang import MeiZhouShengChang
from .MiJingTanXian import MiJingTanXian
from .PaiHangBangDianZan import PaiHangBangDianZan
from .PuTongRenZheZhaoMu import PuTongRenZheZhaoMu
from .QingBaoZhan import QingBaoZhan
from .QingKongYouJian import QingKongYouJian
from .RenFaTieDianZanFenXiang import RenFaTieDianZanFenXiang
from .RenWuJiHuiSuo import RenWuJiHuiSuo
from .SaiJiShengChang import SaiJiShengChang
from .ShengCunTiaoZhan import ShengCunTiaoZhan
from .TuanBen import TuanBen
from .XiaoDuiTuXi import XiaoDuiTuXi
from .XiuXingZhiLu import XiuXingZhiLu
from .YiLeWaiMai import YiLeWaiMai
from .ZuZhiQiFu import ZuZhiQiFu

TASK_TYPE_MAP = {
    '登录奖励': DengLuJiangLi,
    '丰饶之间': FengRaoZhiJian,
    '金币招财': JinBiZhaoCai,
    '好友体力': HaoYouTiLi,
    '购买体力': GouMaiTiLi,
    '组织祈福': ZuZhiQiFu,
    '高级忍者招募': GaoJiRenZheZhaoMu,
    '普通忍者招募': PuTongRenZheZhaoMu,
    '情报站': QingBaoZhan,
    '生存挑战': ShengCunTiaoZhan,
    '小队突袭': XiaoDuiTuXi,
    '清空邮件': QingKongYouJian,
    '任务集会所': RenWuJiHuiSuo,
    '冒险副本': MaoXianFuBen,
    '每日分享': MeiRiFenXiang,
    '更多玩法': GengDuoWanFa,
    '活跃度奖励': HuoYueDuJiangLi,
    '团本': TuanBen,
    '修行之路': XiuXingZhiLu,
    '秘境探险': MiJingTanXian,
    "每日胜场": MeiRiShengChang,
    "每周胜场": MeiZhouShengChang,
    "赛季胜场": SaiJiShengChang,
    "排行榜点赞": PaiHangBangDianZan,
    "一乐外卖": YiLeWaiMai,
    "每月签到": MeiYueQianDao,
    "忍法帖点赞分享": RenFaTieDianZanFenXiang,
    "重启游戏": ChongQiYouXi,
}
