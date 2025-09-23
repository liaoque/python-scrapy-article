# apps/ext_models/views.py

from rest_framework import viewsets
from rest_framework.permissions import AllowAny   # 新增
from rest_framework.authentication import SessionAuthentication, BasicAuthentication  # 可选
from django.utils.dateparse import parse_datetime, parse_date  # 新增
from django.utils import timezone  # 新增
from datetime import datetime, time  # 新增

from .models import MCls
from .serializers import MClsSerializer

from rest_framework import viewsets, permissions
from .models import MCls
from .serializers import MClsSerializer
from rest_framework.filters import OrderingFilter    # ← 关键


class MClsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    支持时间过滤：
      - open=2: 上个交易日 15:00  ~ 今天 07:00
      - open=1: 今天       07:00  ~ 今天 15:00
      - 若不传 open，则用 ?start=...&end=... 解析（日期或ISO时间）
    说明：
      - 项目 settings.py 中 USE_TZ=False，故以下时间均为本地(上海)朴素时间，不加 tzinfo。
    """
    queryset = MCls.objects.all()
    serializer_class = MClsSerializer
    permission_classes = [AllowAny]
    authentication_classes = []

    # 排序
    filter_backends = [OrderingFilter]
    ordering_fields = ('id', 'created_at', 'type', 'tid')
    ordering = ('-id',)  # 注意: 这里需要元组

    # A股常用时间点
    CLOSE_TIME = time(15, 0, 0)       # 收盘 15:00
    MORNING_CUTOFF = time(7, 0, 0)    # 早上 07:00

    # ---------- 工具：取“上一个交易日”（优先用 baostock，失败则退化为工作日逻辑） ----------
    def _prev_trading_day(self, today: date) -> date:
        try:
            import baostock as bs
            bs.login()
            # 查近 15 天的交易日历，找 < today 的最后一个交易日
            start = (today - timedelta(days=15)).strftime('%Y-%m-%d')
            end = today.strftime('%Y-%m-%d')
            rs = bs.query_trade_dates(start_date=start, end_date=end)

            last = None
            while (rs.error_code == '0') and rs.next():
                row = rs.get_row_data()          # [calendar_date, is_trading_day]
                d = datetime.strptime(row[0], '%Y-%m-%d').date()
                if row[1] == '1' and d < today:
                    last = d
            bs.logout()
            if last:
                return last
        except Exception:
            # baostock 不可用或网络异常时走简化逻辑（不含法定节假日）
            pass

        # 退化：前一个工作日（Mon=0..Sun=6）
        wd = today.weekday()
        if wd == 0:         # 周一 → 上周五
            return today - timedelta(days=3)
        elif wd == 6:       # 周日 → 周五
            return today - timedelta(days=2)
        else:               # 其他 → 昨天
            return today - timedelta(days=1)

    # ---------- 过滤主逻辑 ----------
    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.query_params

        start_dt = end_dt = None
        open_flag = q.get('open')  # '1' / '2'

        # 1) 如果传了 open，优先按交易时段自动计算
        if open_flag in ('1', '2'):
            today = datetime.now().date()   # 本地日期（settings.USE_TZ=False）
            if open_flag == '1':
                # 今天 07:00 ~ 今天 15:00
                start_dt = datetime.combine(today, self.MORNING_CUTOFF)
                end_dt = datetime.combine(today, self.CLOSE_TIME)
            else:
                # 上个“交易日” 15:00 ~ 今天 07:00
                prev = self._prev_trading_day(today)
                start_dt = datetime.combine(prev, self.CLOSE_TIME)
                end_dt = datetime.combine(today, self.MORNING_CUTOFF)

        # 2) 否则按显式 start/end 解析
        else:
            start_str = q.get('start')
            end_str = q.get('end')

            if start_str:
                dt = parse_datetime(start_str)
                if dt is None:
                    d = parse_date(start_str)
                    if d is not None:
                        dt = datetime.combine(d, time.min)
                start_dt = dt

            if end_str:
                dt = parse_datetime(end_str)
                if dt is None:
                    d = parse_date(end_str)
                    if d is not None:
                        dt = datetime.combine(d, time.max)
                end_dt = dt

        # 3) 应用过滤
        if start_dt:
            qs = qs.filter(created_at__gte=start_dt)
        if end_dt:
            qs = qs.filter(created_at__lte=end_dt)

        return qs

