from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.api.rbac import Permission, require_permission
from app.api.tenant_scope import resolve_institution_scope, verify_object_institution_access
from app.db.session import get_db
from app.models.enums import ComplianceReportStatus
from app.models.user import User
from app.repositories.compliance_report import ComplianceReportRepository
from app.schemas.common import PaginatedResponse, PaginationParams, SortParams
from app.schemas.compliance_report import (
    ComplianceReportCreate,
    ComplianceReportRead,
    ComplianceReportUpdate,
)
from app.services import compliance_report_service

router = APIRouter(prefix="/compliance-reports", tags=["Compliance Reports"])

_SORTABLE_FIELDS = {"period_start", "period_end", "generated_at", "overall_score", "created_at"}


@router.get(
    "",
    response_model=PaginatedResponse[ComplianceReportRead],
    dependencies=[Depends(require_permission(Permission.REPORTS_READ))],
)
def list_compliance_reports(
    db: Session = Depends(get_db),
    pagination: PaginationParams = Depends(),
    sort: SortParams = Depends(),
    institution_id: UUID | None = Depends(resolve_institution_scope),
    department_id: UUID | None = Query(None),
    status_: ComplianceReportStatus | None = Query(None, alias="status"),
) -> PaginatedResponse[ComplianceReportRead]:
    repo = ComplianceReportRepository(db)
    items, total = repo.list(
        pagination=pagination,
        sort=sort,
        allowed_sort_fields=_SORTABLE_FIELDS,
        default_sort_field="generated_at",
        filters={"institution_id": institution_id, "department_id": department_id, "status": status_},
    )
    return PaginatedResponse.build(
        [ComplianceReportRead.from_model(r) for r in items], total_items=total, params=pagination
    )


@router.get(
    "/{report_id}",
    response_model=ComplianceReportRead,
    dependencies=[Depends(require_permission(Permission.REPORTS_READ))],
)
def get_compliance_report(
    report_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> ComplianceReportRead:
    repo = ComplianceReportRepository(db)
    report = repo.get_or_404(report_id)
    verify_object_institution_access(db, current_user, report.institution_id)
    return ComplianceReportRead.from_model(report)


@router.post(
    "",
    response_model=ComplianceReportRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(Permission.REPORTS_GENERATE))],
)
def create_compliance_report(
    payload: ComplianceReportCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> ComplianceReportRead:
    verify_object_institution_access(db, current_user, payload.institution_id)
    report = compliance_report_service.create_report(db, payload)
    return ComplianceReportRead.from_model(report)


@router.patch(
    "/{report_id}",
    response_model=ComplianceReportRead,
    dependencies=[Depends(require_permission(Permission.REPORTS_GENERATE))],
)
def update_compliance_report(
    report_id: UUID,
    payload: ComplianceReportUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ComplianceReportRead:
    repo = ComplianceReportRepository(db)
    report = repo.get_or_404(report_id)
    verify_object_institution_access(db, current_user, report.institution_id)
    report = compliance_report_service.update_report(db, report, payload)
    return ComplianceReportRead.from_model(report)


@router.delete(
    "/{report_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission(Permission.REPORTS_GENERATE))],
)
def delete_compliance_report(
    report_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> None:
    """ComplianceReport has no soft-delete column by design (per its model
    docstring: corrections are made by generating a new report, not editing
    or hiding an old one) — this is a hard delete."""
    repo = ComplianceReportRepository(db)
    report = repo.get_or_404(report_id)
    verify_object_institution_access(db, current_user, report.institution_id)
    repo.delete(report)
    db.commit()
