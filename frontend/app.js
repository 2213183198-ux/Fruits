const $ = (id) => document.getElementById(id);
const $$ = (selector, root = document) => Array.from(root.querySelectorAll(selector));

const PRODUCT_NAME = "生鲜分拣多模型视觉质检平台";
const SUPPORT_TEXT = "生鲜分拣场景 · 多模型质检、复核回流、样本闭环";
const API_BASE = "/api/v1";
const PANELS = new Set(["overview", "models", "single", "batch", "webcam", "deployment", "settings", "review", "retrain", "history", "cleanup"]);
const PANEL_GROUP_MAP = {
  overview: "overview",
  single: "workbench",
  batch: "workbench",
  webcam: "workbench",
  models: "management",
  settings: "management",
  deployment: "management",
  review: "tracking",
  retrain: "tracking",
  history: "tracking",
  cleanup: "tracking",
};
const OVERVIEW_SHORTCUT_GROUPS = [
  {
    title: "检测工作台",
    description: "单图、批量和摄像头质检入口",
    links: [
      { panel: "single", label: "单图检测" },
      { panel: "batch", label: "批量检测" },
      { panel: "webcam", label: "摄像头检测" },
    ],
  },
  {
    title: "平台管理",
    description: "模型、规则、部署与对比能力统一管理",
    links: [
      { panel: "models", label: "模型中心" },
      { panel: "settings", label: "规则设置" },
      { panel: "deployment", label: "部署与评测" },
    ],
  },
  {
    title: "回流闭环",
    description: "复核、回流、复训与样本追踪集中处理",
    links: [
      { panel: "review", label: "复核中心" },
      { panel: "history", label: "历史记录" },
      { panel: "cleanup", label: "文件清理" },
    ],
  },
];
const IMAGE_EXTENSIONS = /\.(jpg|jpeg|png|bmp|webp)$/i;
const STATUS_LABELS = {
  pass: "通过",
  warning: "预警",
  critical: "严重",
  no_detection: "未检出",
  detected: "已检测",
  failed: "失败",
};
const MODE_LABELS = {
  single: "单图",
  batch: "批量",
  webcam: "摄像头",
};
const TASK_STATUS_LABELS = {
  queued: "排队中",
  running: "处理中",
  succeeded: "已完成",
  failed: "失败",
};
const REVIEW_STATUS_LABELS = {
  pending: "待复核",
  optional: "可选复核",
  reviewed: "已复核",
  feedback: "已回流",
};
const REVIEW_DECISION_LABELS = {
  confirm: "确认结果",
  false_positive: "误检",
  missed_detection: "漏检",
  needs_feedback: "加入回流",
};
const RETRAIN_STATUS_LABELS = {
  pending: "待处理",
  ready: "待复训",
  used: "已入训练",
};

const RETRAIN_BATCH_STATUS_LABELS = {
  draft: "待导出",
  exported: "已导出",
};

const ANNOTATION_STATUS_LABELS = {
  pending: "待补标",
  drafted: "已写草稿",
  ready_empty: "空标签",
};

const dom = {
  sidebar: $("sidebar"),
  sidebarBackdrop: $("sidebarBackdrop"),
  sidebarToggle: $("sidebarToggle"),
  sidebarSupportNote: $("sidebarSupportNote"),
  serviceIndicator: $("headerServiceIndicator"),
  modelBadge: $("headerModelBadge"),
  overlay: $("globalOverlay"),
  overlaySpinner: $("overlaySpinner"),
  overlayTitle: $("overlayTitle"),
  overlayDetail: $("overlayDetail"),
  overlayProgressBlock: $("overlayProgressBlock"),
  overlayProgressBar: $("overlayProgressBar"),
  overlayProgressValue: $("overlayProgressValue"),
  overlaySpeed: $("overlaySpeed"),
  overlayEta: $("overlayEta"),
  modelNotice: $("modelNotice"),
  singleNotice: $("singleNotice"),
  batchNotice: $("batchNotice"),
  webcamNotice: $("webcamNotice"),
  deploymentNotice: $("deploymentNotice"),
  settingsNotice: $("settingsNotice"),
  historyNotice: $("historyNotice"),
  retrainNotice: $("retrainNotice"),
  cleanupNotice: $("cleanupNotice"),
  overviewNotice: $("overviewNotice"),
  overviewModelCard: $("overviewModelCard"),
  overviewQuickLinks: $("overviewQuickLinks"),
  overviewClassList: $("overviewClassList"),
  overviewRecentRuns: $("overviewRecentRuns"),
  overviewDashboardStats: $("overviewDashboardStats"),
  overviewStatusBoard: $("overviewStatusBoard"),
  overviewOpsBoard: $("overviewOpsBoard"),
  overviewTrend: $("overviewTrend"),
  modelUploadFile: $("modelUploadFile"),
  modelYamlFile: $("modelYamlFile"),
  modelAutoActivate: $("modelAutoActivate"),
  modelUploadBtn: $("modelUploadBtn"),
  modelResetBtn: $("modelResetBtn"),
  refreshModelsBtn: $("refreshModelsBtn"),
  modelList: $("modelList"),
  modelSummary: $("modelSummary"),
  modelCompareBoard: $("modelCompareBoard"),
  singleFile: $("singleFile"),
  singleImgsz: $("singleImgsz"),
  singleConf: $("singleConf"),
  singleRunBtn: $("singleRunBtn"),
  singleResetBtn: $("singleResetBtn"),
  singleSourceImage: $("singleSourceImage"),
  singleResultImage: $("singleResultImage"),
  singleSourcePlaceholder: $("singleSourcePlaceholder"),
  singleResultPlaceholder: $("singleResultPlaceholder"),
  singleSummary: $("singleSummary"),
  singleReport: $("singleReport"),
  singleDetections: $("singleDetections"),
  singleActiveModel: $("singleActiveModel"),
  batchFiles: $("batchFiles"),
  batchFolder: $("batchFolder"),
  batchDropZone: $("batchDropZone"),
  batchImgsz: $("batchImgsz"),
  batchConf: $("batchConf"),
  batchRunBtn: $("batchRunBtn"),
  batchResetBtn: $("batchResetBtn"),
  batchSelection: $("batchSelection"),
  batchSummary: $("batchSummary"),
  batchLinks: $("batchLinks"),
  batchResults: $("batchResults"),
  batchFailures: $("batchFailures"),
  batchActiveModel: $("batchActiveModel"),
  webcamStartBtn: $("webcamStartBtn"),
  webcamDetectBtn: $("webcamDetectBtn"),
  webcamAutoBtn: $("webcamAutoBtn"),
  webcamStopBtn: $("webcamStopBtn"),
  webcamVideo: $("webcamVideo"),
  webcamOverlay: $("webcamOverlay"),
  webcamImgsz: $("webcamImgsz"),
  webcamConf: $("webcamConf"),
  webcamReport: $("webcamReport"),
  webcamDetections: $("webcamDetections"),
  webcamMetrics: $("webcamMetrics"),
  webcamActiveModel: $("webcamActiveModel"),
  webcamStageHint: document.querySelector(".video-stage-hint"),
  exportImgsz: $("exportImgsz"),
  exportOnnxBtn: $("exportOnnxBtn"),
  exportTensorRtBtn: $("exportTensorRtBtn"),
  benchmarkFile: $("benchmarkFile"),
  benchmarkImgsz: $("benchmarkImgsz"),
  benchmarkConf: $("benchmarkConf"),
  benchmarkRuns: $("benchmarkRuns"),
  benchmarkRunBtn: $("benchmarkRunBtn"),
  deploymentStatusCards: $("deploymentStatusCards"),
  deploymentOutput: $("deploymentOutput"),
  deploymentCurrentTarget: $("deploymentCurrentTarget"),
  refreshQualityRulesBtn: $("refreshQualityRulesBtn"),
  qualityRulesEnabled: $("qualityRulesEnabled"),
  passMaxRottenRate: $("passMaxRottenRate"),
  warningMaxRottenRate: $("warningMaxRottenRate"),
  freshKeywordsInput: $("freshKeywordsInput"),
  rottenKeywordsInput: $("rottenKeywordsInput"),
  saveQualityRulesBtn: $("saveQualityRulesBtn"),
  resetQualityRulesBtn: $("resetQualityRulesBtn"),
  qualityNoDetectionMessage: $("qualityNoDetectionMessage"),
  qualityDetectedOnlyMessage: $("qualityDetectedOnlyMessage"),
  qualityPassMessage: $("qualityPassMessage"),
  qualityWarningMessage: $("qualityWarningMessage"),
  qualityCriticalMessage: $("qualityCriticalMessage"),
  qualityRulesSummary: $("qualityRulesSummary"),
  refreshHistoryBtn: $("refreshHistoryBtn"),
  reviewNotice: $("reviewNotice"),
  refreshReviewBtn: $("refreshReviewBtn"),
  exportReviewQueueBtn: $("exportReviewQueueBtn"),
  reviewSummary: $("reviewSummary"),
  feedbackPoolPanel: $("feedbackPoolPanel"),
  feedbackPoolSummary: $("feedbackPoolSummary"),
  reviewKeywordInput: $("reviewKeywordInput"),
  reviewList: $("reviewList"),
  reviewDetail: $("reviewDetail"),
  refreshRetrainBtn: $("refreshRetrainBtn"),
  retrainSummary: $("retrainSummary"),
  retrainBatchSummary: $("retrainBatchSummary"),
  retrainSelectionHint: $("retrainSelectionHint"),
  retrainBatchNameInput: $("retrainBatchNameInput"),
  retrainBatchNotesInput: $("retrainBatchNotesInput"),
  createRetrainBatchBtn: $("createRetrainBatchBtn"),
  clearRetrainSelectionBtn: $("clearRetrainSelectionBtn"),
  retrainBatchList: $("retrainBatchList"),
  retrainBatchDetail: $("retrainBatchDetail"),
  retrainKeywordInput: $("retrainKeywordInput"),
  retrainList: $("retrainList"),
  retrainDetail: $("retrainDetail"),
  historyDeleteSelectedBtn: $("historyDeleteSelectedBtn"),
  historyDeleteAllBtn: $("historyDeleteAllBtn"),
  historyDeleteRangeBtn: $("historyDeleteRangeBtn"),
  historyCreatedFrom: $("historyCreatedFrom"),
  historyCreatedTo: $("historyCreatedTo"),
  historyList: $("historyList"),
  historyDetail: $("historyDetail"),
  refreshStorageBtn: $("refreshStorageBtn"),
  deleteSelectedBtn: $("deleteSelectedBtn"),
  storageSummary: $("storageSummary"),
  artifactList: $("artifactList"),
};

const state = {
  health: null,
  modelInventory: null,
  deployment: null,
  qualityRules: null,
  storage: null,
  dashboardSummary: null,
  historyRuns: [],
  historyDetail: null,
  reviewSummary: null,
  reviewItems: [],
  reviewDetail: null,
  feedbackPoolSummary: null,
  retrainSummary: null,
  retrainBatchSummary: null,
  retrainItems: [],
  retrainDetail: null,
  retrainBatches: [],
  retrainBatchDetail: null,
  selectedReviewItemId: null,
  reviewQueue: "focus",
  reviewDecisionFilter: "all",
  reviewModeFilter: "all",
  reviewKeyword: "",
  reviewKeywordTimer: null,
  selectedRetrainItemId: null,
  retrainStatusFilter: "all",
  retrainDecisionFilter: "all",
  retrainModeFilter: "all",
  retrainKeyword: "",
  retrainKeywordTimer: null,
  selectedRetrainBatchId: null,
  selectedRetrainCatalogIds: new Set(),
  selectedHistoryId: null,
  selectedHistoryIds: new Set(),
  selectedArtifacts: new Set(),
  batchFiles: [],
  batchTask: null,
  benchmarkTask: null,
  deploymentOutput: null,
  singleSourceUrl: null,
  singleResult: null,
  healthTimer: null,
  overlayStartedAt: 0,
  webcam: {
    stream: null,
    socket: null,
    autoTimer: null,
    busy: false,
    autoRunning: false,
    frameId: 0,
    lastLatencyMs: null,
    captureCanvas: document.createElement("canvas"),
  },
};

function init() {
  applyShellCopy();
  bindSidebarSections();
  bindShell();
  bindDelegatedActions();
  bindModelControls();
  bindSingleControls();
  bindBatchControls();
  bindWebcamControls();
  bindDeploymentControls();
  bindSettingsControls();
  bindReviewControls();
  bindRetrainControls();
  bindHistoryControls();
  bindCleanupControls();
  resetSingleView();
  resetBatchView();
  resetWebcamView();
  renderHeader();
  renderOverview();
  renderModelSummary();
  renderModelComparison();
  renderModelList();
  renderDeploymentStatus();
  renderDeploymentOutput();
  renderQualityRules();
  renderReviewSummary();
  renderFeedbackPoolSummary();
  updateReviewModeButtons();
  renderReviewList();
  renderReviewDetail();
  renderRetrainSummary();
  renderRetrainBatchSummary();
  renderRetrainBatchList();
  renderRetrainBatchDetail();
  renderRetrainList();
  renderRetrainDetail();
  renderHistoryList();
  renderHistoryDetail();
  renderStorageSummary();
  renderArtifactList();
  activatePanel(getPanelFromHash());
  void bootstrap();
}

function cleanupBeforeUnload() {
  releaseSingleSourcePreview();
  stopWebcam(false);
  if (state.reviewKeywordTimer) {
    window.clearTimeout(state.reviewKeywordTimer);
    state.reviewKeywordTimer = null;
  }
  if (state.retrainKeywordTimer) {
    window.clearTimeout(state.retrainKeywordTimer);
    state.retrainKeywordTimer = null;
  }
  if (state.healthTimer) {
    window.clearInterval(state.healthTimer);
    state.healthTimer = null;
  }
}

async function bootstrap() {
  await Promise.allSettled([
    loadHealth(true),
    loadModels(true),
    loadDashboardSummary(true),
    loadDeployment(true),
    loadQualityRules(true),
    loadReviewSummary(true),
    loadReviewItems(true),
    loadRetrainSummary(true),
    loadRetrainBatchSummary(true),
    loadRetrainBatches(true),
    loadRetrainItems(true),
    loadHistory(true),
    loadStorage(true),
  ]);

  if (state.healthTimer) {
    window.clearInterval(state.healthTimer);
  }
  state.healthTimer = window.setInterval(() => {
    void loadHealth(true);
  }, 25000);
}

function applyShellCopy() {
  document.title = PRODUCT_NAME;
  $("sidebarProjectName").textContent = PRODUCT_NAME;
  dom.sidebarSupportNote.textContent = SUPPORT_TEXT;
  $("headerProjectName").textContent = PRODUCT_NAME;
  $("headerProjectSubtitle").textContent = SUPPORT_TEXT;
}

function getPanelFromHash() {
  const panel = window.location.hash.replace(/^#/, "");
  return PANELS.has(panel) ? panel : "overview";
}

function closeSidebar() {
  dom.sidebar.classList.remove("open");
  document.body.classList.remove("sidebar-open");
}

function setSidebarGroupOpen(groupId, expanded) {
  const section = document.querySelector(`[data-sidebar-group="${groupId}"]`);
  const toggle = document.querySelector(`[data-sidebar-toggle="${groupId}"]`);
  const content = document.querySelector(`[data-sidebar-content="${groupId}"]`);
  if (!section || !toggle || !content) {
    return;
  }
  section.classList.toggle("is-open", expanded);
  toggle.setAttribute("aria-expanded", expanded ? "true" : "false");
  content.hidden = !expanded;
  content.style.display = expanded ? "grid" : "none";
}

function ensurePanelGroupExpanded(panel) {
  const groupId = PANEL_GROUP_MAP[panel];
  if (!groupId) {
    return;
  }
  setSidebarGroupOpen(groupId, true);
}

function bindSidebarSections() {
  $$("[data-sidebar-content]").forEach((content) => {
    const groupId = content.dataset.sidebarContent || "";
    const section = document.querySelector(`[data-sidebar-group="${groupId}"]`);
    const expanded = section?.classList.contains("is-open");
    content.hidden = !expanded;
    content.style.display = expanded ? "grid" : "none";
  });

  $$("[data-sidebar-toggle]").forEach((toggle) => {
    toggle.addEventListener("click", (event) => {
      event.preventDefault();
      event.stopPropagation();
      const groupId = toggle.dataset.sidebarToggle || "";
      const expanded = toggle.getAttribute("aria-expanded") === "true";
      setSidebarGroupOpen(groupId, !expanded);
    });
  });
}

function jumpToPanel(panel) {
  if (!PANELS.has(panel)) {
    return;
  }
  window.location.hash = panel;
  activatePanel(panel);
}

function activatePanel(panel) {
  const current = PANELS.has(panel) ? panel : "overview";
  $$(".panel").forEach((node) => {
    node.classList.toggle("is-active", node.dataset.panel === current);
  });
  $$(".nav-link").forEach((node) => {
    node.classList.toggle("is-active", node.dataset.panel === current);
  });
  ensurePanelGroupExpanded(current);
  closeSidebar();
}

function bindShell() {
  dom.sidebarToggle.addEventListener("click", () => {
    dom.sidebar.classList.add("open");
    document.body.classList.add("sidebar-open");
  });

  dom.sidebarBackdrop.addEventListener("click", closeSidebar);

  $$(".nav-link").forEach((button) => {
    button.addEventListener("click", () => {
      jumpToPanel(button.dataset.panel || "overview");
    });
  });

  window.addEventListener("hashchange", () => {
    activatePanel(getPanelFromHash());
  });
}

function bindDelegatedActions() {
  document.addEventListener("click", (event) => {
    if (event.defaultPrevented) {
      return;
    }
    const jumpTarget = event.target.closest("[data-jump-panel]");
    if (jumpTarget) {
      event.preventDefault();
      jumpToPanel(jumpTarget.dataset.jumpPanel || "overview");
      return;
    }

    const activateTarget = event.target.closest("[data-model-activate]");
    if (activateTarget) {
      event.preventDefault();
      void activateModel(activateTarget.dataset.modelActivate || "");
      return;
    }

    const deleteTarget = event.target.closest("[data-model-delete]");
    if (deleteTarget) {
      event.preventDefault();
      void deleteModel(deleteTarget.dataset.modelDelete || "", deleteTarget.dataset.modelName || "该模型");
      return;
    }

    const historyTarget = event.target.closest("[data-history-id]");
    if (historyTarget) {
      event.preventDefault();
      jumpToPanel("history");
      void loadHistoryDetail(Number(historyTarget.dataset.historyId), true);
      return;
    }

    const reviewTarget = event.target.closest("[data-review-item-id]");
    if (reviewTarget) {
      event.preventDefault();
      jumpToPanel("review");
      void loadReviewDetail(Number(reviewTarget.dataset.reviewItemId), true);
      return;
    }

    const retrainTarget = event.target.closest("[data-retrain-item-id]");
    if (retrainTarget) {
      event.preventDefault();
      jumpToPanel("retrain");
      void loadRetrainDetail(Number(retrainTarget.dataset.retrainItemId), true);
      return;
    }

    const retrainBatchTarget = event.target.closest("[data-retrain-batch-id]");
    if (retrainBatchTarget) {
      event.preventDefault();
      jumpToPanel("retrain");
      void loadRetrainBatchDetail(Number(retrainBatchTarget.dataset.retrainBatchId), true);
      return;
    }

    const batchRemoveTarget = event.target.closest("[data-batch-remove]");
    if (batchRemoveTarget) {
      event.preventDefault();
      removeBatchFile(batchRemoveTarget.dataset.batchRemove || "");
      return;
    }

    const downloadTarget = event.target.closest("[data-download-url]");
    if (downloadTarget) {
      event.preventDefault();
      const url = downloadTarget.dataset.downloadUrl;
      if (url) {
        const filename = downloadTarget.dataset.downloadName || basenamePath(url);
        void downloadBlob(url, filename);
      }
      return;
    }

    const reviewActionTarget = event.target.closest("[data-review-action]");
    if (reviewActionTarget) {
      event.preventDefault();
      const action = reviewActionTarget.dataset.reviewAction || "";
      void handleReviewAction(action);
      return;
    }

    const retrainActionTarget = event.target.closest("[data-retrain-action]");
    if (retrainActionTarget) {
      event.preventDefault();
      const action = retrainActionTarget.dataset.retrainAction || "";
      void handleRetrainAction(action);
      return;
    }

    const retrainBatchActionTarget = event.target.closest("[data-retrain-batch-action]");
    if (retrainBatchActionTarget) {
      event.preventDefault();
      const action = retrainBatchActionTarget.dataset.retrainBatchAction || "";
      void handleRetrainBatchAction(action);
    }
  });
}

function resolveUrl(path) {
  return new URL(path, window.location.origin).toString();
}

function basenamePath(value) {
  return String(value || "").split("/").pop() || "";
}

function csvCell(value) {
  return `"${String(value ?? "").replaceAll('"', '""')}"`;
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function formatPercent(value, digits = 1) {
  const numeric = Number(value) || 0;
  return `${(numeric * 100).toFixed(digits)}%`;
}

function formatNumber(value, digits = 2) {
  return Number(value || 0).toFixed(digits);
}

function formatDateTime(value) {
  if (!value) {
    return "-";
  }
  return String(value).replace("T", " ");
}

function formatLocalDateTime(value) {
  if (!value) {
    return null;
  }
  return `${value.replace("T", " ")}:00`;
}

function formatSizeMb(value) {
  return `${formatNumber(value || 0, 2)} MB`;
}

function formatStatus(status) {
  return STATUS_LABELS[status] || status || "-";
}

function formatTaskStatus(status) {
  return TASK_STATUS_LABELS[status] || status || "-";
}

function formatReviewStatus(status) {
  return REVIEW_STATUS_LABELS[status] || status || "-";
}

function formatReviewDecision(decision) {
  return REVIEW_DECISION_LABELS[decision] || decision || "-";
}

function formatRetrainStatus(status) {
  return RETRAIN_STATUS_LABELS[status] || status || "-";
}

function formatAnnotationStatus(status) {
  return ANNOTATION_STATUS_LABELS[status] || status || "-";
}

function formatRetrainBatchStatus(status) {
  return RETRAIN_BATCH_STATUS_LABELS[status] || status || "-";
}

function formatMode(mode) {
  return MODE_LABELS[mode] || mode || "-";
}

function sleep(ms) {
  return new Promise((resolve) => window.setTimeout(resolve, ms));
}

function parseKeywordList(value) {
  return String(value || "")
    .replace(/\uFF0C/g, ",")
    .split(/[\n,;]+/)
    .map((item) => item.trim())
    .filter(Boolean);
}

function isImageFile(file) {
  if (!file) {
    return false;
  }
  return IMAGE_EXTENSIONS.test(file.name || "") || String(file.type || "").startsWith("image/");
}

function createSummaryPill(label, value) {
  return `<span class="summary-pill"><span>${escapeHtml(label)}</span><strong>${escapeHtml(value)}</strong></span>`;
}

function createStatusPill(status) {
  return `<span class="status-pill ${escapeHtml(status || "no_detection")}">${escapeHtml(formatStatus(status))}</span>`;
}

function createReviewStatusPill(status) {
  return `<span class="review-pill ${escapeHtml(status || "optional")}">${escapeHtml(formatReviewStatus(status))}</span>`;
}

function createRetrainStatusPill(status) {
  return `<span class="retrain-pill ${escapeHtml(status || "pending")}">${escapeHtml(formatRetrainStatus(status))}</span>`;
}

function createRetrainBatchStatusPill(status) {
  return `<span class="batch-pill ${escapeHtml(status || "draft")}">${escapeHtml(formatRetrainBatchStatus(status))}</span>`;
}

function createAnnotationStatusPill(status) {
  const normalized = status || "pending";
  return `<span class="annotation-pill ${escapeHtml(normalized)}">${escapeHtml(formatAnnotationStatus(normalized))}</span>`;
}

function formatYoloCoordinate(value) {
  return Number(value || 0).toFixed(6).replace(/\.?0+$/, "");
}

function buildYoloDraftLine(classId, xCenter, yCenter, width, height) {
  return `${Math.max(0, Math.trunc(Number(classId) || 0))} ${[
    xCenter,
    yCenter,
    width,
    height,
  ]
    .map((value) => formatYoloCoordinate(value))
    .join(" ")}`;
}

function parseYoloAnnotationDraft(value) {
  const lines = String(value || "").replace(/\r\n/g, "\n").split("\n");
  const boxes = [];
  const errors = [];

  lines.forEach((rawLine, index) => {
    const line = rawLine.trim();
    if (!line) {
      return;
    }

    const parts = line.split(/\s+/);
    if (parts.length !== 5) {
      errors.push(`第 ${index + 1} 行格式不正确，应为 class x_center y_center width height`);
      return;
    }

    const classId = Number(parts[0]);
    const coords = parts.slice(1).map((item) => Number(item));
    if (!Number.isInteger(classId) || coords.some((item) => !Number.isFinite(item))) {
      errors.push(`第 ${index + 1} 行包含无效数字`);
      return;
    }
    if (coords.some((item) => item < 0 || item > 1)) {
      errors.push(`第 ${index + 1} 行坐标必须在 0 到 1 之间`);
      return;
    }

    const [xCenter, yCenter, width, height] = coords;
    const left = Math.max(0, (xCenter - width / 2) * 100);
    const top = Math.max(0, (yCenter - height / 2) * 100);
    boxes.push({
      classId,
      xCenter,
      yCenter,
      width,
      height,
      left: Math.min(left, 100),
      top: Math.min(top, 100),
      widthPercent: Math.min(width * 100, 100),
      heightPercent: Math.min(height * 100, 100),
      lineIndex: index,
      lineNumber: index + 1,
      lineText: buildYoloDraftLine(classId, xCenter, yCenter, width, height),
    });
  });

  return {
    boxes,
    errors,
    nonEmptyLineCount: lines.filter((line) => line.trim()).length,
  };
}

function buildRetrainAnnotationOverlayHtml(draft) {
  const parsed = parseYoloAnnotationDraft(draft);
  if (!parsed.boxes.length) {
    return '<div class="annotation-overlay-empty">暂无可预览框</div>';
  }
  return parsed.boxes
    .map(
      (box, index) => `
        <div
          class="annotation-box"
          style="left:${box.left}%;top:${box.top}%;width:${box.widthPercent}%;height:${box.heightPercent}%"
        >
          <span class="annotation-box-label">#${index + 1} · cls ${box.classId}</span>
        </div>
      `,
    )
    .join("");
}

function buildRetrainAnnotationStatsHtml(draft) {
  const parsed = parseYoloAnnotationDraft(draft);
  return [
    createSummaryPill("有效框", `${parsed.boxes.length}`),
    createSummaryPill("待修正", `${parsed.errors.length}`),
    createSummaryPill("非空行", `${parsed.nonEmptyLineCount}`),
  ].join("");
}

function buildRetrainAnnotationListHtml(draft) {
  const parsed = parseYoloAnnotationDraft(draft);
  if (!parsed.boxes.length) {
    return '<div class="helper-note">当前没有有效框。可以直接输入 YOLO 文本，或点击上方图片按默认尺寸补一个框。</div>';
  }
  return parsed.boxes
    .map(
      (box) => `
        <div class="annotation-draft-item">
          <div class="annotation-draft-copy">
            <strong>第 ${box.lineNumber} 行</strong>
            <span>${escapeHtml(box.lineText)}</span>
          </div>
          <button class="btn btn-ghost" type="button" data-retrain-draft-remove="${box.lineIndex}">删除</button>
        </div>
      `,
    )
    .join("");
}

function buildRetrainAnnotationNoticeText(draft, hasArtifactPreview = false) {
  const parsed = parseYoloAnnotationDraft(draft);
  if (parsed.errors.length) {
    return parsed.errors.join("；");
  }
  if (!parsed.boxes.length) {
    return hasArtifactPreview
      ? "点击上方图片可按默认尺寸补一个框，也可以直接编辑 YOLO 文本。"
      : "可直接编辑 YOLO 文本补框；当前没有标注图预览。";
  }
  return hasArtifactPreview
    ? "点击上方图片可继续补框；保存后会随样本一起导出到 labels/ 目录。"
    : "保存后会随样本一起导出到 labels/ 目录。";
}

function renderRetrainAnnotationComposer() {
  const input = $("retrainAnnotationInput");
  if (!input) {
    return;
  }

  const draft = input.value;
  const overlay = $("retrainAnnotationOverlay");
  const stats = $("retrainAnnotationStats");
  const list = $("retrainAnnotationList");
  const notice = $("retrainAnnotationNotice");

  if (overlay) {
    overlay.innerHTML = buildRetrainAnnotationOverlayHtml(draft);
  }
  if (stats) {
    stats.innerHTML = buildRetrainAnnotationStatsHtml(draft);
  }
  if (list) {
    list.innerHTML = buildRetrainAnnotationListHtml(draft);
  }
  if (notice) {
    notice.textContent = buildRetrainAnnotationNoticeText(draft, Boolean(state.retrainDetail?.artifact_url));
    notice.classList.toggle("is-warning", parseYoloAnnotationDraft(draft).errors.length > 0);
  }
}

function appendRetrainDraftLine(line) {
  const input = $("retrainAnnotationInput");
  if (!input) {
    return;
  }
  const nextLine = String(line || "").trim();
  if (!nextLine) {
    return;
  }
  const current = input.value.trim();
  input.value = current ? `${current}\n${nextLine}` : nextLine;
  renderRetrainAnnotationComposer();
}

function removeRetrainDraftLine(lineIndex) {
  const input = $("retrainAnnotationInput");
  if (!input) {
    return;
  }
  const nextLines = input.value
    .replace(/\r\n/g, "\n")
    .split("\n")
    .filter((_, index) => index !== lineIndex);
  input.value = nextLines.join("\n").replace(/^\n+|\n+$/g, "");
  renderRetrainAnnotationComposer();
}

function handleRetrainDraftTool(action) {
  const input = $("retrainAnnotationInput");
  if (!input) {
    return;
  }
  if (action === "append_default") {
    const parsed = parseYoloAnnotationDraft(input.value);
    const lastClassId = parsed.boxes.length ? parsed.boxes[parsed.boxes.length - 1].classId : 0;
    appendRetrainDraftLine(buildYoloDraftLine(lastClassId, 0.5, 0.5, 0.2, 0.2));
    return;
  }
  if (action === "clear") {
    input.value = "";
    renderRetrainAnnotationComposer();
  }
}

function handleRetrainStageClick(stage, event) {
  const input = $("retrainAnnotationInput");
  if (!input || !stage) {
    return;
  }

  const rect = stage.getBoundingClientRect();
  if (!rect.width || !rect.height) {
    return;
  }

  const xCenter = Math.min(Math.max((event.clientX - rect.left) / rect.width, 0), 1);
  const yCenter = Math.min(Math.max((event.clientY - rect.top) / rect.height, 0), 1);
  const parsed = parseYoloAnnotationDraft(input.value);
  const classId = parsed.boxes.length ? parsed.boxes[parsed.boxes.length - 1].classId : 0;
  appendRetrainDraftLine(buildYoloDraftLine(classId, xCenter, yCenter, 0.2, 0.2));
}

function summarizeRetrainBatchItems(items) {
  const summary = {
    total: items.length,
    readyLabeled: 0,
    readyEmpty: 0,
    pendingAnnotation: 0,
    readyToTrain: 0,
    pendingItems: [],
  };

  items.forEach((item) => {
    const status = item.annotation_status || "pending";
    if (status === "drafted") {
      summary.readyLabeled += 1;
      summary.readyToTrain += 1;
      return;
    }
    if (status === "ready_empty") {
      summary.readyEmpty += 1;
      summary.readyToTrain += 1;
      return;
    }
    summary.pendingAnnotation += 1;
    summary.pendingItems.push(item);
  });

  return summary;
}

function formatRetrainExportAdvice(item) {
  const annotationStatus = item.annotation_status || "pending";
  if (annotationStatus === "drafted") {
    return "可直接训练";
  }
  if (annotationStatus === "ready_empty") {
    return "负样本可直接训练";
  }
  return "需先补标";
}

function formatModelTypeLabel(value) {
  return value ? String(value).toUpperCase() : "-";
}

function formatOptionalPercent(value, digits = 2) {
  return value == null || value === "" ? "-" : formatPercent(value, digits);
}

function formatModelSourceLabel(model) {
  return model.source === "default" ? "内置" : "上传";
}

function buildModelBenchmarkSummaryText(model) {
  const parts = [
    model.benchmark_pytorch_average_ms != null ? `PT ${formatNumber(model.benchmark_pytorch_average_ms, 2)} ms` : "",
    model.benchmark_onnx_average_ms != null ? `ONNX ${formatNumber(model.benchmark_onnx_average_ms, 2)} ms` : "",
    model.benchmark_tensorrt_average_ms != null ? `TRT ${formatNumber(model.benchmark_tensorrt_average_ms, 2)} ms` : "",
    model.benchmark_speedup_vs_pytorch != null ? `${formatNumber(model.benchmark_speedup_vs_pytorch, 2)}x` : "",
    model.benchmark_tensorrt_speedup_vs_pytorch != null ? `TRT ${formatNumber(model.benchmark_tensorrt_speedup_vs_pytorch, 2)}x` : "",
  ].filter(Boolean);
  return parts.join(" · ");
}

function deriveModelRecommendation(model) {
  if (model.is_active) {
    return "当前启用";
  }
  if (model.benchmark_tensorrt_average_ms != null || model.benchmark_onnx_average_ms != null) {
    return "部署优先候选";
  }
  if (model.benchmark_onnx_average_ms != null || model.benchmark_pytorch_average_ms != null) {
    return "待对比候选";
  }
  return "待评测";
}

function buildActiveModelOverviewHtml(model) {
  const benchmarkText = buildModelBenchmarkSummaryText(model);
  const recommendation = deriveModelRecommendation(model);

  return `
    <div class="result-mini">
      <div>
        <strong>${escapeHtml(model.name)}</strong>
        <span>${escapeHtml(model.type.toUpperCase())} · ${escapeHtml(model.yaml_name || "未绑定 YAML")}</span>
      </div>
      ${createStatusPill(state.health?.status === "ok" ? "detected" : "failed")}
    </div>
    <div class="summary-row">
      ${createSummaryPill("类别数", `${model.class_names.length}`)}
      ${createSummaryPill("大小", formatSizeMb(model.size_mb))}
      ${createSummaryPill("来源", formatModelSourceLabel(model))}
      ${createSummaryPill("角色", recommendation)}
    </div>
    ${
      benchmarkText
        ? `<div class="helper-note">最近评测：${escapeHtml(benchmarkText)}${model.benchmarked_at ? ` · ${escapeHtml(formatDateTime(model.benchmarked_at))}` : ""}</div>`
        : '<div class="helper-note">当前模型还没有 Benchmark 摘要，建议在“部署与评测”中跑一轮对比。</div>'
    }
  `;
}

function renderEmpty(container, text) {
  const compact =
    container.classList.contains("summary-row") ||
    container.classList.contains("chip-list") ||
    container.classList.contains("inline-links");
  container.innerHTML = compact
    ? `<span class="table-muted">${escapeHtml(text)}</span>`
    : `<div class="empty-state">${escapeHtml(text)}</div>`;
}

function showNotice(element, message, tone = "ok") {
  if (!element) {
    return;
  }
  if (!message) {
    clearNotice(element);
    return;
  }
  element.textContent = message;
  element.className = `notice is-visible ${tone}`;
}

function clearNotice(element) {
  if (!element) {
    return;
  }
  element.textContent = "";
  element.className = "notice";
}

function showOverlay(title, detail, options = {}) {
  state.overlayStartedAt = Date.now();
  dom.overlay.hidden = false;
  dom.overlayTitle.textContent = title || "处理中...";
  dom.overlayDetail.textContent = detail || "请稍候";
  dom.overlaySpinner.hidden = Boolean(options.hideSpinner);
  if (typeof options.progress === "number") {
    dom.overlayProgressBlock.hidden = false;
    updateOverlayProgress(options.progress, options.loadedBytes || 0, options.totalBytes || 0);
  } else {
    dom.overlayProgressBlock.hidden = true;
    dom.overlayProgressBar.style.width = "0%";
    dom.overlayProgressValue.textContent = "0%";
    dom.overlaySpeed.textContent = "0 MB/s";
    dom.overlayEta.textContent = "ETA --";
  }
}

function updateOverlay(text) {
  if (!dom.overlay.hidden) {
    dom.overlayDetail.textContent = text;
  }
}

function updateOverlayProgress(progress, loadedBytes = 0, totalBytes = 0) {
  const percent = Math.max(0, Math.min(100, Number(progress) || 0));
  dom.overlayProgressBlock.hidden = false;
  dom.overlayProgressBar.style.width = `${percent}%`;
  dom.overlayProgressValue.textContent = `${percent.toFixed(0)}%`;

  const elapsedSeconds = Math.max((Date.now() - state.overlayStartedAt) / 1000, 0.001);
  const speed = loadedBytes > 0 ? loadedBytes / elapsedSeconds : 0;
  const remaining = totalBytes > 0 && speed > 0 ? (totalBytes - loadedBytes) / speed : null;
  dom.overlaySpeed.textContent = `${(speed / 1024 / 1024).toFixed(2)} MB/s`;
  dom.overlayEta.textContent = remaining == null || !Number.isFinite(remaining) ? "ETA --" : `ETA ${Math.ceil(remaining)}s`;
}

function hideOverlay() {
  dom.overlay.hidden = true;
  dom.overlayProgressBlock.hidden = true;
  dom.overlaySpinner.hidden = false;
}

function buildError(message, payload, status) {
  const error = new Error(message || "请求失败");
  error.payload = payload || null;
  error.status = status || 0;
  return error;
}

function extractErrorMessage(payload, fallback = "请求失败") {
  if (!payload) {
    return fallback;
  }
  return payload.error?.message || payload.message || payload.detail || fallback;
}

async function apiRequest(path, options = {}) {
  const response = await fetch(resolveUrl(path), {
    credentials: "same-origin",
    ...options,
    headers: {
      Accept: "application/json",
      ...(options.body instanceof FormData ? {} : options.body ? { "Content-Type": "application/json" } : {}),
      ...(options.headers || {}),
    },
  });

  const text = await response.text();
  let payload = null;
  if (text) {
    try {
      payload = JSON.parse(text);
    } catch {
      payload = null;
    }
  }

  if (!response.ok) {
    throw buildError(extractErrorMessage(payload, response.statusText || "请求失败"), payload, response.status);
  }
  if (payload && payload.success === false) {
    throw buildError(extractErrorMessage(payload), payload, response.status);
  }
  return payload?.data ?? payload;
}

function apiGet(path) {
  return apiRequest(path, { method: "GET" });
}

function apiDelete(path) {
  return apiRequest(path, { method: "DELETE" });
}

function apiPostJson(path, body) {
  return apiRequest(path, { method: "POST", body: JSON.stringify(body) });
}

function apiPutJson(path, body) {
  return apiRequest(path, { method: "PUT", body: JSON.stringify(body) });
}

function uploadForm(path, formData, title, detail) {
  showOverlay(title, detail, { progress: 0 });
  return xhrRequest({
    method: "POST",
    path,
    body: formData,
    onProgress: (progress, loaded, total) => {
      updateOverlayProgress(progress, loaded, total);
      updateOverlay(detail);
    },
  });
}

function xhrRequest({ method = "POST", path, body = null, responseType = "json", onProgress = null }) {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    xhr.open(method, resolveUrl(path), true);
    xhr.responseType = responseType === "blob" ? "blob" : "text";
    xhr.setRequestHeader("Accept", "application/json");

    const handleProgress = (event) => {
      if (!onProgress || !event.lengthComputable) {
        return;
      }
      const progress = event.total > 0 ? (event.loaded / event.total) * 100 : 0;
      onProgress(progress, event.loaded, event.total);
    };

    if (xhr.upload) {
      xhr.upload.onprogress = handleProgress;
    }
    xhr.onprogress = handleProgress;

    xhr.onerror = () => {
      reject(buildError("网络请求失败，请确认后端服务可访问。"));
    };

    xhr.onload = () => {
      if (responseType === "blob") {
        if (xhr.status >= 200 && xhr.status < 300) {
          resolve(xhr.response);
          return;
        }
        reject(buildError("下载失败", null, xhr.status));
        return;
      }

      let payload = null;
      if (xhr.responseText) {
        try {
          payload = JSON.parse(xhr.responseText);
        } catch {
          payload = null;
        }
      }

      if (xhr.status < 200 || xhr.status >= 300) {
        reject(buildError(extractErrorMessage(payload, "请求失败"), payload, xhr.status));
        return;
      }
      if (payload && payload.success === false) {
        reject(buildError(extractErrorMessage(payload), payload, xhr.status));
        return;
      }
      resolve(payload?.data ?? payload);
    };

    xhr.send(body);
  });
}

async function downloadBlob(url, filename) {
  try {
    showOverlay("下载文件", `正在下载 ${filename}`, { progress: 0 });
    const blob = await xhrRequest({
      method: "GET",
      path: url,
      responseType: "blob",
      onProgress: (progress, loaded, total) => {
        updateOverlayProgress(progress, loaded, total);
        updateOverlay(`正在下载 ${filename}`);
      },
    });

    const objectUrl = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = objectUrl;
    anchor.download = filename;
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
    URL.revokeObjectURL(objectUrl);
  } finally {
    hideOverlay();
  }
}

async function waitForTask(taskId, { title, onUpdate } = {}) {
  showOverlay(title || "处理中...", "任务已创建，正在等待后端执行...", { progress: 0, hideSpinner: true });

  while (true) {
    const task = await apiGet(`${API_BASE}/tasks/${encodeURIComponent(taskId)}`);
    if (typeof onUpdate === "function") {
      onUpdate(task);
    }
    updateOverlay(task.message || "处理中...");
    updateOverlayProgress(task.progress || 0);

    if (task.status === "succeeded") {
      hideOverlay();
      return task;
    }
    if (task.status === "failed") {
      hideOverlay();
      throw buildError(task.error_message || task.message || "任务执行失败", task, 500);
    }
    await sleep(900);
  }
}

function activeModelDescriptor() {
  return state.modelInventory?.models?.find((item) => item.is_active) || null;
}

function updateActiveContextLines() {
  const model = activeModelDescriptor();
  const classNames = state.modelInventory?.active_class_names || [];
  const text = model
    ? `当前模型：${model.name} · ${model.type.toUpperCase()} · ${classNames.length} 个类别`
    : "当前没有可用模型，请先在模型中心启用模型。";
  [dom.singleActiveModel, dom.batchActiveModel, dom.webcamActiveModel, dom.deploymentCurrentTarget].forEach((node) => {
    node.textContent = text;
  });
}

function renderHeader() {
  const health = state.health;
  const online = health?.status === "ok";
  dom.serviceIndicator.classList.toggle("online", online);
  dom.serviceIndicator.classList.toggle("offline", Boolean(health) && !online);
  dom.modelBadge.textContent = health?.active_model_name || state.modelInventory?.active_model_name || "未加载模型";
  updateActiveContextLines();
}

function renderOverview() {
  renderOverviewModelCard();
  renderOverviewClasses();
  renderOverviewRecentRuns();
  renderOverviewDashboardStats();
  renderOverviewStatusBoard();
  renderOverviewOpsBoard();
  renderOverviewTrend();
}

async function loadHealth(silent = false) {
  try {
    state.health = await apiGet(`${API_BASE}/system/health`);
    renderHeader();
    if (!silent) {
      clearNotice(dom.overviewNotice);
    }
  } catch (error) {
    state.health = null;
    renderHeader();
    if (!silent) {
      showNotice(dom.overviewNotice, error.message, "error");
    }
  }
}

async function loadModels(silent = false) {
  try {
    state.modelInventory = await apiGet(`${API_BASE}/models`);
    renderHeader();
    renderOverview();
    renderModelSummary();
    renderModelComparison();
    renderModelList();
    if (!silent) {
      clearNotice(dom.modelNotice);
    }
  } catch (error) {
    state.modelInventory = null;
    renderHeader();
    renderOverview();
    renderModelSummary();
    renderModelComparison();
    renderModelList();
    if (!silent) {
      showNotice(dom.modelNotice, error.message, "error");
    }
  }
}

async function loadDashboardSummary(silent = false) {
  try {
    state.dashboardSummary = await apiGet(`${API_BASE}/dashboard/summary?days=7`);
    renderOverview();
    if (!silent) {
      clearNotice(dom.overviewNotice);
    }
  } catch (error) {
    state.dashboardSummary = null;
    renderOverview();
    if (!silent) {
      showNotice(dom.overviewNotice, error.message, "error");
    }
  }
}

async function loadDeployment(silent = false) {
  try {
    state.deployment = await apiGet(`${API_BASE}/deployment/status`);
    renderDeploymentStatus();
    if (!silent) {
      clearNotice(dom.deploymentNotice);
    }
  } catch (error) {
    state.deployment = null;
    renderDeploymentStatus();
    if (!silent) {
      showNotice(dom.deploymentNotice, error.message, "error");
    }
  }
}

async function loadQualityRules(silent = false) {
  try {
    state.qualityRules = await apiGet(`${API_BASE}/settings/quality-rules`);
    renderQualityRules();
    if (!silent) {
      clearNotice(dom.settingsNotice);
    }
  } catch (error) {
    state.qualityRules = null;
    renderQualityRules();
    if (!silent) {
      showNotice(dom.settingsNotice, error.message, "error");
    }
  }
}

async function loadReviewSummary(silent = false) {
  try {
    state.reviewSummary = await apiGet(`${API_BASE}/review/summary`);
    renderReviewSummary();
    if (!silent) {
      clearNotice(dom.reviewNotice);
    }
  } catch (error) {
    state.reviewSummary = null;
    renderReviewSummary();
    if (!silent) {
      showNotice(dom.reviewNotice, error.message, "error");
    }
  }
}

async function loadFeedbackPoolSummary(silent = false) {
  if (state.reviewQueue !== "feedback") {
    state.feedbackPoolSummary = null;
    renderFeedbackPoolSummary();
    updateReviewModeButtons();
    return;
  }

  try {
    const params = new URLSearchParams();
    if (state.reviewDecisionFilter && state.reviewDecisionFilter !== "all") {
      params.set("decision", state.reviewDecisionFilter);
    }
    if (state.reviewModeFilter && state.reviewModeFilter !== "all") {
      params.set("mode", state.reviewModeFilter);
    }
    if (state.reviewKeyword.trim()) {
      params.set("keyword", state.reviewKeyword.trim());
    }
    state.feedbackPoolSummary = await apiGet(`${API_BASE}/review/feedback/summary?${params.toString()}`);
    renderFeedbackPoolSummary();
    updateReviewModeButtons();
    if (!silent) {
      clearNotice(dom.reviewNotice);
    }
  } catch (error) {
    state.feedbackPoolSummary = null;
    renderFeedbackPoolSummary();
    updateReviewModeButtons();
    if (!silent) {
      showNotice(dom.reviewNotice, error.message, "error");
    }
  }
}

async function loadReviewItems(silent = false) {
  try {
    const params = new URLSearchParams({
      limit: "40",
      queue: state.reviewQueue,
    });
    if (state.reviewDecisionFilter && state.reviewDecisionFilter !== "all") {
      params.set("decision", state.reviewDecisionFilter);
    }
    if (state.reviewQueue === "feedback") {
      if (state.reviewModeFilter && state.reviewModeFilter !== "all") {
        params.set("mode", state.reviewModeFilter);
      }
      if (state.reviewKeyword.trim()) {
        params.set("keyword", state.reviewKeyword.trim());
      }
    }
    state.reviewItems = await apiGet(`${API_BASE}/review/items?${params.toString()}`);
    if (state.selectedReviewItemId && !state.reviewItems.some((item) => item.item_id === state.selectedReviewItemId)) {
      state.selectedReviewItemId = null;
      state.reviewDetail = null;
    }
    renderReviewList();
    renderReviewDetail();
    updateReviewQueueButtons();
    updateReviewDecisionButtons();
    updateReviewModeButtons();
    renderFeedbackPoolSummary();
    if (!silent) {
      clearNotice(dom.reviewNotice);
    }
  } catch (error) {
    state.reviewItems = [];
    state.selectedReviewItemId = null;
    state.reviewDetail = null;
    renderReviewList();
    renderReviewDetail();
    renderFeedbackPoolSummary();
    updateReviewModeButtons();
    if (!silent) {
      showNotice(dom.reviewNotice, error.message, "error");
    }
  }
}

async function loadReviewDetail(itemId, silent = false) {
  if (!itemId) {
    state.selectedReviewItemId = null;
    state.reviewDetail = null;
    renderReviewList();
    renderReviewDetail();
    return;
  }
  try {
    state.selectedReviewItemId = itemId;
    state.reviewDetail = await apiGet(`${API_BASE}/review/items/${itemId}`);
    renderReviewList();
    renderReviewDetail();
    if (!silent) {
      clearNotice(dom.reviewNotice);
    }
  } catch (error) {
    state.reviewDetail = null;
    renderReviewDetail();
    if (!silent) {
      showNotice(dom.reviewNotice, error.message, "error");
    }
  }
}

function buildRetrainQueryParams(includeLimit = true) {
  const params = new URLSearchParams();
  if (includeLimit) {
    params.set("limit", "40");
  }
  if (state.retrainStatusFilter && state.retrainStatusFilter !== "all") {
    params.set("status", state.retrainStatusFilter);
  }
  if (state.retrainDecisionFilter && state.retrainDecisionFilter !== "all") {
    params.set("decision", state.retrainDecisionFilter);
  }
  if (state.retrainModeFilter && state.retrainModeFilter !== "all") {
    params.set("mode", state.retrainModeFilter);
  }
  if (state.retrainKeyword.trim()) {
    params.set("keyword", state.retrainKeyword.trim());
  }
  return params;
}

async function loadRetrainSummary(silent = false) {
  try {
    const params = buildRetrainQueryParams(false);
    state.retrainSummary = await apiGet(`${API_BASE}/retrain/summary?${params.toString()}`);
    renderRetrainSummary();
    updateRetrainFilterButtons();
    if (!silent) {
      clearNotice(dom.retrainNotice);
    }
  } catch (error) {
    state.retrainSummary = null;
    renderRetrainSummary();
    updateRetrainFilterButtons();
    if (!silent) {
      showNotice(dom.retrainNotice, error.message, "error");
    }
  }
}

async function loadRetrainBatchSummary(silent = false) {
  try {
    state.retrainBatchSummary = await apiGet(`${API_BASE}/retrain/batches/summary`);
    renderRetrainBatchSummary();
    renderRetrainSelectionHint();
    if (!silent) {
      clearNotice(dom.retrainNotice);
    }
  } catch (error) {
    state.retrainBatchSummary = null;
    renderRetrainBatchSummary();
    renderRetrainSelectionHint();
    if (!silent) {
      showNotice(dom.retrainNotice, error.message, "error");
    }
  }
}

async function loadRetrainBatches(silent = false) {
  try {
    state.retrainBatches = await apiGet(`${API_BASE}/retrain/batches?limit=8`);
    renderRetrainBatchList();
    renderRetrainSelectionHint();
    if (
      state.selectedRetrainBatchId &&
      !state.retrainBatches.some((item) => item.batch_id === state.selectedRetrainBatchId)
    ) {
      state.selectedRetrainBatchId = state.retrainBatchDetail?.batch_id || state.selectedRetrainBatchId;
    }
    if (!silent) {
      clearNotice(dom.retrainNotice);
    }
  } catch (error) {
    state.retrainBatches = [];
    renderRetrainBatchList();
    renderRetrainSelectionHint();
    if (!silent) {
      showNotice(dom.retrainNotice, error.message, "error");
    }
  }
}

async function loadRetrainItems(silent = false) {
  try {
    const params = buildRetrainQueryParams(true);
    state.retrainItems = await apiGet(`${API_BASE}/retrain/items?${params.toString()}`);
    const visibleEligibleIds = new Set(
      state.retrainItems.filter((item) => isRetrainBatchSelectable(item)).map((item) => item.item_id)
    );
    state.selectedRetrainCatalogIds = new Set(
      Array.from(state.selectedRetrainCatalogIds).filter((itemId) => visibleEligibleIds.has(itemId))
    );
    if (state.selectedRetrainItemId && !state.retrainItems.some((item) => item.item_id === state.selectedRetrainItemId)) {
      state.selectedRetrainItemId = null;
      state.retrainDetail = null;
    }
    renderRetrainList();
    renderRetrainDetail();
    renderRetrainSelectionHint();
    updateRetrainFilterButtons();
    if (!silent) {
      clearNotice(dom.retrainNotice);
    }
  } catch (error) {
    state.retrainItems = [];
    state.selectedRetrainCatalogIds = new Set();
    state.selectedRetrainItemId = null;
    state.retrainDetail = null;
    renderRetrainList();
    renderRetrainDetail();
    renderRetrainSelectionHint();
    updateRetrainFilterButtons();
    if (!silent) {
      showNotice(dom.retrainNotice, error.message, "error");
    }
  }
}

async function loadRetrainDetail(itemId, silent = false) {
  if (!itemId) {
    state.selectedRetrainItemId = null;
    state.retrainDetail = null;
    renderRetrainList();
    renderRetrainDetail();
    return;
  }
  try {
    state.selectedRetrainItemId = itemId;
    state.retrainDetail = await apiGet(`${API_BASE}/retrain/items/${itemId}`);
    renderRetrainList();
    renderRetrainDetail();
    if (!silent) {
      clearNotice(dom.retrainNotice);
    }
  } catch (error) {
    state.retrainDetail = null;
    renderRetrainDetail();
    if (!silent) {
      showNotice(dom.retrainNotice, error.message, "error");
    }
  }
}

async function loadRetrainBatchDetail(batchId, silent = false) {
  if (!batchId) {
    state.selectedRetrainBatchId = null;
    state.retrainBatchDetail = null;
    renderRetrainBatchList();
    renderRetrainBatchDetail();
    return;
  }
  try {
    state.selectedRetrainBatchId = batchId;
    state.retrainBatchDetail = await apiGet(`${API_BASE}/retrain/batches/${batchId}`);
    renderRetrainBatchList();
    renderRetrainBatchDetail();
    if (!silent) {
      clearNotice(dom.retrainNotice);
    }
  } catch (error) {
    state.retrainBatchDetail = null;
    renderRetrainBatchDetail();
    if (!silent) {
      showNotice(dom.retrainNotice, error.message, "error");
    }
  }
}

async function loadHistory(silent = false) {
  try {
    state.historyRuns = await apiGet(`${API_BASE}/history/runs?limit=50`);
    state.selectedHistoryIds = new Set(
      Array.from(state.selectedHistoryIds).filter((id) => state.historyRuns.some((item) => item.id === id))
    );
    if (state.selectedHistoryId && !state.historyRuns.some((item) => item.id === state.selectedHistoryId)) {
      state.selectedHistoryId = null;
      state.historyDetail = null;
    }
    renderOverview();
    renderHistoryList();
    renderHistoryDetail();
    if (!silent) {
      clearNotice(dom.historyNotice);
    }
  } catch (error) {
    state.historyRuns = [];
    state.historyDetail = null;
    state.selectedHistoryId = null;
    renderOverview();
    renderHistoryList();
    renderHistoryDetail();
    if (!silent) {
      showNotice(dom.historyNotice, error.message, "error");
    }
  }
}

async function loadHistoryDetail(runId, silent = false) {
  try {
    state.historyDetail = await apiGet(`${API_BASE}/history/runs/${runId}`);
    state.selectedHistoryId = runId;
    renderHistoryList();
    renderHistoryDetail();
    if (!silent) {
      clearNotice(dom.historyNotice);
    }
  } catch (error) {
    if (!silent) {
      showNotice(dom.historyNotice, error.message, "error");
    }
  }
}

async function loadStorage(silent = false) {
  try {
    state.storage = await apiGet(`${API_BASE}/maintenance/storage`);
    state.selectedArtifacts = new Set(
      Array.from(state.selectedArtifacts).filter((name) => state.storage?.artifacts?.some((item) => item.name === name))
    );
    renderStorageSummary();
    renderArtifactList();
    if (!silent) {
      clearNotice(dom.cleanupNotice);
    }
  } catch (error) {
    state.storage = null;
    renderStorageSummary();
    renderArtifactList();
    if (!silent) {
      showNotice(dom.cleanupNotice, error.message, "error");
    }
  }
}

function renderOverviewModelCard() {
  const model = activeModelDescriptor();
  if (!model) {
    renderEmpty(dom.overviewModelCard, "当前没有已启用模型");
  } else {
    dom.overviewModelCard.innerHTML = buildActiveModelOverviewHtml(model);
  }

  dom.overviewQuickLinks.innerHTML = OVERVIEW_SHORTCUT_GROUPS.map(
    (group) => `
      <section class="shortcut-group">
        <div class="shortcut-group-head">
          <strong>${escapeHtml(group.title)}</strong>
          <span>${escapeHtml(group.description)}</span>
        </div>
        <div class="shortcut-links">
          ${group.links
            .map(
              (item) => `
                <a class="shortcut-link" href="#${escapeHtml(item.panel)}" data-jump-panel="${escapeHtml(item.panel)}">
                  ${escapeHtml(item.label)}
                </a>
              `
            )
            .join("")}
        </div>
      </section>
    `
  ).join("");
}

function renderOverviewClasses() {
  const classNames = state.modelInventory?.active_class_names || [];
  if (!classNames.length) {
    renderEmpty(dom.overviewClassList, "暂无类别映射");
    return;
  }
  dom.overviewClassList.innerHTML = classNames.map((item) => `<span class="chip">${escapeHtml(item)}</span>`).join("");
}

function renderOverviewRecentRuns() {
  const runs = state.historyRuns.slice(0, 6);
  if (!runs.length) {
    renderEmpty(dom.overviewRecentRuns, "暂无检测记录");
    return;
  }
  dom.overviewRecentRuns.innerHTML = runs
    .map(
      (item) => `
        <div class="history-item">
          <button type="button" data-history-id="${item.id}">
            <strong>#${item.id} · ${escapeHtml(formatMode(item.mode))}</strong>
            <small>${escapeHtml(formatDateTime(item.created_at))} · ${item.successful_files}/${item.total_files} 成功 · ${item.total_detections} 个目标</small>
          </button>
        </div>
      `
    )
    .join("");
}

function createOverviewMetricRow(label, count, ratio, tone = "neutral") {
  const percent = Math.max(0, Math.min(100, Number(ratio || 0) * 100));
  return `
    <div class="overview-metric-row">
      <div class="overview-metric-head">
        <strong>${escapeHtml(label)}</strong>
        <span>${escapeHtml(`${count}`)} · ${percent.toFixed(1)}%</span>
      </div>
      <div class="overview-metric-track">
        <span class="overview-metric-bar ${escapeHtml(tone)}" style="width: ${percent}%;"></span>
      </div>
    </div>
  `;
}

function renderOverviewDashboardStats() {
  const summary = state.dashboardSummary;
  if (!summary) {
    renderEmpty(dom.overviewDashboardStats, "统计数据未加载");
    return;
  }
  const activeModel = activeModelDescriptor();

  dom.overviewDashboardStats.innerHTML = [
    createSummaryPill("累计记录", `${summary.total_runs || 0}`),
    createSummaryPill("累计样本", `${summary.total_samples || 0}`),
    createSummaryPill("检测成功率", formatPercent(summary.success_rate || 0)),
    createSummaryPill("累计目标", `${summary.total_detections || 0}`),
    createSummaryPill("待复核", `${summary.review_pending_count || 0}`),
    createSummaryPill("回流中", `${summary.feedback_queued_count || 0}`),
    createSummaryPill("待复训", `${summary.retrain_ready_count || 0}`),
    createSummaryPill("已入训练", `${summary.retrain_used_count || 0}`),
    createSummaryPill("最近记录", formatDateTime(summary.latest_run_at) || "-"),
    activeModel?.benchmark_onnx_average_ms != null ? createSummaryPill("当前 ONNX 延迟", `${formatNumber(activeModel.benchmark_onnx_average_ms, 2)} ms`) : "",
    activeModel?.benchmark_tensorrt_average_ms != null ? createSummaryPill("当前 TRT 延迟", `${formatNumber(activeModel.benchmark_tensorrt_average_ms, 2)} ms`) : "",
  ].join("");
}

function renderOverviewStatusBoard() {
  const summary = state.dashboardSummary;
  if (!summary) {
    renderEmpty(dom.overviewStatusBoard, "统计数据未加载");
    return;
  }

  const total = Math.max(Number(summary.total_samples) || 0, 1);
  const counts = summary.quality_status_counts || {};
  const rows = [
    { key: "pass", label: "通过", tone: "pass" },
    { key: "warning", label: "预警", tone: "warning" },
    { key: "critical", label: "严重", tone: "critical" },
    { key: "no_detection", label: "无目标", tone: "neutral" },
    { key: "failed", label: "失败", tone: "failed" },
  ].map((item) => createOverviewMetricRow(item.label, counts[item.key] || 0, (counts[item.key] || 0) / total, item.tone)).join("");

  dom.overviewStatusBoard.innerHTML = rows || '<div class="empty-state">暂无质检统计</div>';
}

function renderOverviewOpsBoard() {
  const summary = state.dashboardSummary;
  if (!summary) {
    renderEmpty(dom.overviewOpsBoard, "统计数据未加载");
    return;
  }
  const activeModel = activeModelDescriptor();

  const total = Math.max(Number(summary.total_samples) || 0, 1);
  const rows = [
    { label: "待复核", value: summary.review_pending_count || 0, tone: "warning" },
    { label: "已复核", value: summary.reviewed_count || 0, tone: "pass" },
    { label: "回流队列", value: summary.feedback_queued_count || 0, tone: "detected" },
    { label: "复训待处理", value: summary.retrain_pending_count || 0, tone: "neutral" },
    { label: "待复训", value: summary.retrain_ready_count || 0, tone: "warning" },
    { label: "已入训练", value: summary.retrain_used_count || 0, tone: "pass" },
  ].map((item) => createOverviewMetricRow(item.label, item.value, item.value / total, item.tone)).join("");

  const modeCounts = summary.mode_sample_counts || {};
  dom.overviewOpsBoard.innerHTML = `
    ${rows}
    <div class="surface-divider"></div>
    <div class="summary-row">
      ${createSummaryPill("单图样本", `${modeCounts.single || 0}`)}
      ${createSummaryPill("批量样本", `${modeCounts.batch || 0}`)}
      ${createSummaryPill("摄像头样本", `${modeCounts.webcam || 0}`)}
      ${createSummaryPill("平均每次检测样本", `${formatNumber(summary.avg_samples_per_run || 0, 2)}`)}
      ${createSummaryPill("平均每次检测目标", `${formatNumber(summary.avg_detections_per_run || 0, 2)}`)}
    </div>
    <div class="surface-divider"></div>
    <div class="summary-row">
      ${createSummaryPill("当前模型角色", activeModel ? deriveModelRecommendation(activeModel) : "-")}
      ${createSummaryPill("当前模型来源", activeModel ? formatModelSourceLabel(activeModel) : "-")}
      ${createSummaryPill("闭环阶段", summary.retrain_ready_count > 0 ? "回流待复训" : summary.feedback_queued_count > 0 ? "回流处理中" : "主链路稳定")}
    </div>
  `;
}

function renderOverviewTrend() {
  const summary = state.dashboardSummary;
  if (!summary) {
    renderEmpty(dom.overviewTrend, "统计数据未加载");
    return;
  }

  const stats = summary.recent_daily_stats || [];
  if (!stats.length) {
    renderEmpty(dom.overviewTrend, "最近 7 天暂无统计");
    return;
  }

  const maxSampleCount = Math.max(...stats.map((item) => Number(item.sample_count) || 0), 1);
  dom.overviewTrend.innerHTML = stats
    .map((item) => {
      const sampleRatio = ((Number(item.sample_count) || 0) / maxSampleCount) * 100;
      return `
        <article class="overview-trend-card">
          <div class="overview-trend-head">
            <strong>${escapeHtml(String(item.date || "").slice(5))}</strong>
            <span>${escapeHtml(`${item.sample_count || 0} 样本`)}</span>
          </div>
          <div class="overview-trend-bar">
            <span style="height: ${Math.max(sampleRatio, 8)}%;"></span>
          </div>
          <div class="overview-trend-meta">
            <span>运行 ${item.run_count || 0}</span>
            <span>目标 ${item.detection_count || 0}</span>
            <span>回流 ${item.feedback_count || 0}</span>
            <span>入目录 ${item.retrain_count || 0}</span>
          </div>
        </article>
      `;
    })
    .join("");
}

function renderModelSummary() {
  const inventory = state.modelInventory;
  if (!inventory) {
    renderEmpty(dom.modelSummary, "模型数据未加载");
    return;
  }
  const models = inventory.models || [];
  const uploadedCount = models.filter((item) => item.source === "uploaded").length;
  const benchmarkedCount = models.filter((item) => item.benchmarked_at).length;
  const recommendedCount = models.filter((item) => deriveModelRecommendation(item) === "部署优先候选").length;
  const totalSizeMb = models.reduce((sum, item) => sum + (Number(item.size_mb) || 0), 0);
  dom.modelSummary.innerHTML = [
    createSummaryPill("模型总数", `${models.length}`),
    createSummaryPill("上传模型", `${uploadedCount}`),
    createSummaryPill("已评测", `${benchmarkedCount}`),
    createSummaryPill("部署候选", `${recommendedCount}`),
    createSummaryPill("当前启用", inventory.active_model_name || "未启用"),
    createSummaryPill("类别数", `${inventory.active_class_names.length}`),
    createSummaryPill("格式", inventory.active_model_type ? inventory.active_model_type.toUpperCase() : "-"),
    createSummaryPill("总占用", formatSizeMb(totalSizeMb)),
  ].join("");
}

function renderModelComparison() {
  const inventory = state.modelInventory;
  if (!inventory) {
    renderEmpty(dom.modelCompareBoard, "模型数据未加载");
    return;
  }

  const models = inventory.models || [];
  if (!models.length) {
    renderEmpty(dom.modelCompareBoard, "暂无模型，请先上传");
    return;
  }

  const rows = models
    .map((model) => {
      const statusParts = [
        createStatusPill(model.is_active ? "detected" : "no_detection"),
        model.is_active ? '<span class="chip chip-accent">当前启用</span>' : "",
        model.is_default ? '<span class="chip">默认</span>' : '<span class="chip">可切换</span>',
      ].join("");
      const classPreview = model.class_names.length
        ? `${model.class_names.slice(0, 3).join(" / ")}${model.class_names.length > 3 ? " ..." : ""}`
        : "未配置";
      const benchmarkPreview = buildModelBenchmarkSummaryText(model) || "-";
      const recommendation = deriveModelRecommendation(model);

      return `
        <tr>
          <td>
            <div class="compare-model-cell">
              <strong>${escapeHtml(model.name)}</strong>
              <small>${escapeHtml(model.id)}</small>
            </div>
          </td>
          <td>${escapeHtml(model.type.toUpperCase())}</td>
          <td>${formatSizeMb(model.size_mb)}</td>
          <td>${escapeHtml(formatModelSourceLabel(model))}</td>
          <td>${model.class_names.length}</td>
          <td>${escapeHtml(model.yaml_name || "未上传")}</td>
          <td>
            <div class="compare-class-cell">
              <span>${escapeHtml(classPreview)}</span>
            </div>
          </td>
          <td>${escapeHtml(benchmarkPreview)}</td>
          <td>${escapeHtml(recommendation)}</td>
          <td>
            <div class="compare-status-cell">${statusParts}</div>
          </td>
        </tr>
      `;
    })
    .join("");

  dom.modelCompareBoard.innerHTML = `
    <table class="data-table">
      <thead>
        <tr>
          <th>模型</th>
          <th>格式</th>
          <th>大小</th>
          <th>来源</th>
          <th>类别数</th>
          <th>YAML</th>
          <th>类别预览</th>
          <th>延迟摘要</th>
          <th>推荐角色</th>
          <th>状态</th>
        </tr>
      </thead>
      <tbody>${rows}</tbody>
    </table>
  `;
}

function renderModelList() {
  const models = state.modelInventory?.models || [];
  if (!models.length) {
    renderEmpty(dom.modelList, "暂无模型，请先上传");
    return;
  }

  dom.modelList.innerHTML = models
    .map((model) => {
      const classesHtml = model.class_names.length
        ? model.class_names.map((item) => `<span class="chip">${escapeHtml(item)}</span>`).join("")
        : '<span class="chip">未提供类别</span>';

      const actions = model.is_active
        ? '<button class="btn btn-secondary table-action-btn" type="button" disabled>当前使用中</button>'
        : `<button class="btn btn-primary table-action-btn" type="button" data-model-activate="${escapeHtml(model.id)}">启用</button>`;

      const deleteAction = model.can_delete
        ? `<button class="btn btn-ghost table-action-btn" type="button" data-model-delete="${escapeHtml(model.id)}" data-model-name="${escapeHtml(model.name)}">删除</button>`
        : "";
      const benchmarkText = buildModelBenchmarkSummaryText(model);
      const recommendation = deriveModelRecommendation(model);

      return `
        <article class="model-card ${model.is_active ? "is-active" : ""}">
          <div class="model-card-head">
            <div>
              <h4 class="model-card-title">${escapeHtml(model.name)}</h4>
              <p class="model-card-subtitle">${escapeHtml(model.type.toUpperCase())} · ${formatSizeMb(model.size_mb)} · ${escapeHtml(formatModelSourceLabel(model))}</p>
            </div>
            ${createStatusPill(model.is_active ? "detected" : "no_detection")}
          </div>
          <div class="summary-row">
            ${createSummaryPill("YAML", model.yaml_name || "未上传")}
            ${createSummaryPill("类别", `${model.class_names.length}`)}
            ${createSummaryPill("默认", model.is_default ? "是" : "否")}
            ${benchmarkText ? createSummaryPill("延迟", benchmarkText) : ""}
            ${createSummaryPill("推荐", recommendation)}
          </div>
          ${model.benchmarked_at ? `<div class="helper-note">最近评测：${escapeHtml(formatDateTime(model.benchmarked_at))} · imgsz ${model.benchmark_image_size || "-"} · conf ${model.benchmark_confidence_threshold ?? "-"}</div>` : ""}
          <div class="model-classes">${classesHtml}</div>
          <div class="model-card-actions">${actions}${deleteAction}</div>
        </article>
      `;
    })
    .join("");
}

function bindModelControls() {
  dom.refreshModelsBtn.addEventListener("click", () => {
    void Promise.allSettled([loadHealth(true), loadModels(false), loadDeployment(true)]);
  });

  dom.modelUploadBtn.addEventListener("click", () => {
    void uploadModel();
  });

  dom.modelResetBtn.addEventListener("click", resetModelInputs);
}

function resetModelInputs() {
  dom.modelUploadFile.value = "";
  dom.modelYamlFile.value = "";
  dom.modelAutoActivate.checked = true;
}

async function uploadModel() {
  const file = dom.modelUploadFile.files?.[0];
  const yamlFile = dom.modelYamlFile.files?.[0] || null;
  if (!file) {
    showNotice(dom.modelNotice, "请先选择模型文件。", "warn");
    return;
  }

  const formData = new FormData();
  formData.append("file", file);
  if (yamlFile) {
    formData.append("yaml_file", yamlFile);
  }

  try {
    const created = await uploadForm(`${API_BASE}/models`, formData, "上传模型", `正在上传 ${file.name}`);
    resetModelInputs();
    await loadModels(true);
    await loadHealth(true);
    await loadDeployment(true);
    showNotice(dom.modelNotice, `模型 ${created.name} 上传成功。`, "ok");

    if (dom.modelAutoActivate.checked) {
      await activateModel(created.id, true);
      showNotice(dom.modelNotice, `模型 ${created.name} 上传并启用成功。`, "ok");
    }
  } catch (error) {
    showNotice(dom.modelNotice, error.message, "error");
  } finally {
    hideOverlay();
  }
}

async function activateModel(modelId, silent = false) {
  if (!modelId) {
    return;
  }
  try {
    showOverlay("启用模型", "正在切换当前推理模型...");
    await apiRequest(`${API_BASE}/models/${encodeURIComponent(modelId)}/activate`, { method: "POST" });
    await Promise.allSettled([loadHealth(true), loadModels(true), loadDeployment(true)]);
    if (!silent) {
      showNotice(dom.modelNotice, "模型已启用。", "ok");
    }
  } catch (error) {
    if (!silent) {
      showNotice(dom.modelNotice, error.message, "error");
    }
  } finally {
    hideOverlay();
  }
}

async function deleteModel(modelId, modelName) {
  if (!modelId) {
    return;
  }
  if (!window.confirm(`确认删除模型 ${modelName} 吗？`)) {
    return;
  }
  try {
    showOverlay("删除模型", `正在删除 ${modelName}...`);
    await apiDelete(`${API_BASE}/models/${encodeURIComponent(modelId)}`);
    await Promise.allSettled([loadHealth(true), loadModels(true), loadDeployment(true)]);
    showNotice(dom.modelNotice, `模型 ${modelName} 已删除。`, "ok");
  } catch (error) {
    showNotice(dom.modelNotice, error.message, "error");
  } finally {
    hideOverlay();
  }
}

function buildReportHtml(report, summary = null) {
  if (!report) {
    return '<div class="empty-state">等待结果</div>';
  }
  const pills = [
    createStatusPill(report.status),
    createSummaryPill("新鲜", `${report.fresh_count}`),
    createSummaryPill("腐烂", `${report.rotten_count}`),
    createSummaryPill("腐烂占比", formatPercent(report.rotten_rate)),
  ];
  if (summary) {
    pills.push(createSummaryPill("检测总数", `${summary.total_detections || 0}`));
  }
  return `
    <div class="summary-row">${pills.join("")}</div>
    <div class="result-mini">
      <strong>结论</strong>
      <span>${escapeHtml(report.recommendation || "无")}</span>
    </div>
  `;
}

function buildDetectionsTable(detections) {
  if (!detections?.length) {
    return '<div class="empty-state">暂无检测目标</div>';
  }
  const rows = detections
    .map((item) => {
      const bbox = item.bbox || {};
      const boxText = `${Math.round(bbox.x1 || 0)}, ${Math.round(bbox.y1 || 0)}, ${Math.round(bbox.x2 || 0)}, ${Math.round(bbox.y2 || 0)}`;
      return `
        <tr>
          <td>${escapeHtml(item.label)}</td>
          <td>${formatPercent(item.confidence, 1)}</td>
          <td>${escapeHtml(boxText)}</td>
        </tr>
      `;
    })
    .join("");
  return `
    <div class="table-wrap">
      <table class="data-table">
        <thead>
          <tr>
            <th>目标</th>
            <th>置信度</th>
            <th>框坐标</th>
          </tr>
        </thead>
        <tbody>${rows}</tbody>
      </table>
    </div>
  `;
}

function buildTaskCard(task, title) {
  return `
    <div class="task-progress-card">
      <div class="task-progress-head">
        <div>
          <strong>${escapeHtml(title)}</strong>
          <div class="task-progress-subtitle">${escapeHtml(task.message || "任务处理中")}</div>
        </div>
        ${createStatusPill(task.status === "failed" ? "failed" : "detected")}
      </div>
      <div class="task-progress-track">
        <div class="progress-track">
          <div class="progress-bar" style="width:${Math.max(0, Math.min(100, task.progress || 0))}%"></div>
        </div>
      </div>
      <div class="task-progress-meta">
        <span>状态：${escapeHtml(formatTaskStatus(task.status))}</span>
        <span>进度：${Math.round(task.progress || 0)}%</span>
        <span>创建时间：${escapeHtml(formatDateTime(task.created_at))}</span>
      </div>
    </div>
  `;
}

function bindSingleControls() {
  dom.singleFile.addEventListener("change", (event) => {
    const file = event.target.files?.[0] || null;
    previewSingleFile(file);
  });

  dom.singleRunBtn.addEventListener("click", () => {
    void runSinglePrediction();
  });

  dom.singleResetBtn.addEventListener("click", resetSingleView);
}

function releaseSingleSourcePreview() {
  if (state.singleSourceUrl) {
    URL.revokeObjectURL(state.singleSourceUrl);
    state.singleSourceUrl = null;
  }
}

function previewSingleFile(file) {
  releaseSingleSourcePreview();
  if (!file) {
    dom.singleSourceImage.hidden = true;
    dom.singleSourcePlaceholder.hidden = false;
    dom.singleSourcePlaceholder.textContent = "选择图片";
    return;
  }
  state.singleSourceUrl = URL.createObjectURL(file);
  dom.singleSourceImage.src = state.singleSourceUrl;
  dom.singleSourceImage.hidden = false;
  dom.singleSourcePlaceholder.hidden = true;
}

function resetSingleView() {
  dom.singleFile.value = "";
  state.singleResult = null;
  releaseSingleSourcePreview();
  dom.singleSourceImage.hidden = true;
  dom.singleSourceImage.removeAttribute("src");
  dom.singleSourcePlaceholder.hidden = false;
  dom.singleSourcePlaceholder.textContent = "选择图片";
  dom.singleResultImage.hidden = true;
  dom.singleResultImage.removeAttribute("src");
  dom.singleResultPlaceholder.hidden = false;
  dom.singleResultPlaceholder.textContent = "等待结果";
  renderEmpty(dom.singleSummary, "等待检测");
  renderEmpty(dom.singleReport, "等待结果");
  renderEmpty(dom.singleDetections, "暂无检测目标");
  clearNotice(dom.singleNotice);
}

function renderSingleResult(result) {
  if (!result) {
    renderEmpty(dom.singleSummary, "等待检测");
    renderEmpty(dom.singleReport, "等待结果");
    renderEmpty(dom.singleDetections, "暂无检测目标");
    return;
  }
  dom.singleSummary.innerHTML = [
    createSummaryPill("文件", result.filename || "-"),
    createSummaryPill("模型", result.model_name || "-"),
    createSummaryPill("目标数", `${result.summary?.total_detections || 0}`),
    createStatusPill(result.report?.status || "no_detection"),
  ].join("");
  dom.singleReport.innerHTML = buildReportHtml(result.report, result.summary);
  dom.singleDetections.innerHTML = buildDetectionsTable(result.detections || []);

  if (result.artifact_url) {
    dom.singleResultImage.src = resolveUrl(result.artifact_url);
    dom.singleResultImage.hidden = false;
    dom.singleResultPlaceholder.hidden = true;
  } else {
    dom.singleResultImage.hidden = true;
    dom.singleResultImage.removeAttribute("src");
    dom.singleResultPlaceholder.hidden = false;
    dom.singleResultPlaceholder.textContent = "本次未保存标注图";
  }
}

async function runSinglePrediction() {
  const file = dom.singleFile.files?.[0];
  if (!file) {
    showNotice(dom.singleNotice, "请先选择一张图片。", "warn");
    return;
  }

  const formData = new FormData();
  formData.append("file", file);
  formData.append("imgsz", dom.singleImgsz.value || "416");
  formData.append("conf", dom.singleConf.value || "0.25");
  formData.append("save_artifact", "true");
  formData.append("record_history", "true");

  try {
    state.singleResult = await uploadForm(`${API_BASE}/inference/image`, formData, "单图检测", `正在上传 ${file.name}`);
    renderSingleResult(state.singleResult);
    await Promise.allSettled([loadHistory(true), loadStorage(true), loadDashboardSummary(true)]);
    showNotice(dom.singleNotice, "单图检测完成。", "ok");
  } catch (error) {
    showNotice(dom.singleNotice, error.message, "error");
  } finally {
    hideOverlay();
  }
}

function bindBatchControls() {
  dom.batchFiles.addEventListener("change", (event) => {
    mergeBatchFiles(Array.from(event.target.files || []));
    event.target.value = "";
  });

  dom.batchFolder.addEventListener("change", (event) => {
    mergeBatchFiles(Array.from(event.target.files || []));
    event.target.value = "";
  });

  dom.batchRunBtn.addEventListener("click", () => {
    void runBatchPrediction();
  });

  dom.batchResetBtn.addEventListener("click", resetBatchView);

  dom.batchDropZone.addEventListener("click", () => dom.batchFiles.click());
  dom.batchDropZone.addEventListener("dragover", (event) => {
    event.preventDefault();
    dom.batchDropZone.classList.add("is-dragover");
  });
  dom.batchDropZone.addEventListener("dragleave", () => {
    dom.batchDropZone.classList.remove("is-dragover");
  });
  dom.batchDropZone.addEventListener("drop", (event) => {
    event.preventDefault();
    dom.batchDropZone.classList.remove("is-dragover");
    mergeBatchFiles(Array.from(event.dataTransfer?.files || []));
  });
}

function mergeBatchFiles(files) {
  const existing = new Map(state.batchFiles.map((item) => [item.__key, item]));
  files
    .filter(isImageFile)
    .forEach((file) => {
      const key = `${file.webkitRelativePath || file.name}::${file.size}::${file.lastModified}`;
      if (!existing.has(key)) {
        file.__key = key;
        existing.set(key, file);
      }
    });
  state.batchFiles = Array.from(existing.values());
  renderBatchSelection();
  clearNotice(dom.batchNotice);
}

function removeBatchFile(key) {
  state.batchFiles = state.batchFiles.filter((item) => item.__key !== key);
  renderBatchSelection();
}

function renderBatchSelection() {
  if (!state.batchFiles.length) {
    renderEmpty(dom.batchSelection, "暂无待检测文件");
    return;
  }
  const rows = state.batchFiles
    .map(
      (file) => `
        <tr>
          <td>${escapeHtml(file.webkitRelativePath || file.name)}</td>
          <td>${formatSizeMb(file.size / 1024 / 1024)}</td>
          <td><button class="btn btn-ghost table-action-btn" type="button" data-batch-remove="${escapeHtml(file.__key)}">移除</button></td>
        </tr>
      `
    )
    .join("");
  dom.batchSelection.innerHTML = `
    <div class="summary-row">${createSummaryPill("文件数", `${state.batchFiles.length}`)}</div>
    <div class="table-wrap">
      <table class="data-table">
        <thead>
          <tr>
            <th>文件</th>
            <th>大小</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>${rows}</tbody>
      </table>
    </div>
  `;
}

function resetBatchView() {
  dom.batchFiles.value = "";
  dom.batchFolder.value = "";
  state.batchFiles = [];
  state.batchTask = null;
  renderBatchSelection();
  renderEmpty(dom.batchSummary, "等待任务");
  dom.batchLinks.innerHTML = "";
  renderEmpty(dom.batchResults, "等待批量检测");
  renderEmpty(dom.batchFailures, "暂无失败项");
  clearNotice(dom.batchNotice);
}

function renderBatchPayload(payload) {
  if (!payload) {
    renderEmpty(dom.batchSummary, "等待任务");
    dom.batchLinks.innerHTML = "";
    renderEmpty(dom.batchResults, "等待批量检测");
    renderEmpty(dom.batchFailures, "暂无失败项");
    return;
  }

  dom.batchSummary.innerHTML = [
    createSummaryPill("总文件", `${payload.total_files || 0}`),
    createSummaryPill("成功", `${payload.successful_files || 0}`),
    createSummaryPill("失败", `${payload.failed_files || 0}`),
    createSummaryPill("目标数", `${payload.total_detections || 0}`),
  ].join("");

  dom.batchLinks.innerHTML = [
    payload.csv_url ? `<a href="${escapeHtml(payload.csv_url)}" data-download-url="${escapeHtml(payload.csv_url)}" data-download-name="batch-report.csv">下载 CSV</a>` : "",
    payload.excel_url ? `<a href="${escapeHtml(payload.excel_url)}" data-download-url="${escapeHtml(payload.excel_url)}" data-download-name="batch-report.xlsx">下载 Excel</a>` : "",
  ].filter(Boolean).join("");

  const resultRows = (payload.results || [])
    .map((item) => `
      <tr>
        <td>${escapeHtml(item.filename)}</td>
        <td>${createStatusPill(item.report?.status || "no_detection")}</td>
        <td>${item.summary?.total_detections || 0}</td>
        <td>${formatPercent(item.report?.rotten_rate || 0)}</td>
        <td>${item.artifact_url ? `<a href="${escapeHtml(item.artifact_url)}" data-download-url="${escapeHtml(item.artifact_url)}" data-download-name="${escapeHtml(basenamePath(item.artifact_url))}">下载标注图</a>` : '<span class="table-muted">无</span>'}</td>
      </tr>
    `)
    .join("");
  dom.batchResults.innerHTML = resultRows
    ? `
      <div class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th>文件</th>
              <th>结果</th>
              <th>目标数</th>
              <th>腐烂占比</th>
              <th>标注图</th>
            </tr>
          </thead>
          <tbody>${resultRows}</tbody>
        </table>
      </div>
    `
    : '<div class="empty-state">没有成功结果</div>';

  const failureRows = (payload.failures || [])
    .map((item) => `<tr><td>${escapeHtml(item.filename)}</td><td>${escapeHtml(item.error)}</td></tr>`)
    .join("");
  dom.batchFailures.innerHTML = failureRows
    ? `
      <div class="table-wrap">
        <table class="data-table">
          <thead><tr><th>文件</th><th>原因</th></tr></thead>
          <tbody>${failureRows}</tbody>
        </table>
      </div>
    `
    : '<div class="empty-state">没有失败项</div>';
}

function renderBatchTask() {
  const task = state.batchTask;
  if (!task) {
    renderBatchPayload(null);
    return;
  }
  if (task.status === "queued" || task.status === "running") {
    dom.batchResults.innerHTML = buildTaskCard(task, "批量检测任务");
    return;
  }
  if (task.status === "failed") {
    dom.batchResults.innerHTML = `<div class="empty-state">${escapeHtml(task.error_message || "批量任务失败")}</div>`;
    return;
  }
  renderBatchPayload(task.result_payload || null);
}

async function runBatchPrediction() {
  if (!state.batchFiles.length) {
    showNotice(dom.batchNotice, "请先选择多张图片或一个图片文件夹。", "warn");
    return;
  }

  const formData = new FormData();
  state.batchFiles.forEach((file) => formData.append("files", file, file.webkitRelativePath || file.name));
  formData.append("imgsz", dom.batchImgsz.value || "416");
  formData.append("conf", dom.batchConf.value || "0.25");
  formData.append("save_artifact", "true");
  formData.append("export_csv", "true");
  formData.append("export_excel", "true");

  try {
    state.batchTask = await uploadForm(`${API_BASE}/tasks/batch-inference`, formData, "批量检测", `正在上传 ${state.batchFiles.length} 个文件`);
    renderBatchTask();
    const finished = await waitForTask(state.batchTask.id, {
      title: "批量检测",
      onUpdate: (task) => {
        state.batchTask = task;
        renderBatchTask();
      },
    });
    state.batchTask = finished;
    renderBatchTask();
    await Promise.allSettled([loadHistory(true), loadStorage(true), loadDashboardSummary(true)]);
    if (finished.result_payload?.history_run_id) {
      await loadHistoryDetail(finished.result_payload.history_run_id, true);
    }
    showNotice(dom.batchNotice, "批量检测完成。", "ok");
  } catch (error) {
    showNotice(dom.batchNotice, error.message, "error");
  } finally {
    hideOverlay();
  }
}

function bindWebcamControls() {
  dom.webcamStartBtn.addEventListener("click", () => {
    void startWebcam();
  });
  dom.webcamDetectBtn.addEventListener("click", () => {
    void detectWebcamFrame();
  });
  dom.webcamAutoBtn.addEventListener("click", () => {
    toggleWebcamAuto();
  });
  dom.webcamStopBtn.addEventListener("click", () => {
    stopWebcam(true);
  });
}

function updateWebcamButtons() {
  const started = Boolean(state.webcam.stream);
  dom.webcamDetectBtn.disabled = !started || state.webcam.busy;
  dom.webcamAutoBtn.disabled = !started;
  dom.webcamAutoBtn.textContent = state.webcam.autoRunning ? "停止自动检测" : "自动检测";
  dom.webcamStartBtn.disabled = started;
}

function resetWebcamView() {
  renderEmpty(dom.webcamMetrics, "等待摄像头启动");
  renderEmpty(dom.webcamReport, "等待结果");
  renderEmpty(dom.webcamDetections, "暂无检测目标");
  const canvas = dom.webcamOverlay;
  const context = canvas.getContext("2d");
  context.clearRect(0, 0, canvas.width, canvas.height);
  if (dom.webcamStageHint) {
    dom.webcamStageHint.textContent = "未启动";
  }
  updateWebcamButtons();
}

async function startWebcam() {
  if (state.webcam.stream) {
    return;
  }
  try {
    state.webcam.stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
    dom.webcamVideo.srcObject = state.webcam.stream;
    await dom.webcamVideo.play();
    await ensureWebcamSocket();
    if (dom.webcamStageHint) {
      dom.webcamStageHint.textContent = "摄像头已连接";
    }
    clearNotice(dom.webcamNotice);
  } catch (error) {
    showNotice(dom.webcamNotice, error.message || "摄像头启动失败。", "error");
  } finally {
    updateWebcamButtons();
  }
}

async function ensureWebcamSocket() {
  if (state.webcam.socket && state.webcam.socket.readyState === WebSocket.OPEN) {
    return state.webcam.socket;
  }
  if (state.webcam.connectPromise) {
    return state.webcam.connectPromise;
  }

  state.webcam.connectPromise = new Promise((resolve, reject) => {
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const socket = new WebSocket(`${protocol}//${window.location.host}/ws/webcam`);

    const cleanup = () => {
      socket.removeEventListener("open", handleOpen);
      socket.removeEventListener("message", handleMessage);
      socket.removeEventListener("error", handleError);
      socket.removeEventListener("close", handleClose);
    };

    const handleOpen = () => {
      state.webcam.socket = socket;
    };

    const handleMessage = (event) => {
      let payload = null;
      try {
        payload = JSON.parse(event.data);
      } catch {
        payload = null;
      }
      if (payload?.type === "ready") {
        cleanup();
        resolve(socket);
      }
    };

    const handleError = () => {
      cleanup();
      reject(buildError("摄像头通道连接失败。"));
    };

    const handleClose = () => {
      if (state.webcam.socket === socket) {
        state.webcam.socket = null;
      }
      cleanup();
      reject(buildError("摄像头通道已关闭。"));
    };

    socket.addEventListener("open", handleOpen);
    socket.addEventListener("message", handleMessage);
    socket.addEventListener("error", handleError);
    socket.addEventListener("close", handleClose);
  }).finally(() => {
    state.webcam.connectPromise = null;
  });

  return state.webcam.connectPromise;
}

function captureWebcamFrame() {
  const video = dom.webcamVideo;
  const canvas = state.webcam.captureCanvas;
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  const context = canvas.getContext("2d");
  context.drawImage(video, 0, 0, canvas.width, canvas.height);
  return canvas.toDataURL("image/jpeg", 0.85);
}

function waitForFrameResponse(socket, frameId) {
  return new Promise((resolve, reject) => {
    const timeoutId = window.setTimeout(() => {
      cleanup();
      reject(buildError("摄像头检测超时。"));
    }, 15000);

    const cleanup = () => {
      window.clearTimeout(timeoutId);
      socket.removeEventListener("message", handleMessage);
      socket.removeEventListener("close", handleClose);
      socket.removeEventListener("error", handleError);
    };

    const handleMessage = (event) => {
      let payload = null;
      try {
        payload = JSON.parse(event.data);
      } catch {
        payload = null;
      }
      if (!payload || payload.frame_id !== frameId) {
        return;
      }
      cleanup();
      if (payload.type === "error") {
        reject(buildError(payload.message || "摄像头检测失败", payload, 500));
        return;
      }
      resolve(payload);
    };

    const handleClose = () => {
      cleanup();
      reject(buildError("摄像头连接已断开。"));
    };

    const handleError = () => {
      cleanup();
      reject(buildError("摄像头连接出错。"));
    };

    socket.addEventListener("message", handleMessage);
    socket.addEventListener("close", handleClose);
    socket.addEventListener("error", handleError);
  });
}

function drawWebcamDetections(detections) {
  const video = dom.webcamVideo;
  const canvas = dom.webcamOverlay;
  const context = canvas.getContext("2d");
  canvas.width = video.clientWidth || video.videoWidth || 1;
  canvas.height = video.clientHeight || video.videoHeight || 1;
  context.clearRect(0, 0, canvas.width, canvas.height);
  if (!detections?.length || !video.videoWidth || !video.videoHeight) {
    return;
  }

  const scaleX = canvas.width / video.videoWidth;
  const scaleY = canvas.height / video.videoHeight;
  context.lineWidth = 2;
  context.font = "12px Segoe UI";

  detections.forEach((item, index) => {
    const color = ["#38bdf8", "#f59e0b", "#22c55e", "#ef4444"][index % 4];
    const bbox = item.bbox || {};
    const x = (bbox.x1 || 0) * scaleX;
    const y = (bbox.y1 || 0) * scaleY;
    const width = Math.max(((bbox.x2 || 0) - (bbox.x1 || 0)) * scaleX, 1);
    const height = Math.max(((bbox.y2 || 0) - (bbox.y1 || 0)) * scaleY, 1);
    const label = `${item.label} ${formatPercent(item.confidence || 0, 1)}`;

    context.strokeStyle = color;
    context.strokeRect(x, y, width, height);
    context.fillStyle = color;
    context.fillRect(x, Math.max(0, y - 22), Math.max(context.measureText(label).width + 16, 56), 20);
    context.fillStyle = "#ffffff";
    context.fillText(label, x + 8, Math.max(14, y - 8));
  });
}

function renderWebcamResult(result, latencyMs = null) {
  if (!result) {
    renderEmpty(dom.webcamMetrics, "等待摄像头启动");
    renderEmpty(dom.webcamReport, "等待结果");
    renderEmpty(dom.webcamDetections, "暂无检测目标");
    return;
  }
  dom.webcamMetrics.innerHTML = [
    createSummaryPill("延迟", `${formatNumber(latencyMs || 0, 2)} ms`),
    createSummaryPill("目标数", `${result.summary?.total_detections || 0}`),
    createSummaryPill("模型", result.model_name || "-"),
    createStatusPill(result.report?.status || "no_detection"),
  ].join("");
  dom.webcamReport.innerHTML = buildReportHtml(result.report, result.summary);
  dom.webcamDetections.innerHTML = buildDetectionsTable(result.detections || []);
  drawWebcamDetections(result.detections || []);
}

async function detectWebcamFrame() {
  if (!state.webcam.stream) {
    showNotice(dom.webcamNotice, "请先启动摄像头。", "warn");
    return;
  }
  if (state.webcam.busy) {
    return;
  }

  try {
    state.webcam.busy = true;
    updateWebcamButtons();
    const socket = await ensureWebcamSocket();
    const frameId = `frame-${++state.webcam.frameId}`;
    socket.send(JSON.stringify({
      type: "frame",
      frame_id: frameId,
      image_base64: captureWebcamFrame(),
      imgsz: Number(dom.webcamImgsz.value || 416),
      conf: Number(dom.webcamConf.value || 0.25),
    }));
    const payload = await waitForFrameResponse(socket, frameId);
    state.webcam.lastLatencyMs = payload.latency_ms || 0;
    renderWebcamResult(payload.data, payload.latency_ms || 0);
    clearNotice(dom.webcamNotice);
  } catch (error) {
    showNotice(dom.webcamNotice, error.message, "error");
  } finally {
    state.webcam.busy = false;
    updateWebcamButtons();
  }
}

function toggleWebcamAuto() {
  if (!state.webcam.stream) {
    showNotice(dom.webcamNotice, "请先启动摄像头。", "warn");
    return;
  }
  if (state.webcam.autoRunning) {
    window.clearInterval(state.webcam.autoTimer);
    state.webcam.autoTimer = null;
    state.webcam.autoRunning = false;
    if (dom.webcamStageHint) {
      dom.webcamStageHint.textContent = "自动检测已停止";
    }
    updateWebcamButtons();
    return;
  }
  state.webcam.autoRunning = true;
  state.webcam.autoTimer = window.setInterval(() => {
    if (!state.webcam.busy) {
      void detectWebcamFrame();
    }
  }, 900);
  if (dom.webcamStageHint) {
    dom.webcamStageHint.textContent = "自动检测中";
  }
  updateWebcamButtons();
}

function stopWebcam(notify = true) {
  if (state.webcam.autoTimer) {
    window.clearInterval(state.webcam.autoTimer);
    state.webcam.autoTimer = null;
  }
  state.webcam.autoRunning = false;
  state.webcam.busy = false;

  if (state.webcam.socket) {
    state.webcam.socket.close();
    state.webcam.socket = null;
  }
  if (state.webcam.stream) {
    state.webcam.stream.getTracks().forEach((track) => track.stop());
    state.webcam.stream = null;
  }
  dom.webcamVideo.srcObject = null;
  resetWebcamView();
  if (notify) {
    showNotice(dom.webcamNotice, "摄像头已停止。", "ok");
  }
}

function bindDeploymentControls() {
  dom.exportOnnxBtn.addEventListener("click", () => {
    void exportOnnx();
  });
  dom.exportTensorRtBtn.addEventListener("click", () => {
    void exportTensorRt();
  });
  dom.benchmarkRunBtn.addEventListener("click", () => {
    void runBenchmark();
  });
}

function renderDeploymentStatus() {
  const deployment = state.deployment;
  if (!deployment) {
    renderEmpty(dom.deploymentStatusCards, "部署状态未加载");
    return;
  }
  const providers = deployment.onnxruntime_providers?.length ? deployment.onnxruntime_providers.join(", ") : "未检测到";
  dom.deploymentStatusCards.innerHTML = [
    createSummaryPill("PyTorch", deployment.pytorch?.exists ? deployment.pytorch.name : "未就绪"),
    createSummaryPill("ONNX", deployment.onnx?.exists ? deployment.onnx.name : "未导出"),
    createSummaryPill("TensorRT", deployment.tensorrt?.exists ? deployment.tensorrt.name : "未导出"),
    createSummaryPill("依赖", deployment.onnx_dependencies_ready ? "已就绪" : "未就绪"),
    createSummaryPill("TRT 依赖", deployment.tensorrt_dependencies_ready ? "已就绪" : "未就绪"),
    createSummaryPill("Providers", providers),
  ].join("");
}

function renderBenchmarkPayload(payload) {
  if (!payload) {
    return '<div class="empty-state">等待结果</div>';
  }
  const engineRows = (payload.engines || [])
    .map((item) => `
      <tr>
        <td>${escapeHtml(item.engine)}</td>
        <td>${item.runs}</td>
        <td>${formatNumber(item.average_ms, 2)} ms</td>
        <td>${formatNumber(item.best_ms, 2)} ms</td>
        <td>${formatNumber(item.worst_ms, 2)} ms</td>
        <td>${item.total_detections || 0}</td>
      </tr>
    `)
    .join("");
  const capabilityHtml = (payload.capabilities || [])
    .map((item) => createSummaryPill(item.engine, item.available ? (item.implemented ? "可用" : "预留") : item.reason || "不可用"))
    .join("");
  const notesHtml = (payload.notes || []).map((item) => `<div class="result-mini"><strong>说明</strong><span>${escapeHtml(item)}</span></div>`).join("");

  return `
    <div class="summary-row">
      ${createSummaryPill("图片", payload.filename || "-")}
      ${createSummaryPill("imgsz", `${payload.image_size || 0}`)}
      ${createSummaryPill("conf", `${payload.confidence_threshold || 0}`)}
      ${payload.speedup_vs_pytorch ? createSummaryPill("相对 PyTorch", `${formatNumber(payload.speedup_vs_pytorch, 2)}x`) : ""}
      ${payload.tensorrt_speedup_vs_pytorch ? createSummaryPill("TensorRT 相对 PyTorch", `${formatNumber(payload.tensorrt_speedup_vs_pytorch, 2)}x`) : ""}
    </div>
    <div class="summary-row">${capabilityHtml}</div>
    <div class="table-wrap">
      <table class="data-table">
        <thead>
          <tr>
            <th>引擎</th>
            <th>Runs</th>
            <th>平均延迟</th>
            <th>最佳</th>
            <th>最差</th>
            <th>目标数</th>
          </tr>
        </thead>
        <tbody>${engineRows}</tbody>
      </table>
    </div>
    <div class="result-grid">${notesHtml || '<div class="empty-state">暂无额外说明</div>'}</div>
  `;
}

function renderDeploymentOutput() {
  if (state.benchmarkTask && (state.benchmarkTask.status === "queued" || state.benchmarkTask.status === "running")) {
    dom.deploymentOutput.innerHTML = buildTaskCard(state.benchmarkTask, "Benchmark 任务");
    return;
  }
  if (state.benchmarkTask?.status === "failed") {
    dom.deploymentOutput.innerHTML = `<div class="empty-state">${escapeHtml(state.benchmarkTask.error_message || "Benchmark 失败")}</div>`;
    return;
  }
  if (!state.deploymentOutput) {
    renderEmpty(dom.deploymentOutput, "等待结果");
    return;
  }
  if (state.deploymentOutput.kind === "export") {
    const payload = state.deploymentOutput.payload;
    dom.deploymentOutput.innerHTML = `
      <div class="result-grid">
        <div class="result-mini"><strong>状态</strong><span>${escapeHtml(payload.status || "-")}</span></div>
        <div class="result-mini"><strong>ONNX 文件</strong><span>${escapeHtml(payload.onnx?.name || "未生成")}</span></div>
        <div class="result-mini"><strong>导出 imgsz</strong><span>${payload.image_size || 0}</span></div>
        <div class="result-mini"><strong>说明</strong><span>${escapeHtml(payload.message || "-")}</span></div>
      </div>
    `;
    return;
  }
  if (state.deploymentOutput.kind === "tensorrt_export") {
    const payload = state.deploymentOutput.payload;
    dom.deploymentOutput.innerHTML = `
      <div class="result-grid">
        <div class="result-mini"><strong>状态</strong><span>${escapeHtml(payload.status || "-")}</span></div>
        <div class="result-mini"><strong>TensorRT 文件</strong><span>${escapeHtml(payload.tensorrt?.name || "未生成")}</span></div>
        <div class="result-mini"><strong>导出 imgsz</strong><span>${payload.image_size || 0}</span></div>
        <div class="result-mini"><strong>说明</strong><span>${escapeHtml(payload.message || "-")}</span></div>
      </div>
    `;
    return;
  }
  if (state.deploymentOutput.kind === "benchmark") {
    dom.deploymentOutput.innerHTML = renderBenchmarkPayload(state.deploymentOutput.payload);
    return;
  }
  renderEmpty(dom.deploymentOutput, "等待结果");
}

async function exportOnnx() {
  try {
    showOverlay("导出 ONNX", "正在导出当前启用模型...");
    const formData = new FormData();
    formData.append("imgsz", dom.exportImgsz.value || "416");
    const payload = await apiRequest(`${API_BASE}/deployment/onnx/export`, { method: "POST", body: formData });
    state.deploymentOutput = { kind: "export", payload };
    renderDeploymentOutput();
    await loadDeployment(true);
    showNotice(dom.deploymentNotice, "ONNX 导出完成。", "ok");
  } catch (error) {
    showNotice(dom.deploymentNotice, error.message, "error");
  } finally {
    hideOverlay();
  }
}

async function runBenchmark() {
  const file = dom.benchmarkFile.files?.[0];
  if (!file) {
    showNotice(dom.deploymentNotice, "请先选择一张 Benchmark 图片。", "warn");
    return;
  }

  const formData = new FormData();
  formData.append("file", file);
  formData.append("imgsz", dom.benchmarkImgsz.value || "416");
  formData.append("conf", dom.benchmarkConf.value || "0.25");
  formData.append("runs", dom.benchmarkRuns.value || "3");

  try {
    state.benchmarkTask = await uploadForm(`${API_BASE}/tasks/benchmark`, formData, "Benchmark", `正在上传 ${file.name}`);
    renderDeploymentOutput();
    const finished = await waitForTask(state.benchmarkTask.id, {
      title: "Benchmark",
      onUpdate: (task) => {
        state.benchmarkTask = task;
        renderDeploymentOutput();
      },
    });
    state.benchmarkTask = finished;
    state.deploymentOutput = { kind: "benchmark", payload: finished.result_payload || null };
    await loadModels(true);
    renderDeploymentOutput();
    showNotice(dom.deploymentNotice, "Benchmark 完成。", "ok");
  } catch (error) {
    showNotice(dom.deploymentNotice, error.message, "error");
  } finally {
    hideOverlay();
  }
}

function bindSettingsControls() {
  dom.refreshQualityRulesBtn.addEventListener("click", () => {
    void loadQualityRules(false);
  });
  dom.saveQualityRulesBtn.addEventListener("click", () => {
    void saveQualityRules();
  });
  dom.resetQualityRulesBtn.addEventListener("click", renderQualityRules);
}

function renderQualityRules() {
  const rules = state.qualityRules;
  if (!rules) {
    renderEmpty(dom.qualityRulesSummary, "规则未加载");
    return;
  }
  dom.qualityRulesEnabled.checked = Boolean(rules.enabled);
  dom.passMaxRottenRate.value = String(rules.pass_max_rotten_rate ?? 0);
  dom.warningMaxRottenRate.value = String(rules.warning_max_rotten_rate ?? 0.5);
  dom.freshKeywordsInput.value = (rules.fresh_keywords || []).join(", ");
  dom.rottenKeywordsInput.value = (rules.rotten_keywords || []).join(", ");
  dom.qualityNoDetectionMessage.value = rules.messages?.no_detection || "";
  dom.qualityDetectedOnlyMessage.value = rules.messages?.detected_only || "";
  dom.qualityPassMessage.value = rules.messages?.pass_message || "";
  dom.qualityWarningMessage.value = rules.messages?.warning_message || "";
  dom.qualityCriticalMessage.value = rules.messages?.critical_message || "";
  dom.qualityRulesSummary.innerHTML = [
    createSummaryPill("启用状态", rules.enabled ? "开启" : "关闭"),
    createSummaryPill("Pass 上限", formatPercent(rules.pass_max_rotten_rate || 0)),
    createSummaryPill("Warning 上限", formatPercent(rules.warning_max_rotten_rate || 0)),
    createSummaryPill("新鲜关键词", `${rules.fresh_keywords?.length || 0}`),
    createSummaryPill("腐烂关键词", `${rules.rotten_keywords?.length || 0}`),
  ].join("");
}

async function saveQualityRules() {
  const passRate = Number(dom.passMaxRottenRate.value || 0);
  const warningRate = Number(dom.warningMaxRottenRate.value || 0.5);
  if (passRate > warningRate) {
    showNotice(dom.settingsNotice, "Pass 阈值不能大于 Warning 阈值。", "warn");
    return;
  }

  const payload = {
    enabled: dom.qualityRulesEnabled.checked,
    fresh_keywords: parseKeywordList(dom.freshKeywordsInput.value),
    rotten_keywords: parseKeywordList(dom.rottenKeywordsInput.value),
    pass_max_rotten_rate: passRate,
    warning_max_rotten_rate: warningRate,
    messages: {
      no_detection: dom.qualityNoDetectionMessage.value.trim(),
      detected_only: dom.qualityDetectedOnlyMessage.value.trim(),
      pass_message: dom.qualityPassMessage.value.trim(),
      warning_message: dom.qualityWarningMessage.value.trim(),
      critical_message: dom.qualityCriticalMessage.value.trim(),
    },
  };

  try {
    showOverlay("保存规则", "正在更新质检规则...");
    state.qualityRules = await apiPutJson(`${API_BASE}/settings/quality-rules`, payload);
    renderQualityRules();
    showNotice(dom.settingsNotice, "规则已保存。", "ok");
  } catch (error) {
    showNotice(dom.settingsNotice, error.message, "error");
  } finally {
    hideOverlay();
  }
}

function bindReviewControls() {
  dom.refreshReviewBtn.addEventListener("click", () => {
    void Promise.all([loadReviewSummary(false), loadReviewItems(false), loadFeedbackPoolSummary(true)]);
  });
  dom.exportReviewQueueBtn.addEventListener("click", () => {
    void exportReviewQueueCsv();
  });
  if (dom.reviewKeywordInput) {
    dom.reviewKeywordInput.addEventListener("input", () => {
      state.reviewKeyword = dom.reviewKeywordInput.value.trim();
      if (state.reviewQueue !== "feedback") {
        return;
      }
      if (state.reviewKeywordTimer) {
        window.clearTimeout(state.reviewKeywordTimer);
      }
      state.reviewKeywordTimer = window.setTimeout(() => {
        state.selectedReviewItemId = null;
        state.reviewDetail = null;
        void Promise.all([loadReviewItems(false), loadFeedbackPoolSummary(true)]);
      }, 240);
    });
  }

  $$("[data-review-queue]").forEach((button) => {
    button.addEventListener("click", () => {
      const queue = button.dataset.reviewQueue || "focus";
      if (queue === state.reviewQueue) {
        return;
      }
      state.reviewQueue = queue;
      state.selectedReviewItemId = null;
      state.reviewDetail = null;
      updateReviewQueueButtons();
      renderFeedbackPoolSummary();
      void Promise.all([loadReviewItems(false), loadFeedbackPoolSummary(true)]);
    });
  });

  $$("[data-review-decision]").forEach((button) => {
    button.addEventListener("click", () => {
      const decision = button.dataset.reviewDecision || "all";
      if (decision === state.reviewDecisionFilter) {
        return;
      }
      state.reviewDecisionFilter = decision;
      state.selectedReviewItemId = null;
      state.reviewDetail = null;
      updateReviewDecisionButtons();
      void Promise.all([loadReviewItems(false), loadFeedbackPoolSummary(true)]);
    });
  });

  $$("[data-review-mode]").forEach((button) => {
    button.addEventListener("click", () => {
      const mode = button.dataset.reviewMode || "all";
      if (mode === state.reviewModeFilter) {
        return;
      }
      state.reviewModeFilter = mode;
      state.selectedReviewItemId = null;
      state.reviewDetail = null;
      updateReviewModeButtons();
      if (state.reviewQueue !== "feedback") {
        return;
      }
      void Promise.all([loadReviewItems(false), loadFeedbackPoolSummary(true)]);
    });
  });
}

function bindRetrainControls() {
  dom.refreshRetrainBtn.addEventListener("click", () => {
    void Promise.all([
      loadRetrainSummary(false),
      loadRetrainBatchSummary(true),
      loadRetrainBatches(true),
      loadRetrainItems(false),
      state.selectedRetrainBatchId ? loadRetrainBatchDetail(state.selectedRetrainBatchId, true) : Promise.resolve(),
      state.selectedRetrainItemId ? loadRetrainDetail(state.selectedRetrainItemId, true) : Promise.resolve(),
    ]);
  });

  if (dom.createRetrainBatchBtn) {
    dom.createRetrainBatchBtn.addEventListener("click", () => {
      void createRetrainBatch();
    });
  }

  if (dom.clearRetrainSelectionBtn) {
    dom.clearRetrainSelectionBtn.addEventListener("click", () => {
      state.selectedRetrainCatalogIds = new Set();
      renderRetrainList();
      renderRetrainSelectionHint();
      if (dom.retrainBatchNotesInput && !state.selectedRetrainBatchId) {
        dom.retrainBatchNotesInput.value = "";
      }
    });
  }

  if (dom.retrainList) {
    dom.retrainList.addEventListener("change", (event) => {
      const target = event.target.closest("[data-retrain-select-id]");
      if (!target) {
        return;
      }
      const itemId = Number(target.dataset.retrainSelectId);
      if (!itemId) {
        return;
      }
      if (target.checked) {
        state.selectedRetrainCatalogIds.add(itemId);
      } else {
        state.selectedRetrainCatalogIds.delete(itemId);
      }
      renderRetrainList();
      renderRetrainSelectionHint();
    });
  }

  if (dom.retrainDetail) {
    dom.retrainDetail.addEventListener("input", (event) => {
      if (event.target.id === "retrainAnnotationInput") {
        renderRetrainAnnotationComposer();
      }
    });

    dom.retrainDetail.addEventListener("click", (event) => {
      const removeTarget = event.target.closest("[data-retrain-draft-remove]");
      if (removeTarget) {
        event.preventDefault();
        removeRetrainDraftLine(Number(removeTarget.dataset.retrainDraftRemove));
        return;
      }

      const toolTarget = event.target.closest("[data-retrain-draft-tool]");
      if (toolTarget) {
        event.preventDefault();
        handleRetrainDraftTool(toolTarget.dataset.retrainDraftTool || "");
        return;
      }

      const stageTarget = event.target.closest("[data-retrain-stage]");
      if (stageTarget) {
        event.preventDefault();
        handleRetrainStageClick(stageTarget, event);
      }
    });
  }

  if (dom.retrainKeywordInput) {
    dom.retrainKeywordInput.addEventListener("input", () => {
      state.retrainKeyword = dom.retrainKeywordInput.value.trim();
      if (state.retrainKeywordTimer) {
        window.clearTimeout(state.retrainKeywordTimer);
      }
      state.retrainKeywordTimer = window.setTimeout(() => {
        state.selectedRetrainItemId = null;
        state.retrainDetail = null;
        void Promise.all([loadRetrainSummary(true), loadRetrainItems(false)]);
      }, 240);
    });
  }

  $$("[data-retrain-status]").forEach((button) => {
    button.addEventListener("click", () => {
      const status = button.dataset.retrainStatus || "all";
      if (status === state.retrainStatusFilter) {
        return;
      }
      state.retrainStatusFilter = status;
      state.selectedRetrainItemId = null;
      state.retrainDetail = null;
      updateRetrainFilterButtons();
      void Promise.all([loadRetrainSummary(true), loadRetrainItems(false)]);
    });
  });

  $$("[data-retrain-decision]").forEach((button) => {
    button.addEventListener("click", () => {
      const decision = button.dataset.retrainDecision || "all";
      if (decision === state.retrainDecisionFilter) {
        return;
      }
      state.retrainDecisionFilter = decision;
      state.selectedRetrainItemId = null;
      state.retrainDetail = null;
      updateRetrainFilterButtons();
      void Promise.all([loadRetrainSummary(true), loadRetrainItems(false)]);
    });
  });

  $$("[data-retrain-mode]").forEach((button) => {
    button.addEventListener("click", () => {
      const mode = button.dataset.retrainMode || "all";
      if (mode === state.retrainModeFilter) {
        return;
      }
      state.retrainModeFilter = mode;
      state.selectedRetrainItemId = null;
      state.retrainDetail = null;
      updateRetrainFilterButtons();
      void Promise.all([loadRetrainSummary(true), loadRetrainItems(false)]);
    });
  });
}

async function exportReviewQueueCsv() {
  if (state.reviewQueue === "feedback") {
    try {
      showOverlay("导出回流清单", "正在生成回流样本清单...");
      const params = new URLSearchParams();
      if (state.reviewDecisionFilter && state.reviewDecisionFilter !== "all") {
        params.set("decision", state.reviewDecisionFilter);
      }
      if (state.reviewModeFilter && state.reviewModeFilter !== "all") {
        params.set("mode", state.reviewModeFilter);
      }
      if (state.reviewKeyword.trim()) {
        params.set("keyword", state.reviewKeyword.trim());
      }
      const suffix = params.toString() ? `?${params.toString()}` : "";
      const result = await apiPostJson(`${API_BASE}/review/feedback/export${suffix}`, {});
      await downloadBlob(result.export_url, result.export_name);
      showNotice(dom.reviewNotice, result.message || "回流清单已导出。", "ok");
    } catch (error) {
      showNotice(dom.reviewNotice, error.message, "error");
    } finally {
      hideOverlay();
    }
    return;
  }

  if (!state.reviewItems.length) {
    showNotice(dom.reviewNotice, "当前队列没有可导出的样本。", "warn");
    return;
  }

  const header = ["item_id", "run_id", "mode", "created_at", "filename", "status", "review_status", "review_decision", "feedback_status", "total_detections", "rotten_rate", "recommendation"];
  const lines = [
    header.join(","),
    ...state.reviewItems.map((item) => [
      item.item_id,
      item.run_id,
      csvCell(item.mode),
      csvCell(item.created_at),
      csvCell(item.filename),
      csvCell(item.status),
      csvCell(item.review_status),
      csvCell(item.review_decision || ""),
      csvCell(item.feedback_status || "none"),
      item.total_detections || 0,
      item.rotten_rate || 0,
      csvCell(item.recommendation || item.error || ""),
    ].join(",")),
  ];

  const blob = new Blob([`\uFEFF${lines.join("\n")}`], { type: "text/csv;charset=utf-8;" });
  const objectUrl = URL.createObjectURL(blob);
  const fileName = `review-queue-${state.reviewQueue}-${Date.now()}.csv`;
  const anchor = document.createElement("a");
  anchor.href = objectUrl;
  anchor.download = fileName;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(objectUrl);
  showNotice(dom.reviewNotice, "当前队列已导出。", "ok");
}

function updateReviewQueueButtons() {
  $$("[data-review-queue]").forEach((button) => {
    button.classList.toggle("is-active", (button.dataset.reviewQueue || "focus") === state.reviewQueue);
  });
  if (dom.exportReviewQueueBtn) {
    dom.exportReviewQueueBtn.textContent = state.reviewQueue === "feedback" ? "导出回流清单" : "导出当前队列";
  }
}

function updateReviewDecisionButtons() {
  $$("[data-review-decision]").forEach((button) => {
    button.classList.toggle("is-active", (button.dataset.reviewDecision || "all") === state.reviewDecisionFilter);
  });
}

function updateReviewModeButtons() {
  $$("[data-review-mode]").forEach((button) => {
    button.classList.toggle("is-active", (button.dataset.reviewMode || "all") === state.reviewModeFilter);
  });
  if (dom.reviewKeywordInput && dom.reviewKeywordInput.value !== state.reviewKeyword) {
    dom.reviewKeywordInput.value = state.reviewKeyword;
  }
}

function updateRetrainFilterButtons() {
  $$("[data-retrain-status]").forEach((button) => {
    button.classList.toggle("is-active", (button.dataset.retrainStatus || "all") === state.retrainStatusFilter);
  });
  $$("[data-retrain-decision]").forEach((button) => {
    button.classList.toggle("is-active", (button.dataset.retrainDecision || "all") === state.retrainDecisionFilter);
  });
  $$("[data-retrain-mode]").forEach((button) => {
    button.classList.toggle("is-active", (button.dataset.retrainMode || "all") === state.retrainModeFilter);
  });
  if (dom.retrainKeywordInput && dom.retrainKeywordInput.value !== state.retrainKeyword) {
    dom.retrainKeywordInput.value = state.retrainKeyword;
  }
}

function renderReviewSummary() {
  const summary = state.reviewSummary;
  if (!summary) {
    renderEmpty(dom.reviewSummary, "复核数据未加载");
    return;
  }
  dom.reviewSummary.innerHTML = [
    createSummaryPill("总样本", `${summary.total || 0}`),
    createSummaryPill("待复核", `${summary.pending || 0}`),
    createSummaryPill("已复核", `${summary.reviewed || 0}`),
    createSummaryPill("回流中", `${summary.feedback || 0}`),
    createSummaryPill("误检", `${summary.false_positive_count || 0}`),
    createSummaryPill("漏检", `${summary.missed_detection_count || 0}`),
    createSummaryPill("通用回流", `${summary.needs_feedback_count || 0}`),
  ].join("");
}

function renderFeedbackPoolSummary() {
  const isVisible = state.reviewQueue === "feedback";
  dom.feedbackPoolPanel.hidden = !isVisible;
  if (!isVisible) {
    return;
  }

  const summary = state.feedbackPoolSummary;
  if (!summary) {
    renderEmpty(dom.feedbackPoolSummary, "回流池数据未加载");
    return;
  }

  dom.feedbackPoolSummary.innerHTML = [
    createSummaryPill("回流样本", `${summary.total || 0}`),
    createSummaryPill("误检回流", `${summary.false_positive_count || 0}`),
    createSummaryPill("漏检回流", `${summary.missed_detection_count || 0}`),
    createSummaryPill("通用回流", `${summary.needs_feedback_count || 0}`),
    createSummaryPill("单图", `${summary.single_count || 0}`),
    createSummaryPill("批量", `${summary.batch_count || 0}`),
    createSummaryPill("摄像头", `${summary.webcam_count || 0}`),
    createSummaryPill("标注图可用", `${summary.artifact_ready_count || 0}`),
    createSummaryPill("平均腐烂占比", formatPercent(summary.avg_rotten_rate || 0)),
    createSummaryPill("最近更新", formatDateTime(summary.latest_updated_at) || "-"),
  ].join("");
}

function renderReviewList() {
  if (!state.reviewItems.length) {
    renderEmpty(dom.reviewList, state.reviewQueue === "feedback" ? "当前筛选条件下暂无回流样本" : "当前筛选条件下暂无复核样本");
    return;
  }

  const rows = state.reviewItems
    .map(
      (item) => `
        <tr class="${item.item_id === state.selectedReviewItemId ? "is-active-row" : ""}">
          <td><button class="table-link-button" type="button" data-review-item-id="${item.item_id}">#${item.item_id}</button></td>
          <td>${escapeHtml(item.filename)}</td>
          <td>${escapeHtml(formatMode(item.mode))}</td>
          <td>${createStatusPill(item.status)}</td>
          <td>${createReviewStatusPill(item.review_status)}</td>
          <td>${escapeHtml(formatReviewDecision(item.review_decision))}</td>
          <td>${escapeHtml(formatDateTime(item.created_at))}</td>
        </tr>
      `
    )
    .join("");

  dom.reviewList.innerHTML = `
    <div class="table-wrap">
      <table class="data-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>文件</th>
            <th>来源</th>
            <th>质检结果</th>
            <th>复核状态</th>
            <th>动作</th>
            <th>时间</th>
          </tr>
        </thead>
        <tbody>${rows}</tbody>
      </table>
    </div>
  `;
}

function renderReviewDetail() {
  const detail = state.reviewDetail;
  if (!detail) {
    renderEmpty(dom.reviewDetail, "选择样本查看");
    return;
  }
  const feedbackActionLabel = detail.feedback_status === "queued" ? "保留回流" : "加入回流";
  const canPromoteRetrain = detail.feedback_status === "queued" || Boolean(detail.retrain_status);
  const retrainActionLabel = detail.retrain_status ? "更新复训目录" : "加入复训目录";

  const links = [
    detail.artifact_url
      ? `<a href="${escapeHtml(detail.artifact_url)}" data-download-url="${escapeHtml(detail.artifact_url)}" data-download-name="${escapeHtml(basenamePath(detail.artifact_url))}">下载标注图</a>`
      : "",
    `<a href="#history" data-history-id="${detail.run_id}">查看所属记录</a>`,
    detail.retrain_status ? `<a href="#retrain" data-retrain-item-id="${detail.item_id}">查看复训目录</a>` : "",
  ].filter(Boolean).join("");

  dom.reviewDetail.innerHTML = `
    <div class="summary-row">
      ${createSummaryPill("样本", `#${detail.item_id}`)}
      ${createSummaryPill("记录", `#${detail.run_id}`)}
      ${createSummaryPill("模式", formatMode(detail.mode))}
      ${createSummaryPill("来源模型", detail.source_model_name || "未知")}
      ${createSummaryPill("目标数", `${detail.total_detections || 0}`)}
      ${createSummaryPill("腐烂占比", formatPercent(detail.rotten_rate || 0))}
    </div>
    <div class="inline-links">${links}</div>
    ${detail.artifact_url ? `
      <div class="review-preview">
        <img class="review-preview-image" src="${escapeHtml(detail.artifact_url)}" alt="${escapeHtml(detail.filename)}">
      </div>
    ` : ""}
    <div class="review-detail-grid">
      <div class="result-box">
        <div class="review-detail-head">
          <strong>${escapeHtml(detail.filename)}</strong>
          ${createStatusPill(detail.status)}
          ${createReviewStatusPill(detail.review_status)}
        </div>
        <p class="helper-note">${escapeHtml(detail.recommendation || detail.error || "暂无模型结论。")}</p>
        <div class="summary-row">
          ${createSummaryPill("当前动作", formatReviewDecision(detail.review_decision))}
          ${createSummaryPill("反馈状态", detail.feedback_status === "queued" ? "待回流" : "未回流")}
          ${createSummaryPill("复训状态", detail.retrain_status ? formatRetrainStatus(detail.retrain_status) : "未入目录")}
          ${createSummaryPill("更新时间", formatDateTime(detail.review_updated_at))}
        </div>
      </div>
      <div class="field-stack review-action-panel">
        <label class="field">
          <span>复核备注</span>
          <textarea id="reviewNotesInput" rows="4" placeholder="例如：误检由阴影导致，建议补充同类样本。">${escapeHtml(detail.review_notes || "")}</textarea>
        </label>
        <div class="action-row review-action-row">
          <button class="btn btn-primary" type="button" data-review-action="confirm">确认结果</button>
          <button class="btn btn-secondary" type="button" data-review-action="false_positive">标记误检</button>
          <button class="btn btn-secondary" type="button" data-review-action="missed_detection">标记漏检</button>
          <button class="btn btn-ghost" type="button" data-review-action="feedback">${feedbackActionLabel}</button>
          ${canPromoteRetrain ? `<button class="btn btn-secondary" type="button" data-review-action="promote_retrain">${retrainActionLabel}</button>` : ""}
        </div>
        ${canPromoteRetrain ? '<div class="helper-note">复训目录用于沉淀已经确认要回流的样本，便于后续整理成可复训数据集。</div>' : ""}
      </div>
    </div>
  `;
}

function buildDefaultRetrainBatchName() {
  const now = new Date();
  const parts = [
    now.getFullYear(),
    String(now.getMonth() + 1).padStart(2, "0"),
    String(now.getDate()).padStart(2, "0"),
    String(now.getHours()).padStart(2, "0"),
    String(now.getMinutes()).padStart(2, "0"),
  ];
  return `fresh-sort-batch-${parts.join("")}`;
}

function isRetrainBatchSelectable(item) {
  return item && item.catalog_status === "ready" && !item.batch_id;
}

function renderRetrainSummary() {
  const summary = state.retrainSummary;
  if (!summary) {
    renderEmpty(dom.retrainSummary, "复训目录数据未加载");
    return;
  }
  dom.retrainSummary.innerHTML = [
    createSummaryPill("目录样本", `${summary.total || 0}`),
    createSummaryPill("待处理", `${summary.pending || 0}`),
    createSummaryPill("待复训", `${summary.ready || 0}`),
    createSummaryPill("已入训练", `${summary.used || 0}`),
    createSummaryPill("误检来源", `${summary.false_positive_count || 0}`),
    createSummaryPill("漏检来源", `${summary.missed_detection_count || 0}`),
    createSummaryPill("通用回流", `${summary.needs_feedback_count || 0}`),
    createSummaryPill("最近更新", formatDateTime(summary.latest_updated_at) || "-"),
  ].join("");
}

function renderRetrainBatchSummary() {
  const summary = state.retrainBatchSummary;
  if (!summary) {
    renderEmpty(dom.retrainBatchSummary, "训练批次数据未加载");
    return;
  }
  dom.retrainBatchSummary.innerHTML = [
    createSummaryPill("训练批次", `${summary.total || 0}`),
    createSummaryPill("待导出", `${summary.draft || 0}`),
    createSummaryPill("已导出", `${summary.exported || 0}`),
    createSummaryPill("覆盖样本", `${summary.total_items || 0}`),
    createSummaryPill("最近导出", formatDateTime(summary.latest_exported_at) || "-"),
  ].join("");
}

function renderRetrainSelectionHint() {
  if (!dom.retrainSelectionHint) {
    return;
  }

  const selectedItems = state.retrainItems.filter((item) => state.selectedRetrainCatalogIds.has(item.item_id));
  const selectedCount = selectedItems.length;
  const readyCount = state.retrainItems.filter((item) => isRetrainBatchSelectable(item)).length;

  if (dom.retrainBatchNameInput) {
    dom.retrainBatchNameInput.placeholder = buildDefaultRetrainBatchName();
  }

  if (selectedCount) {
    const filenames = selectedItems.slice(0, 3).map((item) => item.filename).join("、");
    const moreText = selectedCount > 3 ? ` 等 ${selectedCount} 个样本` : "";
    dom.retrainSelectionHint.textContent = `当前已勾选 ${selectedCount} 个待复训样本，创建批次后可在右侧导出标准样本包。${filenames ? ` 已选：${filenames}${moreText}` : ""}`;
    return;
  }

  if (readyCount) {
    dom.retrainSelectionHint.textContent = `当前筛选结果里有 ${readyCount} 个“待复训”且未分配批次的样本，可以直接勾选后创建训练批次。`;
    return;
  }

  dom.retrainSelectionHint.textContent = "当前没有可加入训练批次的样本。请先把目录状态推进到“待复训”，或调整筛选条件。";
}

function renderRetrainBatchList() {
  if (!state.retrainBatches.length) {
    renderEmpty(dom.retrainBatchList, "暂无训练批次");
    return;
  }

  dom.retrainBatchList.innerHTML = state.retrainBatches
    .map(
      (item) => `
        <article class="history-item ${item.batch_id === state.selectedRetrainBatchId ? "is-active" : ""}">
          <button type="button" data-retrain-batch-id="${item.batch_id}">
            <strong>${escapeHtml(item.batch_name)}</strong>
            <small>${escapeHtml(formatDateTime(item.updated_at))} · ${item.item_count || 0} 个样本 · ${escapeHtml(formatRetrainBatchStatus(item.batch_status))}</small>
          </button>
        </article>
      `
    )
    .join("");
}

function renderRetrainBatchDetail() {
  const detail = state.retrainBatchDetail;
  if (!detail) {
    renderEmpty(dom.retrainBatchDetail, "选择批次查看详情，或先从下方目录勾选样本创建训练批次");
    return;
  }

  const batchSummary = summarizeRetrainBatchItems(detail.items || []);
  const hasPendingAnnotation = batchSummary.pendingAnnotation > 0;

  const links = [
    detail.export_url
      ? `<a href="${escapeHtml(detail.export_url)}" data-download-url="${escapeHtml(detail.export_url)}" data-download-name="${escapeHtml(detail.export_name || basenamePath(detail.export_url))}">下载样本包</a>`
      : "",
  ].filter(Boolean).join("");

  const rows = (detail.items || [])
    .map(
      (item) => `
        <tr>
          <td><button class="table-link-button" type="button" data-retrain-item-id="${item.item_id}">#${item.item_id}</button></td>
          <td>${escapeHtml(item.filename)}</td>
          <td>${escapeHtml(formatMode(item.mode))}</td>
          <td>${escapeHtml(formatReviewDecision(item.review_decision))}</td>
          <td>${createRetrainStatusPill(item.catalog_status)}</td>
          <td>${createAnnotationStatusPill(item.annotation_status)}</td>
          <td>${escapeHtml(formatRetrainExportAdvice(item))}</td>
        </tr>
      `
    )
    .join("");

  dom.retrainBatchDetail.innerHTML = `
    <div class="summary-row">
      ${createSummaryPill("批次", detail.batch_name)}
      ${createSummaryPill("样本数", `${detail.item_count || 0}`)}
      ${createSummaryPill("可直接训练", `${batchSummary.readyToTrain}`)}
      ${createSummaryPill("待补标", `${batchSummary.pendingAnnotation}`)}
      ${createSummaryPill("创建时间", formatDateTime(detail.created_at))}
      ${createSummaryPill("最近更新", formatDateTime(detail.updated_at))}
      ${createSummaryPill("最近导出", formatDateTime(detail.exported_at) || "-")}
    </div>
    <div class="inline-links">${links}</div>
    <div class="review-detail-grid">
      <div class="result-box">
        <div class="review-detail-head">
          <strong>${escapeHtml(detail.batch_name)}</strong>
          ${createRetrainBatchStatusPill(detail.batch_status)}
        </div>
        <p class="helper-note">${escapeHtml(detail.batch_notes || "该批次用于沉淀可进入下一轮训练的数据样本，目前支持导出标准样本包。")}</p>
        <div class="summary-row">
          ${createSummaryPill("草稿标签", `${batchSummary.readyLabeled}`)}
          ${createSummaryPill("空标签负样本", `${batchSummary.readyEmpty}`)}
          ${createSummaryPill("导出任务清单", `${batchSummary.pendingAnnotation}`)}
        </div>
        <div class="helper-note ${hasPendingAnnotation ? "is-warning" : ""}">
          ${
            hasPendingAnnotation
              ? `当前仍有 ${batchSummary.pendingAnnotation} 个样本未补标。导出后这些样本会进入 annotation_tasks.csv，建议先进入复训详情补齐草稿。`
              : "当前批次样本都已具备直接训练条件，导出后 labels/ 目录即可直接用于后续训练流程。"
          }
        </div>
        ${
          hasPendingAnnotation
            ? `
              <div class="batch-checklist">
                ${batchSummary.pendingItems
                  .map(
                    (item) => `
                      <button class="batch-check-item" type="button" data-retrain-item-id="${item.item_id}">
                        <strong>#${item.item_id} · ${escapeHtml(item.filename)}</strong>
                        <span>${escapeHtml(formatReviewDecision(item.review_decision))} · 需先补标</span>
                      </button>
                    `,
                  )
                  .join("")}
              </div>
            `
            : ""
        }
        <div class="action-row review-action-row">
          <button class="btn btn-primary" type="button" data-retrain-batch-action="export">${detail.export_url ? "重新导出样本包" : hasPendingAnnotation ? "导出样本包（含待补标任务）" : "导出样本包并标记已入训练"}</button>
        </div>
      </div>
      <div class="result-box result-scroll result-scroll-lg">
        <div class="table-wrap">
          <table class="data-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>文件</th>
                <th>模式</th>
                <th>回流原因</th>
                <th>目录状态</th>
                <th>标签状态</th>
                <th>导出建议</th>
              </tr>
            </thead>
            <tbody>${rows}</tbody>
          </table>
        </div>
      </div>
    </div>
  `;
}

function renderRetrainList() {
  if (!state.retrainItems.length) {
    renderEmpty(dom.retrainList, "当前筛选条件下暂无复训样本");
    return;
  }

  const rows = state.retrainItems
    .map(
      (item) => `
        <tr class="${item.item_id === state.selectedRetrainItemId ? "is-active-row" : ""}">
          <td class="check-cell">
            <input
              type="checkbox"
              data-retrain-select-id="${item.item_id}"
              ${state.selectedRetrainCatalogIds.has(item.item_id) ? "checked" : ""}
              ${isRetrainBatchSelectable(item) ? "" : "disabled"}
              aria-label="select retrain item ${item.item_id}"
            >
          </td>
          <td><button class="table-link-button" type="button" data-retrain-item-id="${item.item_id}">#${item.item_id}</button></td>
          <td>${escapeHtml(item.filename)}</td>
          <td>${escapeHtml(formatMode(item.mode))}</td>
          <td>${escapeHtml(formatReviewDecision(item.review_decision))}</td>
          <td>${createRetrainStatusPill(item.catalog_status)}</td>
          <td>${escapeHtml(formatDateTime(item.catalog_updated_at))}</td>
          <td>${item.batch_name ? escapeHtml(item.batch_name) : '<span class="table-muted">未分配</span>'}</td>
        </tr>
      `
    )
    .join("");

  dom.retrainList.innerHTML = `
    <div class="table-wrap">
      <table class="data-table">
        <thead>
          <tr>
            <th class="check-cell">选中</th>
            <th>ID</th>
            <th>文件</th>
            <th>来源</th>
            <th>回流原因</th>
            <th>目录状态</th>
            <th>更新时间</th>
            <th>训练批次</th>
          </tr>
        </thead>
        <tbody>${rows}</tbody>
      </table>
    </div>
  `;
}

function renderRetrainDetail() {
  const detail = state.retrainDetail;
  if (!detail) {
    renderEmpty(dom.retrainDetail, "选择样本查看");
    return;
  }

  const links = [
    detail.artifact_url
      ? `<a href="${escapeHtml(detail.artifact_url)}" data-download-url="${escapeHtml(detail.artifact_url)}" data-download-name="${escapeHtml(basenamePath(detail.artifact_url))}">下载标注图</a>`
      : "",
    `<a href="#review" data-review-item-id="${detail.item_id}">回到复核中心</a>`,
    `<a href="#history" data-history-id="${detail.run_id}">查看所属记录</a>`,
  ].filter(Boolean).join("");

  dom.retrainDetail.innerHTML = `
    <div class="summary-row">
      ${createSummaryPill("样本", `#${detail.item_id}`)}
      ${createSummaryPill("记录", `#${detail.run_id}`)}
      ${createSummaryPill("模式", formatMode(detail.mode))}
      ${createSummaryPill("来源模型", detail.source_model_name || "未知")}
      ${createSummaryPill("目录状态", formatRetrainStatus(detail.catalog_status))}
      ${createSummaryPill("加入时间", formatDateTime(detail.catalog_created_at))}
    </div>
    <div class="inline-links">${links}</div>
    ${detail.artifact_url ? `
      <div class="review-preview">
        <div class="annotation-preview-stage" data-retrain-stage>
          <img class="review-preview-image annotation-preview-image" src="${escapeHtml(detail.artifact_url)}" alt="${escapeHtml(detail.filename)}">
          <div id="retrainAnnotationOverlay" class="annotation-overlay">${buildRetrainAnnotationOverlayHtml(detail.annotation_draft || "")}</div>
        </div>
      </div>
    ` : ""}
    <div class="review-detail-grid">
      <div class="result-box">
        <div class="review-detail-head">
          <strong>${escapeHtml(detail.filename)}</strong>
          ${createStatusPill(detail.status)}
          ${createRetrainStatusPill(detail.catalog_status)}
        </div>
        <p class="helper-note">${escapeHtml(detail.recommendation || detail.error || "暂无模型结论。")}</p>
        <div class="summary-row">
          ${createSummaryPill("回流原因", formatReviewDecision(detail.review_decision))}
          ${createSummaryPill("目标数", `${detail.total_detections || 0}`)}
          ${createSummaryPill("腐烂占比", formatPercent(detail.rotten_rate || 0))}
          ${createSummaryPill("来源时间", formatDateTime(detail.source_created_at))}
        </div>
        <div class="summary-row">
          ${createSummaryPill("复核状态", formatReviewStatus(detail.review_status))}
          ${createSummaryPill("反馈状态", detail.feedback_status === "queued" ? "待回流" : "未回流")}
          ${createSummaryPill("模型格式", detail.source_model_type ? detail.source_model_type.toUpperCase() : "-")}
        </div>
        <div class="summary-row">
          ${createSummaryPill("标签状态", formatAnnotationStatus(detail.annotation_status))}
          ${createSummaryPill("草稿更新时间", formatDateTime(detail.annotation_updated_at) || "-")}
          ${createSummaryPill("批次状态", detail.batch_status ? formatRetrainBatchStatus(detail.batch_status) : "未入批次")}
        </div>
      </div>
      <div class="field-stack review-action-panel">
        <label class="field">
          <span>复训备注</span>
          <textarea id="retrainNotesInput" rows="4" placeholder="例如：建议补充遮挡、重叠、光照偏暗等场景样本。">${escapeHtml(detail.catalog_notes || detail.review_notes || "")}</textarea>
        </label>
        <label class="field">
          <span>标签草稿（YOLO）</span>
          <textarea id="retrainAnnotationInput" rows="8" placeholder="每行一个框：class x_center y_center width height&#10;例如：0 0.5 0.5 0.2 0.2">${escapeHtml(detail.annotation_draft || "")}</textarea>
        </label>
        <div id="retrainAnnotationStats" class="summary-row">${buildRetrainAnnotationStatsHtml(detail.annotation_draft || "")}</div>
        <div class="action-row review-action-row">
          <button class="btn btn-ghost" type="button" data-retrain-draft-tool="append_default">居中补一个框</button>
          <button class="btn btn-ghost" type="button" data-retrain-draft-tool="clear">清空草稿</button>
        </div>
        <div id="retrainAnnotationNotice" class="helper-note">${escapeHtml(buildRetrainAnnotationNoticeText(detail.annotation_draft || "", Boolean(detail.artifact_url)))}</div>
        <div id="retrainAnnotationList" class="annotation-draft-list">${buildRetrainAnnotationListHtml(detail.annotation_draft || "")}</div>
        <button class="btn btn-primary" type="button" data-retrain-action="save_draft">保存标签草稿</button>
        <div class="action-row review-action-row">
          <button class="btn btn-secondary ${detail.catalog_status === "pending" ? "is-active" : ""}" type="button" data-retrain-action="pending">待处理</button>
          <button class="btn btn-secondary ${detail.catalog_status === "ready" ? "is-active" : ""}" type="button" data-retrain-action="ready">待复训</button>
          <button class="btn btn-primary ${detail.catalog_status === "used" ? "is-active" : ""}" type="button" data-retrain-action="used">已入训练</button>
        </div>
        <div class="helper-note">这一步不是直接训练模型，而是把回流样本整理成可追踪、可复训、可导出的标准化目录。</div>
      </div>
    </div>
  `;
  renderRetrainAnnotationComposer();
}
async function handleReviewAction(action) {
  if (!state.selectedReviewItemId) {
    showNotice(dom.reviewNotice, "请先选择一个复核样本。", "warn");
    return;
  }

  if (action === "promote_retrain") {
    await promoteReviewItemToRetrain();
    return;
  }

  const notesInput = $("reviewNotesInput");
  const notes = notesInput ? notesInput.value.trim() : "";
  const payload =
    action === "feedback"
      ? {
          decision:
            state.reviewDetail?.review_decision && state.reviewDetail.review_decision !== "needs_feedback"
              ? state.reviewDetail.review_decision
              : "needs_feedback",
          notes,
          send_to_feedback: true,
        }
      : { decision: action, notes, send_to_feedback: false };

  try {
    showOverlay("保存复核", "正在写入复核结果...");
    state.reviewDetail = await apiPostJson(`${API_BASE}/review/items/${state.selectedReviewItemId}/decision`, payload);
    await Promise.all([
      loadReviewSummary(true),
      loadReviewItems(true),
      loadFeedbackPoolSummary(true),
      loadDashboardSummary(true),
      loadRetrainSummary(true),
      loadRetrainItems(true),
      loadHistory(true),
    ]);
    if (state.selectedRetrainItemId === state.selectedReviewItemId) {
      await loadRetrainDetail(state.selectedRetrainItemId, true);
    }
    renderReviewDetail();
    showNotice(dom.reviewNotice, "复核结果已保存。", "ok");
  } catch (error) {
    showNotice(dom.reviewNotice, error.message, "error");
  } finally {
    hideOverlay();
  }
}

async function promoteReviewItemToRetrain() {
  if (!state.selectedReviewItemId) {
    return;
  }

  const notesInput = $("reviewNotesInput");
  const notes = notesInput ? notesInput.value.trim() : "";
  const catalogStatus = state.reviewDetail?.retrain_status || "pending";

  try {
    showOverlay("加入复训目录", "正在沉淀回流样本...");
    await apiPostJson(`${API_BASE}/retrain/items/${state.selectedReviewItemId}`, {
      catalog_status: catalogStatus,
      catalog_notes: notes,
    });
    await Promise.all([
      loadReviewItems(true),
      loadReviewDetail(state.selectedReviewItemId, true),
      loadDashboardSummary(true),
      loadRetrainSummary(true),
      loadRetrainItems(true),
    ]);
    if (state.selectedRetrainItemId === state.selectedReviewItemId) {
      await loadRetrainDetail(state.selectedRetrainItemId, true);
    }
    showNotice(dom.reviewNotice, "样本已加入复训目录。", "ok");
  } catch (error) {
    showNotice(dom.reviewNotice, error.message, "error");
  } finally {
    hideOverlay();
  }
}

async function handleRetrainAction(action) {
  if (!state.selectedRetrainItemId) {
    showNotice(dom.retrainNotice, "请先选择一个复训样本。", "warn");
    return;
  }

  const notesInput = $("retrainNotesInput");
  const annotationInput = $("retrainAnnotationInput");
  const notes = notesInput ? notesInput.value.trim() : "";
  const annotationDraft = annotationInput ? annotationInput.value.trim() : "";
  const isDraftOnly = action === "save_draft";
  const nextCatalogStatus =
    isDraftOnly
      ? state.retrainDetail?.catalog_status || "pending"
      : action || state.retrainDetail?.catalog_status || "pending";

  try {
    showOverlay(
      isDraftOnly ? "保存标签草稿" : "更新复训目录",
      isDraftOnly ? "正在保存 YOLO 标签草稿..." : "正在保存目录状态...",
    );
    state.retrainDetail = await apiPostJson(`${API_BASE}/retrain/items/${state.selectedRetrainItemId}`, {
      catalog_status: nextCatalogStatus,
      catalog_notes: notes,
      annotation_draft: annotationDraft,
    });
    await Promise.all([
      loadDashboardSummary(true),
      loadRetrainSummary(true),
      loadRetrainItems(true),
      loadReviewItems(true),
      state.selectedRetrainItemId === state.selectedReviewItemId
        ? loadReviewDetail(state.selectedReviewItemId, true)
        : Promise.resolve(),
    ]);
    renderRetrainDetail();
    showNotice(dom.retrainNotice, isDraftOnly ? "标签草稿已保存。" : "复训目录已更新。", "ok");
  } catch (error) {
    showNotice(dom.retrainNotice, error.message, "error");
  } finally {
    hideOverlay();
  }
}
async function createRetrainBatch() {
  const itemIds = Array.from(state.selectedRetrainCatalogIds);
  if (!itemIds.length) {
    showNotice(dom.retrainNotice, "请先勾选待复训样本，再创建训练批次。", "warn");
    return;
  }

  const batchName = dom.retrainBatchNameInput?.value.trim() || buildDefaultRetrainBatchName();
  const batchNotes = dom.retrainBatchNotesInput?.value.trim() || "";

  try {
    showOverlay("创建训练批次", "正在整理复训样本并生成训练批次...");
    state.retrainBatchDetail = await apiPostJson(`${API_BASE}/retrain/batches`, {
      batch_name: batchName,
      batch_notes: batchNotes,
      item_ids: itemIds,
    });
    state.selectedRetrainBatchId = state.retrainBatchDetail.batch_id;
    state.selectedRetrainCatalogIds = new Set();
    if (dom.retrainBatchNameInput) {
      dom.retrainBatchNameInput.value = batchName;
    }
    if (dom.retrainBatchNotesInput) {
      dom.retrainBatchNotesInput.value = batchNotes;
    }
    await Promise.all([
      loadRetrainBatchSummary(true),
      loadRetrainBatches(true),
      loadRetrainSummary(true),
      loadRetrainItems(true),
    ]);
    renderRetrainBatchDetail();
    showNotice(dom.retrainNotice, `训练批次 ${batchName} 已创建，可继续导出标准样本包。`, "ok");
  } catch (error) {
    showNotice(dom.retrainNotice, error.message, "error");
  } finally {
    hideOverlay();
  }
}

async function exportTensorRt() {
  try {
    showOverlay("导出 TensorRT", "正在导出当前启用模型...");
    const formData = new FormData();
    formData.append("imgsz", dom.exportImgsz.value || "416");
    const payload = await apiRequest(`${API_BASE}/deployment/tensorrt/export`, { method: "POST", body: formData });
    state.deploymentOutput = { kind: "tensorrt_export", payload };
    renderDeploymentOutput();
    await loadDeployment(true);
    showNotice(dom.deploymentNotice, "TensorRT 导出完成。", "ok");
  } catch (error) {
    showNotice(dom.deploymentNotice, error.message, "error");
  } finally {
    hideOverlay();
  }
}

async function handleRetrainBatchAction(action) {
  if (action === "export") {
    await exportRetrainBatch();
  }
}

async function exportRetrainBatch() {
  if (!state.selectedRetrainBatchId) {
    showNotice(dom.retrainNotice, "请先选择一个训练批次。", "warn");
    return;
  }

  try {
    showOverlay("导出训练批次", "正在生成标准样本包并回写复训状态...");
    const result = await apiPostJson(`${API_BASE}/retrain/batches/${state.selectedRetrainBatchId}/export`, {});
    await downloadBlob(result.export_url, result.export_name);
    await Promise.all([
      loadDashboardSummary(true),
      loadRetrainSummary(true),
      loadRetrainBatchSummary(true),
      loadRetrainBatches(true),
      loadRetrainItems(true),
      loadReviewItems(true),
      loadRetrainBatchDetail(state.selectedRetrainBatchId, true),
      state.selectedRetrainItemId ? loadRetrainDetail(state.selectedRetrainItemId, true) : Promise.resolve(),
    ]);
    showNotice(dom.retrainNotice, result.message || "训练批次已导出。", "ok");
  } catch (error) {
    showNotice(dom.retrainNotice, error.message, "error");
  } finally {
    hideOverlay();
  }
}

function bindHistoryControls() {
  dom.refreshHistoryBtn.addEventListener("click", () => {
    void loadHistory(false);
  });
  dom.historyDeleteSelectedBtn.addEventListener("click", () => {
    void cleanupHistory({ run_ids: Array.from(state.selectedHistoryIds) }, "已删除选中记录。");
  });
  dom.historyDeleteAllBtn.addEventListener("click", () => {
    if (window.confirm("确认清空全部历史记录吗？")) {
      void cleanupHistory({ delete_all: true }, "历史记录已清空。");
    }
  });
  dom.historyDeleteRangeBtn.addEventListener("click", () => {
    const createdFrom = formatLocalDateTime(dom.historyCreatedFrom.value);
    const createdTo = formatLocalDateTime(dom.historyCreatedTo.value);
    if (!createdFrom && !createdTo) {
      showNotice(dom.historyNotice, "请至少选择一个时间范围。", "warn");
      return;
    }
    void cleanupHistory({ created_from: createdFrom, created_to: createdTo }, "指定时间范围内的记录已删除。");
  });

  dom.historyList.addEventListener("click", (event) => {
    const target = event.target.closest("[data-history-id]");
    if (!target) {
      return;
    }
    event.preventDefault();
    jumpToPanel("history");
    void loadHistoryDetail(Number(target.dataset.historyId), true);
  });

  dom.historyList.addEventListener("change", (event) => {
    const target = event.target;
    if (!(target instanceof HTMLInputElement)) {
      return;
    }
    if (target.matches("[data-history-select-all]")) {
      state.selectedHistoryIds = target.checked
        ? new Set(state.historyRuns.map((item) => item.id))
        : new Set();
      renderHistoryList();
      return;
    }
    if (target.matches("[data-history-select]")) {
      const id = Number(target.dataset.historySelect);
      if (target.checked) {
        state.selectedHistoryIds.add(id);
      } else {
        state.selectedHistoryIds.delete(id);
      }
      renderHistoryList();
    }
  });
}

function renderHistoryList() {
  if (!state.historyRuns.length) {
    renderEmpty(dom.historyList, "暂无历史记录");
    return;
  }
  const allSelected = state.historyRuns.length > 0 && state.historyRuns.every((item) => state.selectedHistoryIds.has(item.id));
  const rows = state.historyRuns
    .map((item) => `
      <tr class="${item.id === state.selectedHistoryId ? "is-active-row" : ""}">
        <td class="check-cell"><input type="checkbox" data-history-select="${item.id}" ${state.selectedHistoryIds.has(item.id) ? "checked" : ""}></td>
        <td><button class="table-link-button" type="button" data-history-id="${item.id}">#${item.id}</button></td>
        <td>${escapeHtml(formatMode(item.mode))}</td>
        <td>${escapeHtml(formatDateTime(item.created_at))}</td>
        <td>${item.successful_files}/${item.total_files}</td>
        <td>${item.total_detections}</td>
        <td>${item.csv_url ? `<a href="${escapeHtml(item.csv_url)}" data-download-url="${escapeHtml(item.csv_url)}" data-download-name="history-${item.id}.csv">CSV</a>` : '<span class="table-muted">-</span>'}</td>
      </tr>
    `)
    .join("");
  dom.historyList.innerHTML = `
    <div class="table-wrap">
      <table class="data-table">
        <thead>
          <tr>
            <th class="check-cell"><input type="checkbox" data-history-select-all ${allSelected ? "checked" : ""}></th>
            <th>ID</th>
            <th>模式</th>
            <th>时间</th>
            <th>成功</th>
            <th>目标数</th>
            <th>CSV</th>
          </tr>
        </thead>
        <tbody>${rows}</tbody>
      </table>
    </div>
  `;
}

function renderHistoryDetail() {
  const detail = state.historyDetail;
  if (!detail) {
    renderEmpty(dom.historyDetail, "选择记录查看");
    return;
  }
  const links = [
    detail.csv_url ? `<a href="${escapeHtml(detail.csv_url)}" data-download-url="${escapeHtml(detail.csv_url)}" data-download-name="history-${detail.id}.csv">下载 CSV</a>` : "",
    detail.excel_url ? `<a href="${escapeHtml(detail.excel_url)}" data-download-url="${escapeHtml(detail.excel_url)}" data-download-name="history-${detail.id}.xlsx">下载 Excel</a>` : "",
  ].filter(Boolean).join("");
  const itemRows = (detail.items || [])
    .map((item) => `
      <tr>
        <td>${escapeHtml(item.filename)}</td>
        <td>${createStatusPill(item.status)}</td>
        <td>${createReviewStatusPill(item.review_status)}</td>
        <td>${item.total_detections}</td>
        <td>${formatPercent(item.rotten_rate || 0)}</td>
        <td>${escapeHtml(item.recommendation || item.error || "-")}</td>
        <td>${item.artifact_url ? `<a href="${escapeHtml(item.artifact_url)}" data-download-url="${escapeHtml(item.artifact_url)}" data-download-name="${escapeHtml(basenamePath(item.artifact_url))}">下载</a>` : '<span class="table-muted">-</span>'}</td>
        <td><button class="table-link-button" type="button" data-review-item-id="${item.id}">复核</button></td>
      </tr>
    `)
    .join("");
  dom.historyDetail.innerHTML = `
    <div class="summary-row">
      ${createSummaryPill("ID", `#${detail.id}`)}
      ${createSummaryPill("模式", formatMode(detail.mode))}
      ${createSummaryPill("文件数", `${detail.total_files}`)}
      ${createSummaryPill("成功", `${detail.successful_files}`)}
      ${createSummaryPill("失败", `${detail.failed_files}`)}
      ${createSummaryPill("目标数", `${detail.total_detections}`)}
    </div>
    <div class="inline-links">${links}</div>
    <div class="table-wrap">
      <table class="data-table">
        <thead>
          <tr>
            <th>文件</th>
            <th>结果</th>
            <th>复核</th>
            <th>目标数</th>
            <th>腐烂占比</th>
            <th>结论</th>
            <th>标注图</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>${itemRows}</tbody>
      </table>
    </div>
  `;
}

async function cleanupHistory(payload, successMessage) {
  if (!payload.delete_all && !payload.run_ids?.length && !payload.created_from && !payload.created_to) {
    showNotice(dom.historyNotice, "请先选择要删除的历史记录。", "warn");
    return;
  }
  try {
    showOverlay("清理历史", "正在清理历史记录...");
    const result = await apiPostJson(`${API_BASE}/history/cleanup`, payload);
    state.selectedHistoryIds.clear();
    if (result.deleted_run_ids?.includes(state.selectedHistoryId)) {
      state.selectedHistoryId = null;
      state.historyDetail = null;
    }
    await Promise.allSettled([loadHistory(true), loadDashboardSummary(true)]);
    showNotice(dom.historyNotice, successMessage, "ok");
  } catch (error) {
    showNotice(dom.historyNotice, error.message, "error");
  } finally {
    hideOverlay();
  }
}

function bindCleanupControls() {
  dom.refreshStorageBtn.addEventListener("click", () => {
    void loadStorage(false);
  });
  dom.deleteSelectedBtn.addEventListener("click", () => {
    void cleanupArtifacts();
  });

  dom.artifactList.addEventListener("change", (event) => {
    const target = event.target;
    if (!(target instanceof HTMLInputElement)) {
      return;
    }
    if (target.matches("[data-artifact-select-all]")) {
      state.selectedArtifacts = target.checked
        ? new Set((state.storage?.artifacts || []).map((item) => item.name))
        : new Set();
      renderArtifactList();
      return;
    }
    if (target.matches("[data-artifact-select]")) {
      const name = target.dataset.artifactSelect || "";
      if (target.checked) {
        state.selectedArtifacts.add(name);
      } else {
        state.selectedArtifacts.delete(name);
      }
      renderArtifactList();
    }
  });
}

function renderStorageSummary() {
  const storage = state.storage;
  if (!storage) {
    renderEmpty(dom.storageSummary, "文件信息未加载");
    return;
  }
  dom.storageSummary.innerHTML = [
    createSummaryPill("可清理文件", `${storage.artifact_count || 0}`),
    createSummaryPill("总大小", formatSizeMb(storage.artifact_total_size_mb || 0)),
    createSummaryPill("历史可用", storage.history_available ? "是" : "否"),
  ].join("");
}

function renderArtifactList() {
  const artifacts = state.storage?.artifacts || [];
  if (!artifacts.length) {
    renderEmpty(dom.artifactList, "暂无可清理文件");
    return;
  }
  const allSelected = artifacts.length > 0 && artifacts.every((item) => state.selectedArtifacts.has(item.name));
  const rows = artifacts
    .map((item) => `
      <tr>
        <td class="check-cell"><input type="checkbox" data-artifact-select="${escapeHtml(item.name)}" ${state.selectedArtifacts.has(item.name) ? "checked" : ""}></td>
        <td>${escapeHtml(item.name)}</td>
        <td>${escapeHtml(item.type)}</td>
        <td>${formatSizeMb(item.size_mb || 0)}</td>
        <td>${item.download_url ? `<a href="${escapeHtml(item.download_url)}" data-download-url="${escapeHtml(item.download_url)}" data-download-name="${escapeHtml(item.name)}">下载</a>` : '<span class="table-muted">-</span>'}</td>
      </tr>
    `)
    .join("");
  dom.artifactList.innerHTML = `
    <div class="table-wrap">
      <table class="data-table">
        <thead>
          <tr>
            <th class="check-cell"><input type="checkbox" data-artifact-select-all ${allSelected ? "checked" : ""}></th>
            <th>文件</th>
            <th>类型</th>
            <th>大小</th>
            <th>下载</th>
          </tr>
        </thead>
        <tbody>${rows}</tbody>
      </table>
    </div>
  `;
}

async function cleanupArtifacts() {
  const names = Array.from(state.selectedArtifacts);
  if (!names.length) {
    showNotice(dom.cleanupNotice, "请先勾选要删除的文件。", "warn");
    return;
  }
  try {
    showOverlay("清理文件", "正在删除已选文件...");
    const payload = {
      artifact_names: names,
      delete_all: names.length === (state.storage?.artifacts?.length || 0),
      delete_history: false,
    };
    await apiPostJson(`${API_BASE}/maintenance/cleanup`, payload);
    state.selectedArtifacts.clear();
    await loadStorage(true);
    showNotice(dom.cleanupNotice, "文件清理完成。", "ok");
  } catch (error) {
    showNotice(dom.cleanupNotice, error.message, "error");
  } finally {
    hideOverlay();
  }
}

document.addEventListener("DOMContentLoaded", init);
window.addEventListener("beforeunload", cleanupBeforeUnload);
