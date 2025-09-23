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
    queryset = MCls.objects.all()     # 路由器会让它自动走 qingxu
    serializer_class = MClsSerializer
    authentication_classes = []
    permission_classes = [AllowAny]  # 根据 dvadmin 权限策略调整

    # 开启排序（若全局 settings 里已有 OrderingFilter，这里可不写）
    filter_backends = [OrderingFilter]

    # 允许用户用 ?ordering=... 排的字段白名单
    ordering_fields = ('id', 'created_at')

    # 默认排序（用户不传 ?ordering 时用它）
    ordering = ('-id')  # 再按 id 倒序

    def get_queryset(self):
        qs = super().get_queryset()
        request = self.request
        start_str = request.query_params.get('start')
        end_str = request.query_params.get('end')

        start_dt = None
        end_dt = None

        # 尝试解析 datetime；如果失败再尝试解析 date
        if start_str:
            start_dt = parse_datetime(start_str)
            if start_dt is None:
                d = parse_date(start_str)
                if d is not None:
                    # 仅日期：用当天 00:00:00
                    start_dt = datetime.combine(d, time.min, tzinfo=timezone.utc)

        if end_str:
            end_dt = parse_datetime(end_str)
            if end_dt is None:
                d = parse_date(end_str)
                if d is not None:
                    # 仅日期：用当天 23:59:59.999999（闭区间）
                    end_dt = datetime.combine(d, time.max, tzinfo=timezone.utc)

        if start_dt:
            qs = qs.filter(created_at__gte=start_dt)
        if end_dt:
            qs = qs.filter(created_at__lte=end_dt)

        return qs
