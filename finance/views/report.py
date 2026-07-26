from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from finance.serializers.report import ReportSerializer
from finance.services.report_service import ReportService


class ReportViewSet(GenericViewSet):

    @action(detail=False, methods=["get"])
    def summary(self, request):
        data = ReportService.get_summary(
            user=request.user,
        )

        serializer = ReportSerializer(data)

        return Response(serializer.data)