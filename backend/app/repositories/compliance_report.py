from app.models.compliance_report import ComplianceReport
from app.repositories.base import BaseRepository


class ComplianceReportRepository(BaseRepository[ComplianceReport]):
    model = ComplianceReport
