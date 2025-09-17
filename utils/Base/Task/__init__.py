from .BenFuYaoSaiZhan import BenFuYaoSaiZhan
from .DengLuJiangLi import DengLuJiangLi
from .DianFengDuiJue import DianFengDuiJue
from .FengRaoZhiJian import FengRaoZhiJian
from .GaoJiRenZheZhaoMu import GaoJiRenZheZhaoMu
from .GengDuoWanFa import GengDuoWanFa
from .GouMaiTiLi import GouMaiTiLi
from .HaoYouTiLi import HaoYouTiLi
from .HuoYueDuJiangLi import HuoYueDuJiangLi
from .JinBiZhaoCai import JinBiZhaoCai
from .KuaFuYaoSaiZhan import KuaFuYaoSaiZhan
from .MaoXianFuBen import MaoXianFuBen
from .MeiRiFenXiang import MeiRiFenXiang
from .MeiRiShengChang import MeiRiShengChang
from .MeiYueQianDao import MeiYueQianDao
from .MeiZhouShengChang import MeiZhouShengChang
from .MiJingTanXian import MiJingTanXian
from .PaiHangBangDianZan import PaiHangBangDianZan
from .PanRenLaiXi import PanRenLaiXi
from .PuTongRenZheZhaoMu import PuTongRenZheZhaoMu
from .QingBaoZhan import QingBaoZhan
from .QingKongYouJian import QingKongYouJian
from .RenFaTieDianZanFenXiang import RenFaTieDianZanFenXiang
from .RenWuJiHuiSuo import RenWuJiHuiSuo
from .SaiJiShengChang import SaiJiShengChang
from .ShangChengJiangLi import ShangChengJiangLi
from .ShengCunTiaoZhan import ShengCunTiaoZhan
from .TianDiZhanChang import TianDiZhanChang
from .TuanBen import TuanBen
from .WuChaBieYuXuanSai import WuChaBieYuXuanSai
from .XiaoDuiTuXi import XiaoDuiTuXi
from .XiuXingZhiLu import XiuXingZhiLu
from .YiLeWaiMai import YiLeWaiMai
from .ZhuangBeiHeCheng import ZhuangBeiHeCheng
from .ZhuiJiXiaoZuZhi import ZhuiJiXiaoZuZhi
from .ZuZhiQiFu import ZuZhiQiFu
from .ZuZhiZhengBa import ZuZhiZhengBa

TASK_TYPE_MAP = {
    '登录奖励': DengLuJiangLi,
    "排行榜点赞": PaiHangBangDianZan,
    "每月签到": MeiYueQianDao,
    '购买体力': GouMaiTiLi,
    '金币招财': JinBiZhaoCai,
    '小队突袭': XiaoDuiTuXi,
    '组织祈福': ZuZhiQiFu,
    '好友体力': HaoYouTiLi,
    '普通忍者招募': PuTongRenZheZhaoMu,
    '每日分享': MeiRiFenXiang,
    '丰饶之间': FengRaoZhiJian,
    '任务集会所': RenWuJiHuiSuo,
    "一乐外卖": YiLeWaiMai,
    "每日胜场": MeiRiShengChang,
    '生存挑战': ShengCunTiaoZhan,
    '秘境探险': MiJingTanXian,
    '商城奖励': ShangChengJiangLi,
    '情报站': QingBaoZhan,
    '冒险副本': MaoXianFuBen,
    '活跃度奖励': HuoYueDuJiangLi,
    '清空邮件': QingKongYouJian,

    '修行之路': XiuXingZhiLu,
    "每周胜场": MeiZhouShengChang,
    "忍法帖点赞分享": RenFaTieDianZanFenXiang,
    '更多玩法': GengDuoWanFa,
    '团本': TuanBen,
    '本服要塞战': BenFuYaoSaiZhan,
    '叛忍来袭': PanRenLaiXi,
    '天地战场': TianDiZhanChang,
    '追击晓组织': ZhuiJiXiaoZuZhi,

    '跨服要塞战': KuaFuYaoSaiZhan,
    '巅峰对决': DianFengDuiJue,
    '组织争霸': ZuZhiZhengBa,
    "赛季胜场": SaiJiShengChang,

    '装备合成': ZhuangBeiHeCheng,
    '高级忍者招募': GaoJiRenZheZhaoMu,

    '无差别预选赛': WuChaBieYuXuanSai,
}

TASK_NAME_CN2EN_MAP = {
    '登录奖励': "DengLuJiangLi",
    "排行榜点赞": "PaiHangBangDianZan",
    "每月签到": "MeiYueQianDao",
    '购买体力': "GouMaiTiLi",
    '金币招财': "JinBiZhaoCai",
    '小队突袭': "XiaoDuiTuXi",
    '组织祈福': "ZuZhiQiFu",
    '好友体力': "HaoYouTiLi",
    '普通忍者招募': "PuTongRenZheZhaoMu",
    '每日分享': "MeiRiFenXiang",
    '丰饶之间': "FengRaoZhiJian",
    '任务集会所': "RenWuJiHuiSuo",
    "一乐外卖": "YiLeWaiMai",
    "每日胜场": "MeiRiShengChang",
    '生存挑战': "ShengCunTiaoZhan",
    '商城奖励': "ShangChengJiangLi",
    '秘境探险': "MiJingTanXian",
    '情报站': "QingBaoZhan",
    '冒险副本': "MaoXianFuBen",
    '活跃度奖励': "HuoYueDuJiangLi",
    '清空邮件': "QingKongYouJian",

    '修行之路': "XiuXingZhiLu",
    "每周胜场": "MeiZhouShengChang",
    "忍法帖点赞分享": "RenFaTieDianZanFenXiang",
    '更多玩法': "GengDuoWanFa",
    '团本': "TuanBen",
    '本服要塞战': "BenFuYaoSaiZhan",
    '叛忍来袭': "PanRenLaiXi",
    '天地战场': "TianDiZhanChang",
    '追击晓组织': "ZhuiJiXiaoZuZhi",

    '跨服要塞战': "KuaFuYaoSaiZhan",
    '巅峰对决': "DianFengDuiJue",
    '组织争霸': "ZuZhiZhengBa",
    "赛季胜场": "SaiJiShengChang",

    '装备合成': "ZhuangBeiHeCheng",
    '高级忍者招募': "GaoJiRenZheZhaoMu",
}