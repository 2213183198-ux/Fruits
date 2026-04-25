from fastapi import APIRouter

from backend.app.api.presenters import present_quality_rule_settings
from backend.app.core.runtime import runtime
from backend.app.schemas.common import ApiResponse, build_api_response
from backend.app.schemas.public import (
    PublicQualityRuleSettingsData,
    QualityRuleSettingsUpdateBody,
)
from backend.schemas import QualityRuleMessages, QualityRuleSettingsUpdateRequest


router = APIRouter(prefix="/api/v1/settings", tags=["Settings"])


@router.get(
    "/quality-rules",
    response_model=ApiResponse[PublicQualityRuleSettingsData],
    summary="Get quality rule settings",
)
def get_quality_rule_settings() -> ApiResponse[PublicQualityRuleSettingsData]:
    payload = runtime.get_quality_rule_settings()
    return build_api_response(
        present_quality_rule_settings(payload),
        message="Quality rule settings fetched.",
    )


@router.put(
    "/quality-rules",
    response_model=ApiResponse[PublicQualityRuleSettingsData],
    summary="Update quality rule settings",
)
def update_quality_rule_settings(
    payload: QualityRuleSettingsUpdateBody,
) -> ApiResponse[PublicQualityRuleSettingsData]:
    updated = runtime.update_quality_rule_settings(
        QualityRuleSettingsUpdateRequest(
            enabled=payload.enabled,
            fresh_keywords=payload.fresh_keywords,
            rotten_keywords=payload.rotten_keywords,
            pass_max_rotten_rate=payload.pass_max_rotten_rate,
            warning_max_rotten_rate=payload.warning_max_rotten_rate,
            messages=QualityRuleMessages(**payload.messages.model_dump()),
        )
    )
    return build_api_response(
        present_quality_rule_settings(updated),
        message="Quality rule settings updated.",
    )
