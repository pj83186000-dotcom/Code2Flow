/**
 * Code2Flow — Interactive Multi-Language Frontend Engine
 * Client-side controller for Python, JavaScript, Java, and C++.
 */

(function () {
  "use strict";

  // State Management
  const state = window._code2flowState = {
    language: "python",
    currentTab: "flowchart",
    flowchart: {
      graph: null,
      mermaid: "",
      dot: "",
      svg: "",
      scale: 1.0,
      panX: 0,
      panY: 0,
      isPanning: false,
      startX: 0,
      startY: 0,
      highlightNodeId: null
    },
    dsa: {
      frames: [],
      currentStep: 0,
      isPlaying: false,
      playTimer: null,
      speed: 600
    },
    oop: {
      data: null,
      mermaid: "",
      dot: ""
    },
    viz: {
      frames: [],
      currentStep: 0,
      isPlaying: false,
      playTimer: null,
      speed: 700,
      structures: []
    },
    samples: null
  };

  // DOM Elements
  const els = {
    tabs: document.querySelectorAll(".nav-tab"),
    views: document.querySelectorAll(".workspace-view"),
    themeToggle: document.getElementById("theme-toggle"),
    toast: document.getElementById("toast"),
    globalLangSelect: document.getElementById("global-language-select"),
    editorLangTitle: document.getElementById("editor-lang-title"),
    oopLangTitle: document.getElementById("oop-lang-title"),

    // Flowchart
    flowchartCode: document.getElementById("flowchart-code"),
    flowchartSampleSelect: document.getElementById("flowchart-sample-select"),
    btnGenerateFlowchart: document.getElementById("btn-generate-flowchart"),
    btnToggleDebug: document.getElementById("btn-toggle-debug"),
    debugDrawer: document.getElementById("debug-drawer"),
    tracebackInput: document.getElementById("traceback-input"),
    tracebackSampleSelect: document.getElementById("traceback-sample-select"),
    btnMapTraceback: document.getElementById("btn-map-traceback"),
    btnClearHighlight: document.getElementById("btn-clear-highlight"),
    btnCloseDebug: document.getElementById("btn-close-debug"),
    tracebackCard: document.getElementById("traceback-card"),
    excTag: document.getElementById("exc-tag"),
    excLine: document.getElementById("exc-line"),
    excMsg: document.getElementById("exc-msg"),
    excExplanation: document.getElementById("exc-explanation"),
    excSuggestion: document.getElementById("exc-suggestion"),
    codeContextBlock: document.getElementById("code-context-block"),
    warningsBox: document.getElementById("warnings-box"),
    syntaxStatus: document.getElementById("syntax-status"),

    // Flowchart Viewport
    flowchartViewport: document.getElementById("flowchart-viewport"),
    flowchartTransform: document.getElementById("flowchart-transform"),
    flowchartContainer: document.getElementById("flowchart-container"),
    nodeCountBadge: document.getElementById("node-count-badge"),
    nodeSearch: document.getElementById("node-search"),
    btnZoomIn: document.getElementById("btn-zoom-in"),
    btnZoomOut: document.getElementById("btn-zoom-out"),
    btnZoomReset: document.getElementById("btn-zoom-reset"),
    btnFitScreen: document.getElementById("btn-fit-screen"),

    // Export Dropdown
    exportDropdownBtn: document.getElementById("export-dropdown-btn"),
    exportMenu: document.getElementById("export-menu"),
    exportSvg: document.getElementById("export-svg"),
    exportHtml: document.getElementById("export-html"),
    exportMermaid: document.getElementById("export-mermaid"),
    exportDot: document.getElementById("export-dot"),
    exportJson: document.getElementById("export-json"),

    // Inspector
    nodeInspector: document.getElementById("node-inspector"),
    btnCloseInspector: document.getElementById("btn-close-inspector"),
    inspId: document.getElementById("insp-id"),
    inspType: document.getElementById("insp-type"),
    inspCat: document.getElementById("insp-cat"),
    inspLine: document.getElementById("insp-line"),
    inspScope: document.getElementById("insp-scope"),
    inspCode: document.getElementById("insp-code"),
    inspDetails: document.getElementById("insp-details"),

    // DSA
    dsaAlgorithmSelect: document.getElementById("dsa-algorithm-select"),
    dsaInputField: document.getElementById("dsa-input-field"),
    dsaInputHelper: document.getElementById("dsa-input-helper"),
    btnRunDsa: document.getElementById("btn-run-dsa"),
    currentStepNum: document.getElementById("current-step-num"),
    totalStepNum: document.getElementById("total-step-num"),
    stepNarrativeText: document.getElementById("step-narrative-text"),
    stepCodeLine: document.getElementById("step-code-line"),
    dsaCanvasContainer: document.getElementById("dsa-canvas-container"),
    dsaStepSlider: document.getElementById("dsa-step-slider"),
    dsaSpeed: document.getElementById("dsa-speed"),
    dsaBtnFirst: document.getElementById("dsa-btn-first"),
    dsaBtnPrev: document.getElementById("dsa-btn-prev"),
    dsaBtnPlay: document.getElementById("dsa-btn-play"),
    dsaBtnNext: document.getElementById("dsa-btn-next"),
    dsaBtnLast: document.getElementById("dsa-btn-last"),
    dsaBtnReset: document.getElementById("dsa-btn-reset"),
    playIcon: document.getElementById("play-icon"),
    timeBest: document.getElementById("time-best"),
    timeAvg: document.getElementById("time-avg"),
    timeWorst: document.getElementById("time-worst"),
    spaceComp: document.getElementById("space-comp"),
    complexityExplanation: document.getElementById("complexity-explanation"),
    dsaVarTable: document.getElementById("dsa-var-table"),

    // OOP
    oopCode: document.getElementById("oop-code"),
    oopSampleSelect: document.getElementById("oop-sample-select"),
    btnGenerateOop: document.getElementById("btn-generate-oop"),
    oopDiagramContainer: document.getElementById("oop-diagram-container"),
    oopRelationshipList: document.getElementById("oop-relationship-list"),
    oopCallFlows: document.getElementById("oop-call-flows"),
    oopClassCount: document.getElementById("oop-class-count"),
    btnCopyOopMermaid: document.getElementById("btn-copy-oop-mermaid"),
    btnCopyOopDot: document.getElementById("btn-copy-oop-dot"),

    // Code Visualizer (Tab 4)
    vizCode: document.getElementById("viz-code"),
    vizSampleSelect: document.getElementById("viz-sample-select"),
    btnTraceCode: document.getElementById("btn-trace-code"),
    btnVizClear: document.getElementById("btn-viz-clear"),
    vizStatus: document.getElementById("viz-status"),
    vizStepNum: document.getElementById("viz-step-num"),
    vizTotalSteps: document.getElementById("viz-total-steps"),
    vizNarration: document.getElementById("viz-narration"),
    vizCanvas: document.getElementById("viz-canvas"),
    vizEmptyState: document.getElementById("viz-empty-state"),
    vizVarPanel: document.getElementById("viz-var-panel"),
    vizVarGrid: document.getElementById("viz-var-grid"),
    vizVarStep: document.getElementById("viz-var-step"),
    vizPlaybackBar: document.getElementById("viz-playback-bar"),
    vizStepSlider: document.getElementById("viz-step-slider"),
    vizSpeed: document.getElementById("viz-speed"),
    vizBtnFirst: document.getElementById("viz-btn-first"),
    vizBtnPrev: document.getElementById("viz-btn-prev"),
    vizBtnPlay: document.getElementById("viz-btn-play"),
    vizBtnNext: document.getElementById("viz-btn-next"),
    vizBtnLast: document.getElementById("viz-btn-last"),
    vizPlayIcon: document.getElementById("viz-play-icon"),
    vizLineNumbers: document.getElementById("viz-line-numbers"),
    vizOutputBox: document.getElementById("viz-output-box"),
    vizOutputText: document.getElementById("viz-output-text")
  };

  // Toast Notification
  function showToast(message, duration = 3000) {
    if (!els.toast) return;
    els.toast.textContent = message;
    els.toast.classList.add("show");
    setTimeout(() => {
      els.toast.classList.remove("show");
    }, duration);
  }

  // Theme Toggle
  function initTheme() {
    const savedTheme = localStorage.getItem("code2flow-theme") || "dark";
    document.documentElement.setAttribute("data-theme", savedTheme);

    els.themeToggle.addEventListener("click", () => {
      const current = document.documentElement.getAttribute("data-theme");
      const next = current === "dark" ? "light" : "dark";
      document.documentElement.setAttribute("data-theme", next);
      localStorage.setItem("code2flow-theme", next);
      showToast(`Switched to ${next} theme.`);
    });
  }

  // Tab Navigation
  function initTabs() {
    els.tabs.forEach(tab => {
      tab.addEventListener("click", () => {
        const target = tab.dataset.tab;
        state.currentTab = target;

        els.tabs.forEach(t => {
          t.classList.remove("active");
          t.setAttribute("aria-selected", "false");
        });
        tab.classList.add("active");
        tab.setAttribute("aria-selected", "true");

        els.views.forEach(v => v.classList.remove("active"));
        const targetView = document.getElementById(`view-${target}`);
        if (targetView) targetView.classList.add("active");
      });
    });
  }

  // Pan & Zoom for Flowchart
  function initPanZoom() {
    function updateTransform() {
      els.flowchartTransform.style.transform = `translate(${state.flowchart.panX}px, ${state.flowchart.panY}px) scale(${state.flowchart.scale})`;
      els.btnZoomReset.textContent = `${Math.round(state.flowchart.scale * 100)}%`;
    }

    els.flowchartViewport.addEventListener("mousedown", (e) => {
      if (e.target.closest(".flow-node-group") || e.target.closest(".inspector-drawer")) return;
      state.flowchart.isPanning = true;
      state.flowchart.startX = e.clientX - state.flowchart.panX;
      state.flowchart.startY = e.clientY - state.flowchart.panY;
    });

    window.addEventListener("mousemove", (e) => {
      if (!state.flowchart.isPanning) return;
      state.flowchart.panX = e.clientX - state.flowchart.startX;
      state.flowchart.panY = e.clientY - state.flowchart.startY;
      updateTransform();
    });

    window.addEventListener("mouseup", () => {
      state.flowchart.isPanning = false;
    });

    els.flowchartViewport.addEventListener("wheel", (e) => {
      e.preventDefault();
      const zoomFactor = e.deltaY < 0 ? 1.1 : 0.9;
      state.flowchart.scale = Math.min(Math.max(0.2, state.flowchart.scale * zoomFactor), 3.0);
      updateTransform();
    }, { passive: false });

    els.btnZoomIn.addEventListener("click", () => {
      state.flowchart.scale = Math.min(3.0, state.flowchart.scale * 1.2);
      updateTransform();
    });

    els.btnZoomOut.addEventListener("click", () => {
      state.flowchart.scale = Math.max(0.2, state.flowchart.scale * 0.8);
      updateTransform();
    });

    els.btnZoomReset.addEventListener("click", () => {
      state.flowchart.scale = 1.0;
      state.flowchart.panX = 0;
      state.flowchart.panY = 0;
      updateTransform();
    });

    els.btnFitScreen.addEventListener("click", () => {
      const svg = els.flowchartContainer.querySelector("svg");
      if (!svg) return;
      const rect = els.flowchartViewport.getBoundingClientRect();
      const viewBox = svg.viewBox.baseVal;
      if (viewBox && viewBox.width > 0) {
        const scaleX = (rect.width - 60) / viewBox.width;
        const scaleY = (rect.height - 60) / viewBox.height;
        state.flowchart.scale = Math.min(scaleX, scaleY, 1.2);
        state.flowchart.panX = 30;
        state.flowchart.panY = 30;
        updateTransform();
      }
    });

    state.flowchart.updateTransform = updateTransform;
  }

  // Fetch Multi-Language Samples
  async function loadSamples() {
    try {
      const res = await fetch("/api/samples");
      const json = await res.json();
      if (json.success) {
        state.samples = json.samples;
        populateSamplesForLanguage(state.language);
      }
    } catch (err) {
      console.error("Failed to load sample programs:", err);
    }
  }

  function populateSamplesForLanguage(lang) {
    if (!state.samples || !state.samples[lang]) return;
    const langData = state.samples[lang];

    // Flowchart Samples
    els.flowchartSampleSelect.innerHTML = '<option value="">Load Sample Program...</option>';
    if (langData.flowchart) {
      for (const [key, item] of Object.entries(langData.flowchart)) {
        const opt = document.createElement("option");
        opt.value = key;
        opt.textContent = item.title;
        els.flowchartSampleSelect.appendChild(opt);
      }
    }

    // Traceback Samples
    els.tracebackSampleSelect.innerHTML = '<option value="">Load Buggy Sample...</option>';
    if (langData.traceback) {
      for (const [key, item] of Object.entries(langData.traceback)) {
        const opt = document.createElement("option");
        opt.value = key;
        opt.textContent = item.title;
        els.tracebackSampleSelect.appendChild(opt);
      }
    }

    // OOP Samples
    els.oopSampleSelect.innerHTML = '<option value="">Load OOP Sample...</option>';
    if (langData.oop) {
      for (const [key, item] of Object.entries(langData.oop)) {
        const opt = document.createElement("option");
        opt.value = key;
        opt.textContent = item.title;
        els.oopSampleSelect.appendChild(opt);
      }
    }

    // Load first default flowchart sample
    const firstFlowKey = Object.keys(langData.flowchart || {})[0];
    if (firstFlowKey) {
      els.flowchartCode.value = langData.flowchart[firstFlowKey].code;
    }

    // Load first default OOP sample
    const firstOopKey = Object.keys(langData.oop || {})[0];
    if (firstOopKey) {
      els.oopCode.value = langData.oop[firstOopKey].code;
    }
  }

  // Language Change Handler
  function initLanguageSelector() {
    els.globalLangSelect.addEventListener("change", (e) => {
      const lang = e.target.value;
      state.language = lang;

      const langNames = {
        python: "Python Source Code",
        javascript: "JavaScript Source Code",
        java: "Java Source Code",
        cpp: "C / C++ Source Code"
      };

      els.editorLangTitle.textContent = langNames[lang] || "Source Code";
      els.oopLangTitle.textContent = `${lang.toUpperCase()} Class Definition`;

      if (typeof window.updateVizLanguage === "function") {
        window.updateVizLanguage(lang);
      }

      populateSamplesForLanguage(lang);
      showToast(`Language switched to ${lang.toUpperCase()}`);

      // Auto generate flowchart for the selected language
      generateFlowchart();
    });
  }

  // ==================== TAB 1: FLOWCHART LOGIC ====================

  async function generateFlowchart(highlightId = null) {
    const code = els.flowchartCode.value;
    if (!code.trim()) {
      showToast("Please enter source code to generate a flowchart.");
      return;
    }

    els.syntaxStatus.textContent = "Parsing...";
    els.syntaxStatus.className = "syntax-status";

    try {
      const res = await fetch("/api/flowchart", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code, language: state.language })
      });

      const data = await res.json();

      if (!data.success) {
        els.syntaxStatus.textContent = "Syntax Error";
        els.syntaxStatus.className = "syntax-status badge-err";
        showSyntaxError(data.error);
        return;
      }

      els.syntaxStatus.textContent = `Valid ${state.language.toUpperCase()}`;
      els.syntaxStatus.className = "syntax-status badge-ok";
      els.warningsBox.style.display = "none";

      if (data.warnings && data.warnings.length > 0) {
        els.warningsBox.innerHTML = "<strong>Warnings:</strong><br>" + data.warnings.join("<br>");
        els.warningsBox.style.display = "block";
      }

      state.flowchart.graph = data.graph;
      state.flowchart.mermaid = data.mermaid;
      state.flowchart.dot = data.dot;
      state.flowchart.svg = data.svg;
      state.flowchart.highlightNodeId = highlightId;

      els.nodeCountBadge.textContent = `${data.graph.node_count} nodes`;

      renderFlowchartSVG(data.svg, highlightId);

      if (state.flowchart.scale === 1.0 && state.flowchart.panX === 0) {
        setTimeout(() => els.btnFitScreen.click(), 50);
      }

    } catch (err) {
      console.error("Error generating flowchart:", err);
      showToast("Failed to connect to Code2Flow backend.");
    }
  }

  function renderFlowchartSVG(svgString, highlightId) {
    els.flowchartContainer.innerHTML = svgString;

    const svgEl = els.flowchartContainer.querySelector("svg");
    if (!svgEl) return;

    const nodeGroups = svgEl.querySelectorAll(".flow-node-group");
    nodeGroups.forEach(grp => {
      grp.addEventListener("click", (e) => {
        e.stopPropagation();
        const nid = grp.dataset.nodeId;
        openNodeInspector(nid);
      });
    });

    if (highlightId) {
      const targetGroup = svgEl.querySelector(`[data-node-id="${highlightId}"]`);
      if (targetGroup) {
        targetGroup.classList.add("error-highlight-pulse");
        centerOnNode(targetGroup);
      }
    }
  }

  function centerOnNode(nodeElement) {
    const bbox = nodeElement.getBBox();
    const vpRect = els.flowchartViewport.getBoundingClientRect();
    const cx = bbox.x + bbox.width / 2;
    const cy = bbox.y + bbox.height / 2;

    state.flowchart.panX = (vpRect.width / 2) - (cx * state.flowchart.scale);
    state.flowchart.panY = (vpRect.height / 2) - (cy * state.flowchart.scale);
    state.flowchart.updateTransform();
  }

  function openNodeInspector(nodeId) {
    if (!state.flowchart.graph) return;
    const node = state.flowchart.graph.nodes.find(n => n.id === nodeId);
    if (!node) return;

    els.inspId.textContent = node.id;
    els.inspType.textContent = node.ast_type || "Node";
    els.inspCat.textContent = node.category || "process";
    els.inspLine.textContent = node.lineno ? `Line ${node.lineno}` : "Synthetic Node";
    els.inspScope.textContent = node.scope || "global";
    els.inspCode.textContent = node.label || "-";
    els.inspDetails.textContent = node.details || "No additional metadata.";

    els.nodeInspector.classList.add("open");
  }

  function showSyntaxError(err) {
    els.warningsBox.innerHTML = `<strong>${err.message}</strong>` +
      (err.text ? `<br><code>${err.text}</code>` : "");
    els.warningsBox.style.display = "block";
  }

  function initNodeSearch() {
    els.nodeSearch.addEventListener("input", (e) => {
      const query = e.target.value.toLowerCase().trim();
      const svg = els.flowchartContainer.querySelector("svg");
      if (!svg) return;

      const nodes = svg.querySelectorAll(".flow-node-group");
      nodes.forEach(n => {
        const lbl = n.querySelector(".node-label");
        const text = lbl ? lbl.textContent.toLowerCase() : "";
        if (!query) {
          n.style.opacity = "1";
          n.style.filter = "";
        } else if (text.includes(query)) {
          n.style.opacity = "1";
          n.style.filter = "drop-shadow(0 0 8px #3b82f6)";
        } else {
          n.style.opacity = "0.2";
          n.style.filter = "";
        }
      });
    });
  }

  // Traceback Debugger Logic
  async function mapTraceback() {
    const tbText = els.tracebackInput.value;
    const code = els.flowchartCode.value;

    if (!tbText.trim()) {
      showToast("Please paste an error traceback or compiler message.");
      return;
    }

    if (!state.flowchart.graph) {
      await generateFlowchart();
    }

    try {
      const res = await fetch("/api/traceback", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          code: code,
          traceback: tbText,
          nodes: state.flowchart.graph ? state.flowchart.graph.nodes : [],
          language: state.language
        })
      });

      const data = await res.json();
      if (!data.success) return;

      const analysis = data.analysis;
      displayTracebackAnalysis(analysis);

    } catch (err) {
      console.error("Error analyzing traceback:", err);
      showToast("Failed to process error message.");
    }
  }

  function displayTracebackAnalysis(analysis) {
    els.tracebackCard.style.display = "flex";
    els.btnClearHighlight.style.display = "inline-flex";

    els.excTag.textContent = analysis.exception_type || "Error";
    els.excLine.textContent = analysis.matched_lineno ? `Line ${analysis.matched_lineno}` : "Unknown Line";
    els.excMsg.textContent = analysis.exception_message || "(no error description)";

    if (analysis.guide) {
      els.excExplanation.textContent = analysis.guide.explanation || "";
      els.excSuggestion.textContent = analysis.guide.suggestion || "";
    }

    let contextHtml = "";
    if (analysis.context_lines && analysis.context_lines.length > 0) {
      analysis.context_lines.forEach(row => {
        const cls = row.is_error ? "context-row error-row" : "context-row";
        const arrow = row.is_error ? ">>>" : "   ";
        contextHtml += `<div class="${cls}">
          <span class="context-num">${row.lineno}</span>
          <span>${arrow} ${escapeHtml(row.code)}</span>
        </div>`;
      });
    }
    els.codeContextBlock.innerHTML = contextHtml;

    if (analysis.matched_node_id) {
      state.flowchart.highlightNodeId = analysis.matched_node_id;
      fetch("/api/export", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          type: "svg",
          graph: state.flowchart.graph,
          highlight_id: analysis.matched_node_id
        })
      }).then(r => r.json()).then(expData => {
        if (expData.success) {
          renderFlowchartSVG(expData.content, analysis.matched_node_id);
          showToast(`Error located at Node ${analysis.matched_node_id} (Line ${analysis.matched_lineno})`);
        }
      });
    } else {
      showToast(analysis.notes || "No direct flowchart node matched this line.", 4000);
    }
  }

  function clearErrorHighlight() {
    state.flowchart.highlightNodeId = null;
    els.tracebackCard.style.display = "none";
    els.btnClearHighlight.style.display = "none";
    if (state.flowchart.graph) {
      renderFlowchartSVG(state.flowchart.svg, null);
    }
    showToast("Error highlight cleared.");
  }

  function escapeHtml(str) {
    if (!str) return "";
    return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  }

  // Export Handlers
  function initExports() {
    els.exportDropdownBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      els.exportDropdownBtn.parentElement.classList.toggle("active");
    });

    window.addEventListener("click", () => {
      els.exportDropdownBtn.parentElement.classList.remove("active");
    });

    els.exportSvg.addEventListener("click", (e) => {
      e.preventDefault();
      const svg = els.flowchartContainer.querySelector("svg");
      if (!svg) {
        showToast("No flowchart to export.");
        return;
      }
      const blob = new Blob([svg.outerHTML], { type: "image/svg+xml" });
      downloadBlob(blob, `code2flow_${state.language}_diagram.svg`);
    });

    els.exportHtml.addEventListener("click", async (e) => {
      e.preventDefault();
      if (!state.flowchart.graph) return;
      const res = await fetch("/api/export", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          type: "html",
          graph: state.flowchart.graph,
          title: `${state.language.toUpperCase()} Flowchart Export`
        })
      });
      const data = await res.json();
      if (data.success) {
        const blob = new Blob([data.content], { type: "text/html" });
        downloadBlob(blob, `code2flow_${state.language}_standalone.html`);
      }
    });

    els.exportMermaid.addEventListener("click", (e) => {
      e.preventDefault();
      if (!state.flowchart.mermaid) return;
      copyToClipboard(state.flowchart.mermaid, "Copied Mermaid flowchart source code!");
    });

    els.exportDot.addEventListener("click", (e) => {
      e.preventDefault();
      if (!state.flowchart.dot) return;
      copyToClipboard(state.flowchart.dot, "Copied Graphviz DOT source code!");
    });

    els.exportJson.addEventListener("click", (e) => {
      e.preventDefault();
      if (!state.flowchart.graph) return;
      const blob = new Blob([JSON.stringify(state.flowchart.graph, null, 2)], { type: "application/json" });
      downloadBlob(blob, `code2flow_${state.language}_graph.json`);
    });
  }

  function downloadBlob(blob, filename) {
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    showToast(`Downloaded ${filename}`);
  }

  function copyToClipboard(text, msg) {
    navigator.clipboard.writeText(text).then(() => {
      showToast(msg);
    }).catch(() => {
      showToast("Clipboard copy failed.");
    });
  }

  // ==================== TAB 2: DSA VISUALIZER LOGIC ====================

  async function runDSASimulation() {
    const alg = els.dsaAlgorithmSelect.value;
    const inputVal = els.dsaInputField.value;

    try {
      const res = await fetch("/api/dsa", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ algorithm: alg, input: inputVal })
      });

      const data = await res.json();
      if (!data.success) {
        showToast(data.error || "DSA simulation failed.");
        return;
      }

      state.dsa.frames = data.frames;
      state.dsa.currentStep = 0;
      els.dsaStepSlider.max = data.total_steps;
      els.dsaStepSlider.value = 1;

      if (data.frames.length > 0) {
        const c = data.frames[0].complexity;
        els.timeBest.textContent = c.time_best || "-";
        els.timeAvg.textContent = c.time_avg || "-";
        els.timeWorst.textContent = c.time_worst || "-";
        els.spaceComp.textContent = c.space || "-";
        els.complexityExplanation.textContent = c.explanation || "";
      }

      renderDSAStep(0);
      showToast(`Generated ${data.total_steps} step simulation for ${alg}.`);

    } catch (err) {
      console.error("DSA error:", err);
      showToast("Failed to run DSA simulation.");
    }
  }

  function renderDSAStep(stepIndex) {
    if (!state.dsa.frames || state.dsa.frames.length === 0) return;
    const frame = state.dsa.frames[stepIndex];
    if (!frame) return;

    state.dsa.currentStep = stepIndex;
    els.currentStepNum.textContent = frame.step;
    els.totalStepNum.textContent = frame.total_steps;
    els.dsaStepSlider.value = frame.step;
    els.stepNarrativeText.textContent = frame.action;
    els.stepCodeLine.querySelector("code").textContent = frame.code_line;

    renderVariables(frame.variables);

    if (frame.data_type === "array") {
      renderArrayVisual(frame.state.items);
    } else if (frame.data_type === "linked_list") {
      renderLinkedListVisual(frame.state.nodes, frame.variables);
    } else if (frame.data_type === "tree") {
      renderTreeVisual(frame.state);
    } else if (frame.data_type === "graph") {
      renderGraphVisual(frame.state);
    } else if (frame.data_type === "recursion") {
      renderRecursionVisual(frame.state.call_stack);
    } else if (frame.data_type === "stack_queue") {
      renderStackQueueVisual(frame.state);
    }
  }

  function renderVariables(varsDict) {
    if (!varsDict || Object.keys(varsDict).length === 0) {
      els.dsaVarTable.innerHTML = '<span class="empty-hint">No active variables.</span>';
      return;
    }
    let html = "";
    for (const [k, v] of Object.entries(varsDict)) {
      html += `<div class="var-row">
        <span class="var-name">${k}:</span>
        <span class="var-val">${JSON.stringify(v)}</span>
      </div>`;
    }
    els.dsaVarTable.innerHTML = html;
  }

  function renderArrayVisual(items) {
    let html = '<div class="array-container">';
    const maxVal = Math.max(...items.map(i => Math.abs(i.val)), 1);

    items.forEach(item => {
      const height = Math.max(36, Math.min(220, (item.val / maxVal) * 180));
      html += `<div class="array-bar-col">
        <div class="array-bar state-${item.state}" style="height: ${height}px;">
          ${item.val}
        </div>
        <span class="array-index">[${item.index}]</span>
      </div>`;
    });
    html += '</div>';
    els.dsaCanvasContainer.innerHTML = html;
  }

  function renderLinkedListVisual(nodes, vars) {
    let html = '<div class="ll-container">';
    nodes.forEach((n, idx) => {
      const isCurr = vars.curr === n.val;
      const isPrev = vars.prev === n.val;
      const isNext = vars.next === n.val;
      let badge = "";
      if (isCurr) badge += '<span class="rel-tag composition">curr</span> ';
      if (isPrev) badge += '<span class="rel-tag inheritance">prev</span> ';
      if (isNext) badge += '<span class="rel-tag aggregation">next</span> ';

      html += `<div class="ll-node">
        <div style="font-size:0.7rem; color:#94a3b8;">${badge}</div>
        <div>val: ${n.val}</div>
      </div>`;
      if (idx < nodes.length - 1) {
        html += '<span class="ll-arrow">&rarr;</span>';
      }
    });
    html += '</div>';
    els.dsaCanvasContainer.innerHTML = html;
  }

  function renderTreeVisual(treeState) {
    const nodes = treeState.nodes || [];
    const edges = treeState.edges || [];

    let svg = '<svg width="600" height="280" style="overflow:visible;">';
    edges.forEach(e => {
      const fromN = nodes.find(n => n.id === e.from);
      const toN = nodes.find(n => n.id === e.to);
      if (fromN && toN) {
        svg += `<line x1="${fromN.x}" y1="${fromN.y}" x2="${toN.x}" y2="${toN.y}" stroke="#64748b" stroke-width="2" />`;
      }
    });
    nodes.forEach(n => {
      let fill = "#1e293b";
      let stroke = "#3b82f6";
      if (n.state === "active") {
        fill = "#f59e0b";
        stroke = "#d97706";
      } else if (n.state === "visited") {
        fill = "#10b981";
        stroke = "#059669";
      }
      svg += `<circle cx="${n.x}" cy="${n.y}" r="20" fill="${fill}" stroke="${stroke}" stroke-width="2" />`;
      svg += `<text x="${n.x}" y="${n.y + 5}" text-anchor="middle" fill="#ffffff" font-family="sans-serif" font-weight="700" font-size="12">${n.val}</text>`;
    });
    svg += '</svg>';
    els.dsaCanvasContainer.innerHTML = svg;
  }

  function renderGraphVisual(graphState) {
    const nodes = graphState.nodes || [];
    const edges = graphState.edges || [];

    let svg = '<svg width="450" height="340" style="overflow:visible;">';
    edges.forEach(e => {
      const u = nodes.find(n => n.id === e.from);
      const v = nodes.find(n => n.id === e.to);
      if (u && v) {
        const col = e.is_active ? "#f59e0b" : "#64748b";
        const w = e.is_active ? "3" : "1.5";
        svg += `<line x1="${u.x}" y1="${u.y}" x2="${v.x}" y2="${v.y}" stroke="${col}" stroke-width="${w}" />`;
      }
    });
    nodes.forEach(n => {
      let fill = "#1e293b";
      let stroke = "#3b82f6";
      if (n.state === "current") {
        fill = "#f59e0b";
        stroke = "#d97706";
      } else if (n.state === "visited") {
        fill = "#10b981";
        stroke = "#059669";
      } else if (n.state === "queued") {
        fill = "#8b5cf6";
        stroke = "#7c3aed";
      }
      svg += `<circle cx="${n.x}" cy="${n.y}" r="18" fill="${fill}" stroke="${stroke}" stroke-width="2" />`;
      svg += `<text x="${n.x}" y="${n.y + 5}" text-anchor="middle" fill="#ffffff" font-weight="700" font-size="12">${n.id}</text>`;
    });
    svg += '</svg>';
    els.dsaCanvasContainer.innerHTML = svg;
  }

  function renderRecursionVisual(callStack) {
    let html = '<div style="display:flex; flex-direction:column-reverse; gap:0.5rem; width:260px;">';
    if (!callStack || callStack.length === 0) {
      html += '<span class="empty-hint">Stack is empty.</span>';
    } else {
      callStack.forEach((call, idx) => {
        const isTop = idx === callStack.length - 1;
        const bg = isTop ? "rgba(59, 130, 246, 0.25)" : "var(--bg-surface)";
        const border = isTop ? "#3b82f6" : "var(--border-subtle)";
        html += `<div style="background:${bg}; border:1px solid ${border}; border-radius:6px; padding:0.6rem 1rem; font-family:var(--font-mono); font-size:0.85rem; font-weight:600; display:flex; justify-content:space-between;">
          <span>${call}</span>
          <span style="font-size:0.7rem; color:#94a3b8;">#${idx}</span>
        </div>`;
      });
    }
    html += '</div>';
    els.dsaCanvasContainer.innerHTML = html;
  }

  function renderStackQueueVisual(sqState) {
    const items = sqState.items || [];
    let html = `<div style="display:flex; flex-direction:column; align-items:center; gap:0.5rem;">
      <h4 style="color:#94a3b8;">${sqState.structure.toUpperCase()} (${items.length} items)</h4>
      <div style="display:flex; gap:0.5rem; background:var(--bg-secondary); padding:1rem; border-radius:8px; border:1px solid var(--border-subtle);">`;
    items.forEach(it => {
      html += `<div style="background:var(--accent-primary); color:#ffffff; padding:0.5rem 1rem; border-radius:6px; font-weight:700; font-family:var(--font-mono);">${it}</div>`;
    });
    html += '</div></div>';
    els.dsaCanvasContainer.innerHTML = html;
  }

  // Playback Controls
  function initDSAPlayback() {
    function togglePlay() {
      if (state.dsa.isPlaying) {
        pause();
      } else {
        play();
      }
    }

    function play() {
      if (state.dsa.currentStep >= state.dsa.frames.length - 1) {
        state.dsa.currentStep = 0;
      }
      state.dsa.isPlaying = true;
      els.playIcon.innerHTML = "&#10074;&#10074; Pause";
      state.dsa.playTimer = setInterval(() => {
        if (state.dsa.currentStep < state.dsa.frames.length - 1) {
          renderDSAStep(state.dsa.currentStep + 1);
        } else {
          pause();
        }
      }, state.dsa.speed);
    }

    function pause() {
      state.dsa.isPlaying = false;
      els.playIcon.innerHTML = "&#9654; Play";
      if (state.dsa.playTimer) {
        clearInterval(state.dsa.playTimer);
        state.dsa.playTimer = null;
      }
    }

    els.dsaBtnPlay.addEventListener("click", togglePlay);

    els.dsaBtnNext.addEventListener("click", () => {
      pause();
      if (state.dsa.currentStep < state.dsa.frames.length - 1) {
        renderDSAStep(state.dsa.currentStep + 1);
      }
    });

    els.dsaBtnPrev.addEventListener("click", () => {
      pause();
      if (state.dsa.currentStep > 0) {
        renderDSAStep(state.dsa.currentStep - 1);
      }
    });

    els.dsaBtnFirst.addEventListener("click", () => {
      pause();
      renderDSAStep(0);
    });

    els.dsaBtnLast.addEventListener("click", () => {
      pause();
      renderDSAStep(state.dsa.frames.length - 1);
    });

    els.dsaBtnReset.addEventListener("click", () => {
      pause();
      renderDSAStep(0);
    });

    els.dsaStepSlider.addEventListener("input", (e) => {
      pause();
      renderDSAStep(parseInt(e.target.value) - 1);
    });

    els.dsaSpeed.addEventListener("change", (e) => {
      state.dsa.speed = parseInt(e.target.value);
      if (state.dsa.isPlaying) {
        pause();
        play();
      }
    });

    els.dsaAlgorithmSelect.addEventListener("change", (e) => {
      const val = e.target.value;
      if (val.startsWith("bst")) {
        els.dsaInputField.value = "50, 30, 70, 20, 40, 60, 80";
        els.dsaInputHelper.textContent = "Tree node values (first becomes root).";
      } else if (val.startsWith("graph")) {
        els.dsaInputField.value = "A";
        els.dsaInputHelper.textContent = "Start node label (A, B, C, D, E, F).";
      } else if (val === "binary_search") {
        els.dsaInputField.value = "23";
        els.dsaInputHelper.textContent = "Search target value (in sorted array [2, 5, 8, ...]).";
      } else if (val === "fibonacci") {
        els.dsaInputField.value = "4";
        els.dsaInputHelper.textContent = "Enter integer n for fib(n) recursion.";
      } else {
        els.dsaInputField.value = "64, 34, 25, 12, 22, 11, 90";
        els.dsaInputHelper.textContent = "Enter numbers separated by commas.";
      }
    });
  }

  // ==================== TAB 3: OOP ARCHITECTURE LOGIC ====================

  async function generateOOP() {
    const code = els.oopCode.value;
    if (!code.trim()) {
      showToast("Please enter class code.");
      return;
    }

    try {
      const res = await fetch("/api/oop", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code, language: state.language })
      });

      const data = await res.json();
      if (!data.success) {
        showToast(data.error ? data.error.message : "OOP analysis failed.");
        return;
      }

      state.oop.data = data.oop_data;
      state.oop.mermaid = data.mermaid;
      state.oop.dot = data.dot;

      els.oopClassCount.textContent = `${data.oop_data.total_classes} classes`;

      renderUMLClassDiagram(data.oop_data);
      renderOOPRelationships(data.oop_data);

      showToast(`Analyzed ${data.oop_data.total_classes} ${state.language.toUpperCase()} classes successfully.`);

    } catch (err) {
      console.error("OOP error:", err);
      showToast("Failed to generate OOP diagram.");
    }
  }

  function renderUMLClassDiagram(oopData) {
    const classes = oopData.classes || [];
    if (classes.length === 0) {
      els.oopDiagramContainer.innerHTML = '<div class="empty-state">No classes found in provided code.</div>';
      return;
    }

    const boxW = 220;
    const spacingX = 280;
    let totalW = classes.length * spacingX + 60;
    let maxH = 400;

    let svg = `<svg width="${Math.max(800, totalW)}" height="${maxH}" xmlns="http://www.w3.org/2000/svg" style="overflow:visible;">`;
    svg += `<defs>
      <marker id="uml-inherit" viewBox="0 0 12 12" refX="11" refY="6" markerWidth="8" markerHeight="8" orient="auto-start-reverse">
        <polygon points="0,0 12,6 0,12" fill="#ffffff" stroke="#3b82f6" stroke-width="2" />
      </marker>
    </defs>`;

    classes.forEach((c, idx) => {
      const x = 50 + idx * spacingX;
      const y = 50;
      const attrs = (c.class_attributes || []).concat(c.instance_attributes || []);
      const methods = c.methods || [];

      const headerH = c.is_abstract ? 45 : 36;
      const attrH = Math.max(28, attrs.length * 20 + 12);
      const methH = Math.max(28, methods.length * 20 + 12);
      const totalBoxH = headerH + attrH + methH;

      svg += `<rect x="${x}" y="${y}" width="${boxW}" height="${totalBoxH}" rx="8" fill="#1e293b" stroke="#3b82f6" stroke-width="2" />`;

      svg += `<rect x="${x}" y="${y}" width="${boxW}" height="${headerH}" rx="8 8 0 0" fill="#2563eb" />`;
      if (c.is_abstract) {
        svg += `<text x="${x + boxW/2}" y="${y + 16}" text-anchor="middle" fill="#93c5fd" font-size="10" font-style="italic">&lt;&lt;abstract&gt;&gt;</text>`;
        svg += `<text x="${x + boxW/2}" y="${y + 34}" text-anchor="middle" fill="#ffffff" font-weight="700" font-size="14">${c.name}</text>`;
      } else {
        svg += `<text x="${x + boxW/2}" y="${y + 24}" text-anchor="middle" fill="#ffffff" font-weight="700" font-size="14">${c.name}</text>`;
      }

      svg += `<line x1="${x}" y1="${y + headerH}" x2="${x + boxW}" y2="${y + headerH}" stroke="#334155" stroke-width="1" />`;
      let curY = y + headerH + 18;
      if (attrs.length === 0) {
        svg += `<text x="${x + 12}" y="${curY}" fill="#64748b" font-size="11" font-style="italic">(no attributes)</text>`;
      } else {
        attrs.forEach(a => {
          const sign = a.visibility === "public" ? "+" : (a.visibility === "protected" ? "#" : "-");
          svg += `<text x="${x + 12}" y="${curY}" fill="#e2e8f0" font-size="11" font-family="monospace">${sign} ${a.name}</text>`;
          curY += 20;
        });
      }

      svg += `<line x1="${x}" y1="${y + headerH + attrH}" x2="${x + boxW}" y2="${y + headerH + attrH}" stroke="#334155" stroke-width="1" />`;
      curY = y + headerH + attrH + 18;
      if (methods.length === 0) {
        svg += `<text x="${x + 12}" y="${curY}" fill="#64748b" font-size="11" font-style="italic">(no methods)</text>`;
      } else {
        methods.forEach(m => {
          const sign = m.visibility === "public" ? "+" : (m.visibility === "protected" ? "#" : "-");
          const overrideTag = m.is_override ? " *" : "";
          svg += `<text x="${x + 12}" y="${curY}" fill="#93c5fd" font-size="11" font-family="monospace">${sign} ${m.name}()${overrideTag}</text>`;
          curY += 20;
        });
      }
    });

    svg += '</svg>';
    els.oopDiagramContainer.innerHTML = svg;
  }

  function renderOOPRelationships(oopData) {
    const rels = oopData.relationships || [];
    if (rels.length === 0) {
      els.oopRelationshipList.innerHTML = '<span class="empty-hint">No class relationships detected.</span>';
    } else {
      let html = "";
      rels.forEach(r => {
        html += `<div class="rel-item">
          <div>
            <strong>${r.source}</strong> &rarr; <strong>${r.target}</strong>
            <div style="font-size:0.7rem; color:#94a3b8;">${r.details}</div>
          </div>
          <span class="rel-tag ${r.type}">${r.type} (${r.confidence})</span>
        </div>`;
      });
      els.oopRelationshipList.innerHTML = html;
    }

    const flows = oopData.call_flows || [];
    if (flows.length === 0) {
      els.oopCallFlows.innerHTML = '<span class="empty-hint">No top-level method calls detected.</span>';
    } else {
      let fHtml = "";
      flows.forEach(f => {
        fHtml += `<div class="call-item">
          <div>${f.call}</div>
          <div style="font-size:0.7rem; color:#94a3b8;">${f.description}</div>
        </div>`;
      });
      els.oopCallFlows.innerHTML = fHtml;
    }
  }

  // ==================== INITIALIZATION & SAMPLES ====================

  function initSampleSelectors() {
    els.flowchartSampleSelect.addEventListener("change", (e) => {
      const key = e.target.value;
      const lang = state.language;
      if (state.samples && state.samples[lang] && state.samples[lang].flowchart && state.samples[lang].flowchart[key]) {
        els.flowchartCode.value = state.samples[lang].flowchart[key].code;
        generateFlowchart();
      }
    });

    els.tracebackSampleSelect.addEventListener("change", (e) => {
      const key = e.target.value;
      const lang = state.language;
      if (state.samples && state.samples[lang] && state.samples[lang].traceback && state.samples[lang].traceback[key]) {
        const item = state.samples[lang].traceback[key];
        els.flowchartCode.value = item.code;
        els.tracebackInput.value = item.traceback;
        generateFlowchart().then(() => {
          mapTraceback();
        });
      }
    });

    els.oopSampleSelect.addEventListener("change", (e) => {
      const key = e.target.value;
      const lang = state.language;
      if (state.samples && state.samples[lang] && state.samples[lang].oop && state.samples[lang].oop[key]) {
        els.oopCode.value = state.samples[lang].oop[key].code;
        generateOOP();
      }
    });
  }

  function initEventListeners() {
    els.btnGenerateFlowchart.addEventListener("click", () => generateFlowchart());
    els.btnToggleDebug.addEventListener("click", () => {
      els.debugDrawer.style.display = els.debugDrawer.style.display === "none" ? "flex" : "none";
    });
    els.btnCloseDebug.addEventListener("click", () => {
      els.debugDrawer.style.display = "none";
    });
    els.btnMapTraceback.addEventListener("click", mapTraceback);
    els.btnClearHighlight.addEventListener("click", clearErrorHighlight);
    els.btnCloseInspector.addEventListener("click", () => {
      els.nodeInspector.classList.remove("open");
    });

    els.btnRunDsa.addEventListener("click", runDSASimulation);
    els.btnGenerateOop.addEventListener("click", generateOOP);

    if (els.btnTraceCode) els.btnTraceCode.addEventListener("click", traceAndVisualize);

    els.btnCopyOopMermaid.addEventListener("click", () => {
      if (state.oop.mermaid) copyToClipboard(state.oop.mermaid, "Copied Mermaid classDiagram!");
    });
    els.btnCopyOopDot.addEventListener("click", () => {
      if (state.oop.dot) copyToClipboard(state.oop.dot, "Copied Graphviz DOT UML diagram!");
    });
  }

  async function initApp() {
    initTheme();
    initTabs();
    initPanZoom();
    initNodeSearch();
    initExports();
    initDSAPlayback();
    initEventListeners();
    initSampleSelectors();
    initLanguageSelector();

    await loadSamples();

    if (els.flowchartCode.value.trim()) {
      generateFlowchart();
    }
  }

  document.addEventListener("DOMContentLoaded", initApp);
})();

// ==================== TAB 4: CODE VISUALIZER ENGINE ====================
// Appended as a self-contained IIFE extension
(function() {
  "use strict";

  // ── Multi-Language Sample codes ──────────────────────────────────────
  const VIZ_SAMPLES = {
    python: {
      bubble: `# Bubble Sort\narray = [64, 34, 25, 12, 22, 11, 90]\nn = len(array)\nfor i in range(n):\n    for j in range(0, n - i - 1):\n        if array[j] > array[j + 1]:\n            array[j], array[j + 1] = array[j + 1], array[j]\nprint("Sorted:", array)`,
      selection: `# Selection Sort\narray = [29, 10, 14, 37, 13]\nn = len(array)\nfor i in range(n):\n    min_idx = i\n    for j in range(i + 1, n):\n        if array[j] < array[min_idx]:\n            min_idx = j\n    array[i], array[min_idx] = array[min_idx], array[i]\nprint("Sorted:", array)`,
      insertion: `# Insertion Sort\narray = [12, 11, 13, 5, 6]\nfor i in range(1, len(array)):\n    key = array[i]\n    j = i - 1\n    while j >= 0 and array[j] > key:\n        array[j + 1] = array[j]\n        j -= 1\n    array[j + 1] = key\nprint("Sorted:", array)`,
      binary_search: `# Binary Search\narray = [2, 5, 8, 12, 16, 23, 38, 56, 72, 91]\ntarget = 23\nleft = 0\nright = len(array) - 1\nresult = -1\nwhile left <= right:\n    mid = (left + right) // 2\n    if array[mid] == target:\n        result = mid\n        break\n    elif array[mid] < target:\n        left = mid + 1\n    else:\n        right = mid - 1\nprint("Found at:", result)`,
      linear_search: `# Linear Search\narray = [10, 20, 80, 30, 60, 50, 110, 100]\ntarget = 80\nresult = -1\nfor i in range(len(array)):\n    if array[i] == target:\n        result = i\n        break\nprint("Found at:", result)`,
      fibonacci: `# Fibonacci Recursion\ndef fib(n):\n    if n <= 1:\n        return n\n    return fib(n - 1) + fib(n - 2)\nresult = fib(6)\nprint("fib(6) =", result)`,
      factorial: `# Factorial\ndef factorial(n):\n    if n == 0:\n        return 1\n    return n * factorial(n - 1)\nresult = factorial(5)\nprint("5! =", result)`,
      two_pointers: `# Two Pointers\narray = [1, 2, 3, 4, 6, 8, 9, 14, 15]\ntarget = 13\nleft = 0\nright = len(array) - 1\nfound = False\nwhile left < right:\n    s = array[left] + array[right]\n    if s == target:\n        found = True\n        break\n    elif s < target:\n        left += 1\n    else:\n        right -= 1\nprint("Found:", found)`,
      matrix_sum: `# Matrix Row Sums\nmatrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]\nrow_sums = []\nfor i in range(len(matrix)):\n    total = 0\n    for j in range(len(matrix[i])):\n        total += matrix[i][j]\n    row_sums.append(total)\nprint("Row sums:", row_sums)`
    },
    java: {
      prime_analyzer: `public class PrimeAnalyzer {\\n\\n    public static boolean isPrime(int n) {\\n        if (n <= 1) {\\n            return false;\\n        }\\n\\n        for (int i = 2; i * i <= n; i++) {\\n            if (n % i == 0) {\\n                return false;\\n            }\\n        }\\n\\n        return true;\\n    }\\n\\n    public static void main(String[] args) {\\n\\n        int[] numbers = {2, 7, 10, 13, 15, 17, 20, 23};\\n        int primeCount = 0;\\n        int evenCount = 0;\\n        int oddCount = 0;\\n\\n        for (int i = 0; i < numbers.length; i++) {\\n\\n            int n = numbers[i];\\n\\n            if (n <= 0) {\\n                System.out.println("Skipping invalid number: " + n);\\n                continue;\\n            }\\n\\n            if (n % 2 == 0) {\\n                evenCount++;\\n\\n                if (n == 2) {\\n                    primeCount++;\\n                    System.out.println(n + " is the only even prime");\\n                } else {\\n                    System.out.println(n + " is even");\\n                }\\n            } else {\\n                oddCount++;\\n                if (isPrime(n)) {\\n                    primeCount++;\\n                    System.out.println(n + " is a prime number");\\n                } else {\\n                    System.out.println(n + " is odd and composite");\\n                }\\n            }\\n        }\\n\\n        System.out.println("Prime count: " + primeCount);\\n        System.out.println("Even count: " + evenCount);\\n        System.out.println("Odd count: " + oddCount);\\n\\n        if (primeCount == 0) {\\n            System.out.println("No prime numbers found");\\n        } else if (primeCount < 3) {\\n            System.out.println("Few prime numbers found");\\n        } else {\\n            System.out.println("Multiple prime numbers found");\\n        }\\n\\n        System.out.println("Analysis complete");\\n    }\\n}`,
      bubble: `public class BubbleSort {\\n    public static void main(String[] args) {\\n        int[] arr = {64, 34, 25, 12, 22, 11, 90};\\n        int n = arr.length;\\n        for (int i = 0; i < n - 1; i++) {\\n            for (int j = 0; j < n - i - 1; j++) {\\n                if (arr[j] > arr[j + 1]) {\\n                    int temp = arr[j];\\n                    arr[j] = arr[j + 1];\\n                    arr[j + 1] = temp;\\n                }\\n            }\\n        }\\n        System.out.println("Sorted array complete");\\n    }\\n}`,
      binary_search: `public class BinarySearch {\\n    public static void main(String[] args) {\\n        int[] arr = {2, 5, 8, 12, 16, 23, 38, 56, 72, 91};\\n        int target = 23;\\n        int low = 0;\\n        int high = arr.length - 1;\\n        int found = -1;\\n        while (low <= high) {\\n            int mid = (low + high) / 2;\\n            if (arr[mid] == target) {\\n                found = mid;\\n                break;\\n            } else if (arr[mid] < target) {\\n                low = mid + 1;\\n            } else {\\n                high = mid - 1;\\n            }\\n        }\\n        System.out.println("Found target at index: " + found);\\n    }\\n}`
    },
    javascript: {
      bubble: `function bubbleSort() {\\n    let arr = [64, 34, 25, 12, 22, 11, 90];\\n    let n = arr.length;\\n    for (let i = 0; i < n; i++) {\\n        for (let j = 0; j < n - i - 1; j++) {\\n            if (arr[j] > arr[j + 1]) {\\n                let temp = arr[j];\\n                arr[j] = arr[j + 1];\\n                arr[j + 1] = temp;\\n            }\\n        }\\n    }\\n    console.log("Sorted array: " + arr);\\n}\\nbubbleSort();`,
      binary_search: `function binarySearch() {\\n    let arr = [2, 5, 8, 12, 16, 23, 38, 56, 72, 91];\\n    let target = 23;\\n    let low = 0;\\n    let high = arr.length - 1;\\n    let found = -1;\\n    while (low <= high) {\\n        let mid = Math.floor((low + high) / 2);\\n        if (arr[mid] === target) {\\n            found = mid;\\n            break;\\n        } else if (arr[mid] < target) {\\n            low = mid + 1;\\n        } else {\\n            high = mid - 1;\\n        }\\n    }\\n    console.log("Found at: " + found);\\n}\\nbinarySearch();`
    },
    cpp: {
      bubble: `#include <iostream>\\nusing namespace std;\\nint main() {\\n    int arr[] = {64, 34, 25, 12, 22, 11, 90};\\n    int n = 7;\\n    for (int i = 0; i < n - 1; i++) {\\n        for (int j = 0; j < n - i - 1; j++) {\\n            if (arr[j] > arr[j + 1]) {\\n                int temp = arr[j];\\n                arr[j] = arr[j + 1];\\n                arr[j + 1] = temp;\\n            }\\n        }\\n    }\\n    cout << "Sorted completed" << endl;\\n    return 0;\\n}`,
      binary_search: `#include <iostream>\\nusing namespace std;\\nint main() {\\n    int arr[] = {2, 5, 8, 12, 16, 23, 38, 56, 72, 91};\\n    int target = 23;\\n    int low = 0;\\n    int high = 9;\\n    int found = -1;\\n    while (low <= high) {\\n        int mid = (low + high) / 2;\\n        if (arr[mid] == target) {\\n            found = mid;\\n            break;\\n        } else if (arr[mid] < target) {\\n            low = mid + 1;\\n        } else {\\n            high = mid - 1;\\n        }\\n    }\\n    cout << "Found: " << found << endl;\\n    return 0;\\n}`
    }
  };

  function updateVizLanguage(lang) {
    const titles = {
      python: "Python Code",
      java: "Java Code",
      javascript: "JavaScript Code",
      cpp: "C / C++ Code"
    };
    const placeholders = {
      python: "# Paste your Python code here...",
      java: "// Paste your Java code here...",
      javascript: "// Paste your JavaScript code here...",
      cpp: "// Paste your C / C++ code here..."
    };
    const titleEl = ge("viz-lang-title");
    if (titleEl) titleEl.textContent = titles[lang] || `${lang.toUpperCase()} Code`;
    const codeEl = ge("viz-code");
    if (codeEl) codeEl.placeholder = placeholders[lang] || "// Paste your code here...";

    const selectEl = ge("viz-sample-select");
    if (selectEl) {
      selectEl.innerHTML = '<option value="">Load Sample...</option>';
      const langSamples = VIZ_SAMPLES[lang] || VIZ_SAMPLES.python;
      Object.keys(langSamples).forEach(key => {
        const opt = document.createElement("option");
        opt.value = key;
        opt.textContent = key.split("_").map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(" ");
        selectEl.appendChild(opt);
      });
    }

    const emptyDesc = ge("viz-empty-desc");
    if (emptyDesc) {
      const lName = (titles[lang] || "Source").replace(" Code", "");
      emptyDesc.innerHTML = `Paste your ${lName} code and click <strong>"Trace &amp; Visualize"</strong> to see a live animated execution trace of your exact code.`;
    }

    const errBanner = ge("viz-error-banner");
    if (errBanner) { errBanner.style.display = "none"; errBanner.textContent = ""; }
  }
  window.updateVizLanguage = updateVizLanguage;

  const vizState = window._code2flowVizState = {
    frames: [],
    currentStep: 0,
    isPlaying: false,
    playTimer: null,
    speed: 700,
    structures: []
  };

  function ge(id) { return document.getElementById(id); }

  function _esc(s) {
    if (!s) return "";
    return String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
  }

  function _valStr(info) {
    if (!info) return "?";
    const v = info.value;
    if (Array.isArray(v)) return `[${v.join(", ")}]`;
    if (v === null || v === undefined) return "None";
    return String(v);
  }

  function updateVizLineNumbers(code, activeLine) {
    const el = ge("viz-line-numbers");
    if (!el) return;
    const lines = code.split("\n");
    let html = "";
    lines.forEach((_, i) => {
      const n = i + 1;
      html += n === activeLine
        ? `<div class="ln-active">${n}</div>`
        : `<div>${n}</div>`;
    });
    el.innerHTML = html;
    // scroll to active line
    if (activeLine > 0) {
      const lineH = 1.7 * 12.8; // approx 1rem * 1.7
      el.scrollTop = (activeLine - 3) * lineH;
    }
  }
  window.updateVizLineNumbers = updateVizLineNumbers;

  function _pickMainArray(vars) {
    const candidates = Object.entries(vars).filter(([, info]) =>
      info.type === "array" && Array.isArray(info.value) && info.value.length > 0
    );
    if (!candidates.length) return null;
    const preferred = ["array", "arr", "nums", "data", "a", "b", "lst"];
    for (const p of preferred) {
      const f = candidates.find(([k]) => k === p);
      if (f) return f;
    }
    return candidates[0];
  }

  function buildNarration(frame) {
    const scope = (frame.scope && frame.scope !== "<module>") ? `[${frame.scope}] ` : "";
    const swaps = frame.highlight && frame.highlight.swaps;
    if (swaps && swaps.length > 0) {
      const s = swaps[0];
      return `${scope}SWAP positions ${s.i} ↔ ${s.j}: ${frame.line ? frame.line.trim() : ""}`;
    }
    const changed = frame.changed || [];
    if (changed.length > 0) {
      return `${scope}Changed: ${changed.join(", ")} → ${frame.line ? frame.line.trim() : ""}`;
    }
    return `${scope}Line ${frame.lineno}: ${frame.line ? frame.line.trim() : ""}`;
  }

  function renderVizVars(vars, changed) {
    const el = ge("viz-var-grid");
    if (!el) return;
    const entries = Object.entries(vars);
    if (!entries.length) { el.innerHTML = '<span style="color:#64748b;font-size:0.8rem;">No variables yet.</span>'; return; }
    el.innerHTML = entries.map(([k, info]) => {
      const isChanged = changed && changed.includes(k);
      const cls = isChanged ? "viz-var-chip changed" : "viz-var-chip";
      const val = _valStr(info);
      const displayVal = val.length > 35 ? val.slice(0, 35) + "\u2026" : val;
      return `<div class="${cls}"><span class="viz-var-name">${_esc(k)}</span><span class="viz-var-val"> = ${_esc(displayVal)}</span></div>`;
    }).join("");
  }

  function renderArrayCanvas(varName, arr, indices, swaps) {
    if (!arr || !arr.length) return "";
    const maxVal = Math.max(...arr.map(v => Math.abs(Number(v)||0)), 1);
    const swapSet = new Set((swaps||[]).flatMap(s => [s.i, s.j]));
    const ptrMap = {};
    Object.entries(indices||{}).forEach(([pname, pval]) => {
      if (typeof pval === "number" && pval >= 0 && pval < arr.length) {
        if (!ptrMap[pval]) ptrMap[pval] = [];
        ptrMap[pval].push(pname);
      }
    });
    let html = `<div class="viz-label">${_esc(varName)} [ ${arr.length} elements ]</div><div class="viz-array-container">`;
    arr.forEach((val, i) => {
      const barH = Math.max(28, Math.min(200, (Math.abs(Number(val)||0) / maxVal) * 180));
      let sc = "";
      if (swapSet.has(i)) sc = "state-swapping";
      else if (ptrMap[i]) {
        const ptrs = ptrMap[i];
        if (ptrs.includes("mid")||ptrs.includes("m")) sc = "state-searching";
        else sc = "state-comparing";
      }
      const ptrLabel = ptrMap[i] ? ptrMap[i].join(",") : "";
      html += `<div class="viz-array-bar-col">
        <div class="viz-bar ${sc}" style="height:${barH}px;">${_esc(String(val))}</div>
        <div class="viz-bar-index">[${i}]</div>
        ${ptrLabel ? `<div style="font-size:.68rem;color:#f59e0b;font-weight:700;">${_esc(ptrLabel)}</div>` : ""}
      </div>`;
    });
    html += "</div>";
    return html;
  }

  function renderMatrixCanvas(varName, matrix, vars) {
    if (!matrix||!matrix.length) return "";
    const activeI = vars.i ? Number(vars.i.value) : -1;
    const activeJ = vars.j ? Number(vars.j.value) : -1;
    let html = `<div class="viz-label">${_esc(varName)} [ ${matrix.length}×${(matrix[0]||[]).length} ]</div><div class="viz-matrix-container">`;
    matrix.forEach((row, ri) => {
      html += `<div class="viz-matrix-row">`;
      (row||[]).forEach((cell, ci) => {
        const isActive = ri===activeI && ci===activeJ;
        html += `<div class="viz-matrix-cell ${isActive?"active":""}}">${_esc(String(cell))}</div>`;
      });
      html += `</div>`;
    });
    html += `</div>`;
    return html;
  }

  function renderCallStackCanvas(callStack) {
    if (!callStack||callStack.length<=1) return "";
    let html = `<div class="viz-label">Call Stack (${callStack.length} frames)</div><div class="viz-callstack-container">`;
    [...callStack].reverse().forEach((fn, idx) => {
      html += `<div class="viz-callstack-frame ${idx===0?"current-frame":""}">
        <span>${_esc(fn)}()</span>
        <span style="font-size:.72rem;color:#94a3b8;">#${callStack.length-1-idx}</span>
      </div>`;
    });
    html += `</div>`;
    return html;
  }

  function renderPrimitivesCanvas(vars, skip1, skip2) {
    const cards = Object.entries(vars).filter(([k, info]) => k!==skip1 && k!==skip2 && info.type==="primitive");
    if (!cards.length) return "";
    let html = `<div style="display:flex;flex-wrap:wrap;gap:.6rem;justify-content:center;">`;
    cards.forEach(([k, info]) => {
      html += `<div style="background:var(--bg-surface);border:1.5px solid var(--border-medium);border-radius:8px;padding:.5rem 1rem;font-family:var(--font-mono);font-size:.85rem;">
        <span style="color:var(--accent-primary);font-weight:700;">${_esc(k)}</span>
        <span style="color:var(--text-secondary);"> = </span>
        <span style="color:var(--text-primary);font-weight:600;">${_esc(String(info.value))}</span>
      </div>`;
    });
    html += `</div>`;
    return html;
  }

  function renderVizCanvas(frame) {
    const vars = frame.variables || {};
    const indices = (frame.highlight&&frame.highlight.indices) || {};
    const swaps = (frame.highlight&&frame.highlight.swaps) || [];

    const mainArr = _pickMainArray(vars);
    const matrixEntry = Object.entries(vars).find(([,info]) =>
      info.type==="list" && Array.isArray(info.value) && info.value.length>0 && Array.isArray(info.value[0])
    );
    const callStack = frame.call_stack || [];

    let html = "";
    if (matrixEntry) {
      html += renderMatrixCanvas(matrixEntry[0], matrixEntry[1].value, vars);
    } else if (mainArr) {
      html += renderArrayCanvas(mainArr[0], mainArr[1].value, indices, swaps);
    }
    html += renderCallStackCanvas(callStack);
    html += renderPrimitivesCanvas(vars, mainArr?mainArr[0]:null, matrixEntry?matrixEntry[0]:null);

    const emptyState = ge("viz-empty-state");
    if (emptyState) emptyState.style.display = "none";

    const canvas = ge("viz-canvas");
    if (!canvas) return;
    let inner = canvas.querySelector(".viz-canvas-inner");
    if (!inner) {
      inner = document.createElement("div");
      inner.className = "viz-canvas-inner";
      inner.style.cssText = "display:flex;flex-direction:column;align-items:center;gap:1.5rem;width:100%;";
      canvas.appendChild(inner);
    }
    inner.innerHTML = html;
  }

  function doRenderStep(idx) {
    if (!vizState.frames.length) return;
    const frame = vizState.frames[idx];
    if (!frame) return;
    vizState.currentStep = idx;

    const stepEl = ge("viz-step-num");
    if (stepEl) stepEl.textContent = frame.step;
    const sliderEl = ge("viz-step-slider");
    if (sliderEl) sliderEl.value = frame.step;
    const varStep = ge("viz-var-step");
    if (varStep) varStep.textContent = frame.step;

    const narEl = ge("viz-narration");
    if (narEl) { narEl.textContent = buildNarration(frame); narEl.classList.add("active"); }

    updateVizLineNumbers(ge("viz-code")?ge("viz-code").value:"", frame.lineno);
    renderVizVars(frame.variables, frame.changed);
    renderVizCanvas(frame);
  }

  function vizPauseLocal() {
    vizState.isPlaying = false;
    const pi = ge("viz-play-icon");
    if (pi) pi.innerHTML = "&#9654; Play";
    if (vizState.playTimer) { clearInterval(vizState.playTimer); vizState.playTimer = null; }
  }

  function vizPlayLocal() {
    if (vizState.currentStep >= vizState.frames.length - 1) vizState.currentStep = 0;
    vizState.isPlaying = true;
    const pi = ge("viz-play-icon");
    if (pi) pi.innerHTML = "&#10074;&#10074; Pause";
    vizState.playTimer = setInterval(() => {
      if (vizState.currentStep < vizState.frames.length - 1) {
        doRenderStep(vizState.currentStep + 1);
      } else {
        vizPauseLocal();
      }
    }, vizState.speed);
  }

  async function traceAndVisualize() {
    const codeEl = ge("viz-code");
    const statusEl = ge("viz-status");
    const errBanner = ge("viz-error-banner");
    if (errBanner) { errBanner.style.display = "none"; errBanner.textContent = ""; }

    if (!codeEl || !codeEl.value.trim()) {
      if (errBanner) {
        errBanner.textContent = "Please paste code to visualize.";
        errBanner.style.display = "block";
      }
      return;
    }
    vizPauseLocal();
    if (statusEl) { statusEl.textContent = "Tracing..."; statusEl.className = "syntax-status"; }

    const currentLang = (window._code2flowState && window._code2flowState.language) || "auto";

    try {
      const res = await fetch("/api/visualize", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code: codeEl.value, language: currentLang })
      });
      const data = await res.json();
      if (!data.success && (!data.frames || !data.frames.length)) {
        if (statusEl) { statusEl.textContent = "Error"; statusEl.className = "syntax-status badge-err"; }
        if (errBanner) {
          const errMsg = (data.error && data.error.message) ? data.error.message : "Execution or parsing error occurred.";
          errBanner.textContent = errMsg;
          errBanner.style.display = "block";
        }
        return;
      }

      if (data.language) {
        const titles = {
          python: "Python Code",
          java: "Java Code",
          javascript: "JavaScript Code",
          cpp: "C / C++ Code"
        };
        const titleEl = ge("viz-lang-title");
        if (titleEl) titleEl.textContent = titles[data.language] || `${data.language.toUpperCase()} Code`;
      }

      if (data.error) {
        console.warn("Runtime:", data.error.message);
      }
      vizState.frames = data.frames || [];
      vizState.structures = data.detected_structures || [];
      vizState.currentStep = 0;
      if (statusEl) { statusEl.textContent = `${data.total_steps} steps`; statusEl.className = "syntax-status badge-ok"; }

      // Output
      const outBox = ge("viz-output-box");
      const outTxt = ge("viz-output-text");
      if (data.stdout && data.stdout.trim()) {
        if (outBox) outBox.style.display = "block";
        if (outTxt) outTxt.textContent = data.stdout;
      } else {
        if (outBox) outBox.style.display = "none";
      }

      const sliderEl = ge("viz-step-slider");
      if (sliderEl) { sliderEl.max = data.total_steps; sliderEl.value = 1; }
      const totalEl = ge("viz-total-steps");
      if (totalEl) totalEl.textContent = data.total_steps;
      const vpBar = ge("viz-playback-bar");
      if (vpBar) vpBar.style.display = "flex";
      const vpanel = ge("viz-var-panel");
      if (vpanel) vpanel.style.display = "block";

      updateVizLineNumbers(codeEl.value, 1);
      doRenderStep(0);
    } catch(e) {
      console.error(e);
      if (statusEl) { statusEl.textContent = "Failed"; statusEl.className = "syntax-status badge-err"; }
      if (errBanner) {
        errBanner.textContent = "Server connection error: " + e.message;
        errBanner.style.display = "block";
      }
    }
  }

  function initVizTab() {
    const traceBtn = ge("btn-trace-code");
    if (traceBtn) traceBtn.addEventListener("click", traceAndVisualize);

    const clearBtn = ge("btn-viz-clear");
    if (clearBtn) clearBtn.addEventListener("click", () => {
      const c = ge("viz-code");
      if (c) c.value = "";
      vizPauseLocal();
      vizState.frames = [];
      const emptyState = ge("viz-empty-state");
      if (emptyState) emptyState.style.display = "flex";
      const inner = ge("viz-canvas") ? ge("viz-canvas").querySelector(".viz-canvas-inner") : null;
      if (inner) inner.remove();
      const vpBar = ge("viz-playback-bar"); if (vpBar) vpBar.style.display = "none";
      const vpanel = ge("viz-var-panel"); if (vpanel) vpanel.style.display = "none";
      const outBox = ge("viz-output-box"); if (outBox) outBox.style.display = "none";
      const errBanner = ge("viz-error-banner"); if (errBanner) errBanner.style.display = "none";
      updateVizLineNumbers("", -1);
      const st = ge("viz-status"); if (st) { st.textContent="Ready"; st.className="syntax-status badge-ok"; }
    });

    const playBtn = ge("viz-btn-play");
    if (playBtn) playBtn.addEventListener("click", () => { if (vizState.isPlaying) vizPauseLocal(); else vizPlayLocal(); });

    const nextBtn = ge("viz-btn-next");
    if (nextBtn) nextBtn.addEventListener("click", () => { vizPauseLocal(); if (vizState.currentStep < vizState.frames.length-1) doRenderStep(vizState.currentStep+1); });

    const prevBtn = ge("viz-btn-prev");
    if (prevBtn) prevBtn.addEventListener("click", () => { vizPauseLocal(); if (vizState.currentStep > 0) doRenderStep(vizState.currentStep-1); });

    const firstBtn = ge("viz-btn-first");
    if (firstBtn) firstBtn.addEventListener("click", () => { vizPauseLocal(); doRenderStep(0); });

    const lastBtn = ge("viz-btn-last");
    if (lastBtn) lastBtn.addEventListener("click", () => { vizPauseLocal(); doRenderStep(vizState.frames.length-1); });

    const slider = ge("viz-step-slider");
    if (slider) slider.addEventListener("input", e => { vizPauseLocal(); doRenderStep(parseInt(e.target.value)-1); });

    const speedSel = ge("viz-speed");
    if (speedSel) speedSel.addEventListener("change", e => {
      vizState.speed = parseInt(e.target.value);
      if (vizState.isPlaying) { vizPauseLocal(); vizPlayLocal(); }
    });

    const codeEl = ge("viz-code");
    const lnEl = ge("viz-line-numbers");
    if (codeEl && lnEl) {
      codeEl.addEventListener("scroll", () => { lnEl.scrollTop = codeEl.scrollTop; });
      codeEl.addEventListener("input", () => updateVizLineNumbers(codeEl.value, -1));
    }

    const sampleSel = ge("viz-sample-select");
    if (sampleSel) sampleSel.addEventListener("change", e => {
      const key = e.target.value;
      const currentLang = (window._code2flowState && window._code2flowState.language) || "python";
      const langSamples = VIZ_SAMPLES[currentLang] || VIZ_SAMPLES.python;
      if (key && langSamples[key]) {
        const c = ge("viz-code"); if (c) { c.value = langSamples[key]; updateVizLineNumbers(langSamples[key], -1); }
        vizPauseLocal();
        vizState.frames = [];
        const emptyState = ge("viz-empty-state"); if (emptyState) emptyState.style.display = "flex";
        const inner = ge("viz-canvas") ? ge("viz-canvas").querySelector(".viz-canvas-inner") : null;
        if (inner) inner.remove();
        const vpBar = ge("viz-playback-bar"); if (vpBar) vpBar.style.display = "none";
        const vpanel = ge("viz-var-panel"); if (vpanel) vpanel.style.display = "none";
        const outBox = ge("viz-output-box"); if (outBox) outBox.style.display = "none";
        const errBanner = ge("viz-error-banner"); if (errBanner) errBanner.style.display = "none";
        const st = ge("viz-status"); if (st) { st.textContent="Ready"; st.className="syntax-status badge-ok"; }
      }
    });

    // Initialize visualizer with current language if already selected
    const initialLang = (window._code2flowState && window._code2flowState.language) || "python";
    updateVizLanguage(initialLang);

    // Pre-populate if empty
    if (codeEl && !codeEl.value.trim()) {
      const defaultCode = (VIZ_SAMPLES[initialLang] && VIZ_SAMPLES[initialLang].bubble) || VIZ_SAMPLES.python.bubble;
      codeEl.value = defaultCode;
      updateVizLineNumbers(defaultCode, -1);
    }
  }

  document.addEventListener("DOMContentLoaded", initVizTab);
})();
