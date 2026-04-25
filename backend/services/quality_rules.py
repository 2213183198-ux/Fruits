from __future__ import annotations

import json
import time
from pathlib import Path
from threading import Lock

from backend.config import settings
from backend.schemas import QualityRuleMessages, QualityRuleSettings, QualityRuleSettingsUpdateRequest


def build_default_quality_rule_settings() -> QualityRuleSettings:
    return QualityRuleSettings(
        enabled=True,
        fresh_keywords=["fresh", "新鲜", "好果"],
        rotten_keywords=["rotten", "腐烂", "坏果"],
        pass_max_rotten_rate=0.0,
        warning_max_rotten_rate=0.5,
        messages=QualityRuleMessages(
            no_detection="未检测到目标，请检查图片内容是否与当前模型类别匹配，或更换更清晰的图片后重试。",
            detected_only="当前模型为通用目标检测模型，本次仅展示检测框和类别统计，不输出鲜腐等级结论。",
            pass_message="未检测到腐烂水果，当前样本可通过基础质检。",
            warning_message="检测到部分腐烂水果，建议进行人工复核或二次分拣。",
            critical_message="腐烂比例较高，建议将该批次标记为重点复检或直接剔除。",
        ),
        updated_at=time.strftime("%Y-%m-%d %H:%M:%S"),
    )


class QualityRuleService:
    def __init__(self, config_path: Path) -> None:
        self.config_path = config_path
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()
        self._settings = self._load_or_create()

    def get_settings(self) -> QualityRuleSettings:
        return QualityRuleSettings.model_validate(self._settings.model_dump())

    def update_settings(self, payload: QualityRuleSettingsUpdateRequest) -> QualityRuleSettings:
        updated = QualityRuleSettings(
            enabled=payload.enabled,
            fresh_keywords=self._normalize_keywords(payload.fresh_keywords),
            rotten_keywords=self._normalize_keywords(payload.rotten_keywords),
            pass_max_rotten_rate=payload.pass_max_rotten_rate,
            warning_max_rotten_rate=payload.warning_max_rotten_rate,
            messages=payload.messages,
            updated_at=time.strftime("%Y-%m-%d %H:%M:%S"),
        )
        with self._lock:
            self._write(updated)
            self._settings = updated
        return self.get_settings()

    def _load_or_create(self) -> QualityRuleSettings:
        if not self.config_path.exists():
            default_settings = build_default_quality_rule_settings()
            self._write(default_settings)
            return default_settings

        try:
            payload = json.loads(self.config_path.read_text(encoding="utf-8"))
            settings_model = QualityRuleSettings.model_validate(payload)
        except Exception:
            backup_path = self.config_path.with_suffix(f".broken-{int(time.time())}.json")
            try:
                self.config_path.replace(backup_path)
            except OSError:
                pass
            settings_model = build_default_quality_rule_settings()
            self._write(settings_model)

        normalized = QualityRuleSettings(
            enabled=settings_model.enabled,
            fresh_keywords=self._normalize_keywords(settings_model.fresh_keywords),
            rotten_keywords=self._normalize_keywords(settings_model.rotten_keywords),
            pass_max_rotten_rate=settings_model.pass_max_rotten_rate,
            warning_max_rotten_rate=settings_model.warning_max_rotten_rate,
            messages=settings_model.messages,
            updated_at=settings_model.updated_at or time.strftime("%Y-%m-%d %H:%M:%S"),
        )
        self._write(normalized)
        return normalized

    def _write(self, payload: QualityRuleSettings) -> None:
        self.config_path.write_text(payload.model_dump_json(indent=2), encoding="utf-8")

    def _normalize_keywords(self, keywords: list[str]) -> list[str]:
        normalized: list[str] = []
        seen: set[str] = set()

        for keyword in keywords:
            value = str(keyword).strip()
            if not value:
                continue
            identity = value.casefold()
            if identity in seen:
                continue
            seen.add(identity)
            normalized.append(value)

        return normalized


quality_rule_service = QualityRuleService(settings.quality_rules_path)
