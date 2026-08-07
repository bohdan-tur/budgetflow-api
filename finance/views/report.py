from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from finance.serializers.report import (
    CategoryReportSerializer,
    MonthlyStatisticSerializer,
    PeriodQuerySerializer,
    PeriodStatisticSerializer,
    ReportSerializer,
    TopCategoriesQuerySerializer,
)
from finance.services.report_service import ReportService


class ReportViewSet(GenericViewSet):
    @action(detail=False, methods=["get"])
    def summary(self, request):
        data = ReportService.get_summary(
            user=request.user,
        )

        serializer = ReportSerializer(instance=data)

        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def expenses_by_category(self, request):
        data = ReportService.get_expenses_by_category(
            user=request.user,
        )

        serializer = CategoryReportSerializer(
            instance=data,
            many=True,
        )

        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def income_by_category(self, request):
        data = ReportService.get_income_by_category(
            user=request.user,
        )

        serializer = CategoryReportSerializer(
            instance=data,
            many=True,
        )

        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def monthly_statistics(self, request):
        data = ReportService.get_monthly_statistics(
            user=request.user,
        )

        serializer = MonthlyStatisticSerializer(
            instance=data,
            many=True,
        )

        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def statistics_by_period(self, request):
        query_serializer = PeriodQuerySerializer(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)

        data = ReportService.get_statistics_by_period(
            user=request.user,
            start_time=query_serializer.validated_data.get("start_date"),
            end_time=query_serializer.validated_data.get("end_date"),
        )

        serializer = PeriodStatisticSerializer(
            instance=data,
        )

        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def top_expense_categories(self, request):
        query_serializer = TopCategoriesQuerySerializer(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)

        data = ReportService.get_top_expense_categories(
            user=request.user,
            limit=query_serializer.validated_data["limit"],
        )

        serializer = CategoryReportSerializer(
            instance=data,
            many=True,
        )

        return Response(serializer.data)
