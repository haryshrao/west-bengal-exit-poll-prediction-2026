document.addEventListener('DOMContentLoaded', () => {
    const navLinks = document.querySelectorAll('.nav-link');
    const views = document.querySelectorAll('.dashboard-view');
    const pipelineStatusList = document.getElementById('pipeline-status-list');

    // Pipeline status configurations for different views
    const pipelineConfigs = {
        'view-overview': `
            <li class="flex items-center gap-2 text-on-surface-variant opacity-50">
                <span class="material-symbols-outlined text-sm" data-icon="radio_button_unchecked">radio_button_unchecked</span>
                <span>System Initialization</span>
            </li>
        `,
        'view-data-manager': `
            <li class="flex items-start gap-4 relative z-10">
                <div class="w-6 h-6 rounded-full bg-slate-800 border border-slate-600 flex items-center justify-center mt-0.5">
                    <span class="font-label-caps text-[10px] text-slate-400">1</span>
                </div>
                <div>
                    <p class="font-body-md text-body-md text-slate-300">Data Ingestion</p>
                    <p class="font-body-sm text-body-sm text-slate-500">Pending</p>
                </div>
            </li>
            <li class="flex items-start gap-4 relative z-10">
                <div class="w-6 h-6 rounded-full bg-slate-900 border border-slate-800 flex items-center justify-center mt-0.5">
                    <span class="font-label-caps text-[10px] text-slate-600">2</span>
                </div>
                <div>
                    <p class="font-body-md text-body-md text-slate-500">Model Calibration</p>
                    <p class="font-body-sm text-body-sm text-slate-600">Pending</p>
                </div>
            </li>
            <li class="flex items-start gap-4 relative z-10">
                <div class="w-6 h-6 rounded-full bg-slate-900 border border-slate-800 flex items-center justify-center mt-0.5">
                    <span class="font-label-caps text-[10px] text-slate-600">3</span>
                </div>
                <div>
                    <p class="font-body-md text-body-md text-slate-500">Forecast Generation</p>
                    <p class="font-body-sm text-body-sm text-slate-600">Pending</p>
                </div>
            </li>
        `,
        'view-statistical-results': `
            <li class="flex items-center gap-2 text-primary">
                <span class="material-symbols-outlined text-green-400 text-sm" data-icon="check_circle">check_circle</span>
                <span class="text-on-surface">1. Statistical Prediction</span>
            </li>
            <li class="flex items-center gap-2 text-on-surface-variant opacity-50">
                <span class="material-symbols-outlined text-sm" data-icon="radio_button_unchecked">radio_button_unchecked</span>
                <span>2. Scenario Analysis</span>
            </li>
            <li class="flex items-center gap-2 text-on-surface-variant opacity-50">
                <span class="material-symbols-outlined text-sm" data-icon="radio_button_unchecked">radio_button_unchecked</span>
                <span>3. Report Generation</span>
            </li>
        `,
        'view-ai-integration': `
            <div class="relative pl-6 space-y-6 before:absolute before:inset-0 before:ml-[11px] before:-translate-x-px md:before:w-0.5 before:w-px before:h-full before:bg-surface-variant">
                <div class="relative z-10">
                    <div class="absolute -left-6 bg-primary-container w-6 h-6 rounded-full flex items-center justify-center border-4 border-surface shadow-sm">
                        <span class="material-symbols-outlined text-[14px] text-on-primary-container" data-weight="fill">check</span>
                    </div>
                    <div class="pl-2">
                        <h4 class="font-label-caps text-label-caps text-on-surface uppercase mb-1">Step 1: Data Ingestion</h4>
                        <p class="font-body-sm text-body-sm text-on-surface-variant">Historical polling & demographic data normalized.</p>
                    </div>
                </div>
                <div class="relative z-10">
                    <div class="absolute -left-6 bg-surface w-6 h-6 rounded-full flex items-center justify-center border-2 border-primary shadow-[0_0_10px_rgba(37,99,235,0.5)]">
                        <span class="w-2 h-2 bg-primary rounded-full animate-pulse"></span>
                    </div>
                    <div class="pl-2">
                        <h4 class="font-label-caps text-label-caps text-primary uppercase mb-1">Step 2: AI Interaction</h4>
                        <p class="font-body-sm text-body-sm text-on-surface">Awaiting structured JSON sentiment payload.</p>
                    </div>
                </div>
                <div class="relative z-10">
                    <div class="absolute -left-6 bg-surface-variant w-6 h-6 rounded-full flex items-center justify-center border-4 border-surface">
                        <span class="w-2 h-2 bg-outline rounded-full"></span>
                    </div>
                    <div class="pl-2 opacity-50">
                        <h4 class="font-label-caps text-label-caps text-on-surface uppercase mb-1">Step 3: Model Calibration</h4>
                        <p class="font-body-sm text-body-sm text-on-surface-variant">Swing adjustment and Monte Carlo simulation.</p>
                    </div>
                </div>
            </div>
        `,
        'view-final-forecast': `
            <div class="flex items-center gap-3 opacity-60">
                <span class="material-symbols-outlined text-green-500" style="font-variation-settings: 'FILL' 1;">check_circle</span>
                <div>
                    <p class="font-body-md text-body-md text-slate-300">Stage 1: Ingestion</p>
                </div>
            </div>
            <div class="flex items-center gap-3 opacity-60">
                <span class="material-symbols-outlined text-green-500" style="font-variation-settings: 'FILL' 1;">check_circle</span>
                <div>
                    <p class="font-body-md text-body-md text-slate-300">Stage 2: Statistical Model</p>
                </div>
            </div>
            <div class="flex items-center gap-3">
                <span class="material-symbols-outlined text-green-500" style="font-variation-settings: 'FILL' 1;">check_circle</span>
                <div>
                    <p class="font-body-md text-body-md text-white font-semibold">Stage 3: AI Augmentation</p>
                    <p class="text-blue-400 font-body-sm text-body-sm">Final Output Ready</p>
                </div>
            </div>
        `
    };

    function switchView(targetId) {
        // Hide all views
        views.forEach(view => {
            view.classList.add('hidden');
        });

        // Remove active class from all links
        navLinks.forEach(link => {
            link.classList.remove('bg-slate-800', 'text-white', 'border-l-4', 'border-blue-600', 'opacity-90', 'scale-[0.99]');
            link.classList.add('text-slate-400', 'hover:text-slate-200', 'hover:bg-slate-800/50', 'border-transparent');
            
            // Adjust icon
            const icon = link.querySelector('.material-symbols-outlined');
            if (icon) {
                icon.removeAttribute('data-weight');
                icon.style.fontVariationSettings = "";
            }
        });

        // Show target view
        const targetView = document.getElementById(targetId);
        if (targetView) {
            targetView.classList.remove('hidden');
        }

        // Add active class to corresponding link
        const targetLink = document.querySelector(`.nav-link[data-target="${targetId}"]`);
        if (targetLink) {
            targetLink.classList.remove('text-slate-400', 'hover:text-slate-200', 'hover:bg-slate-800/50', 'border-transparent');
            targetLink.classList.add('bg-slate-800', 'text-white', 'border-l-4', 'border-blue-600', 'opacity-90', 'scale-[0.99]');
            
            // Adjust icon
            const icon = targetLink.querySelector('.material-symbols-outlined');
            if (icon) {
                icon.setAttribute('data-weight', 'fill');
                icon.style.fontVariationSettings = "'FILL' 1";
            }
        }
        
        // Update pipeline status widget based on view
        if (pipelineStatusList && pipelineConfigs[targetId]) {
             pipelineStatusList.innerHTML = pipelineConfigs[targetId];
             
             // special case formatting for pipeline
             if(targetId === 'view-ai-integration') {
                 pipelineStatusList.classList.remove('flex', 'flex-col', 'gap-4', 'relative', 'before:absolute', 'before:inset-y-2', 'before:left-[11px]', 'before:w-px', 'before:bg-slate-800', 'space-y-3', 'space-y-4');
             } else if (targetId === 'view-final-forecast') {
                 pipelineStatusList.className = 'space-y-4 px-3';
             } else if (targetId === 'view-statistical-results') {
                 pipelineStatusList.className = 'space-y-3 font-body-sm text-body-sm';
             } else if (targetId === 'view-data-manager') {
                 pipelineStatusList.className = 'flex flex-col gap-4 relative before:absolute before:inset-y-2 before:left-[11px] before:w-px before:bg-slate-800';
             }
        }
    }

    // Add click event listeners
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const targetId = link.getAttribute('data-target');
            switchView(targetId);
        });
    });

    // Initial state
    switchView('view-overview');

    // Handle iframe resizing messages
    window.addEventListener('message', (e) => {
        if (e.data && e.data.type === 'resize-iframe') {
            const iframe = document.querySelector('iframe[src="/static/overview.html"]');
            if (iframe) {
                iframe.style.height = (e.data.height + 50) + 'px';
            }
        }
    });

    // ── Exit Poll Selection & Prediction Logic ──────────────────────────────
    const pollSelectBtns = document.querySelectorAll('.poll-select-btn');
    const startPredictionBtn = document.getElementById('start-prediction-btn');
    let selectedDataset = null;

    pollSelectBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            pollSelectBtns.forEach(b => {
                b.classList.remove('selected', 'border-blue-500', 'bg-blue-500/5');
            });
            
            btn.classList.add('selected', 'border-blue-500', 'bg-blue-500/5');
            selectedDataset = btn.getAttribute('data-poll');
            
            if (startPredictionBtn) {
                startPredictionBtn.disabled = false;
                startPredictionBtn.classList.remove('opacity-50', 'cursor-not-allowed', 'bg-surface-variant', 'text-on-surface-variant');
                startPredictionBtn.classList.add('bg-blue-600', 'text-white', 'hover:bg-blue-500', 'shadow-[0_0_15px_rgba(37,99,235,0.3)]', 'cursor-pointer');
            }
        });
    });

    // ── Start Prediction button handler ─────────────────────────────────────
    if (startPredictionBtn) {
        startPredictionBtn.addEventListener('click', async () => {
            if (!selectedDataset) return;

            // Show loading state on button
            const originalHTML = startPredictionBtn.innerHTML;
            startPredictionBtn.disabled = true;
            startPredictionBtn.classList.add('opacity-70', 'cursor-wait');
            startPredictionBtn.innerHTML = `
                <svg class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
                </svg>
                Running Prediction...
            `;

            try {
                const response = await fetch('/api/predict', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ dataset: selectedDataset }),
                });

                if (!response.ok) {
                    const errData = await response.json();
                    throw new Error(errData.detail || 'Prediction failed');
                }

                const data = await response.json();
                renderPredictionResults(data);

                // Update button to success state
                startPredictionBtn.innerHTML = `
                    <span class="material-symbols-outlined" data-icon="check_circle">check_circle</span>
                    Prediction Complete
                `;
                startPredictionBtn.classList.remove('bg-blue-600', 'opacity-70', 'cursor-wait');
                startPredictionBtn.classList.add('bg-green-600');

            } catch (err) {
                console.error('Prediction error:', err);
                startPredictionBtn.innerHTML = `
                    <span class="material-symbols-outlined" data-icon="error">error</span>
                    Error: ${err.message}
                `;
                startPredictionBtn.classList.remove('bg-blue-600', 'opacity-70', 'cursor-wait');
                startPredictionBtn.classList.add('bg-red-600');

                // Reset after 3 seconds
                setTimeout(() => {
                    startPredictionBtn.innerHTML = originalHTML;
                    startPredictionBtn.disabled = false;
                    startPredictionBtn.classList.remove('bg-red-600');
                    startPredictionBtn.classList.add('bg-blue-600', 'cursor-pointer');
                }, 3000);
            }
        });
    }

    // ── Render prediction results into the preview canvas ───────────────────
    function renderPredictionResults(data) {
        const canvas = document.querySelector('#view-data-manager > div:last-child');
        if (!canvas) return;

        const alliances = data.alliances;
        const summary = data.summary;
        const maxSeats = data.total_seats;

        // Color map for roles — supports both old (DOMINANT/BJP_FAMILY/MAIN_OPP)
        // and new dynamic roles (LEADING/CHALLENGER) from the updated model.
        // Alliance-name-based coloring gives more intuitive results.
        const roleColors = {
            'DOMINANT':    { bg: 'bg-emerald-500', text: 'text-emerald-400', bar: '#10b981' },
            'BJP_FAMILY':  { bg: 'bg-orange-500',  text: 'text-orange-400',  bar: '#f97316' },
            'MAIN_OPP':    { bg: 'bg-blue-500',    text: 'text-blue-400',    bar: '#3b82f6' },
            'LEADING':     { bg: 'bg-emerald-500', text: 'text-emerald-400', bar: '#10b981' },
            'CHALLENGER':  { bg: 'bg-orange-500',  text: 'text-orange-400',  bar: '#f97316' },
            'OTHERS':      { bg: 'bg-slate-500',   text: 'text-slate-400',   bar: '#64748b' },
        };

        // Alliance-specific colors override role-based ones for clarity
        const allianceColors = {
            'BJP+':     { bg: 'bg-orange-500',  text: 'text-orange-400',  bar: '#f97316' },
            'TMC+':     { bg: 'bg-emerald-500', text: 'text-emerald-400', bar: '#10b981' },
            'OTHERS+':  { bg: 'bg-slate-500',   text: 'text-slate-400',   bar: '#64748b' },
        };

        let allianceCards = alliances.map(a => {
            const colors = allianceColors[a.alliance] || roleColors[a.role] || roleColors['OTHERS'];
            const pct = ((a.point_estimate / maxSeats) * 100).toFixed(1);
            const confLabel = a.confidence >= 0.75 ? 'HIGH' : a.confidence >= 0.55 ? 'MODERATE' : a.confidence >= 0.35 ? 'LOW' : 'VERY LOW';
            const confColor = a.confidence >= 0.75 ? 'text-green-400' : a.confidence >= 0.55 ? 'text-yellow-400' : 'text-red-400';
            
            return `
                <div class="bg-surface-container border border-outline-variant rounded-xl p-5 relative overflow-hidden">
                    <div class="absolute top-0 left-0 h-1 ${colors.bg}" style="width: ${pct}%;"></div>
                    <div class="flex items-center justify-between mb-3">
                        <h3 class="font-bold text-white text-lg">${a.alliance}</h3>
                        <span class="text-xs px-2 py-0.5 rounded-full bg-slate-800 ${colors.text} border border-slate-700">${a.role}</span>
                    </div>
                    <div class="text-3xl font-black ${colors.text} mb-1">${a.point_estimate} <span class="text-sm font-normal text-slate-400">seats</span></div>
                    <div class="text-xs text-slate-400 mb-3">Range: ${a.interval_lo} - ${a.interval_hi} seats</div>
                    <div class="w-full bg-slate-800 rounded-full h-2 mb-3">
                        <div class="${colors.bg} h-2 rounded-full transition-all duration-700" style="width: ${pct}%;"></div>
                    </div>
                    <div class="flex justify-between text-xs">
                        <span class="text-slate-500">${a.n_agencies} agencies | Bias: ${a.bias_correction > 0 ? '+' : ''}${a.bias_correction}</span>
                        <span class="${confColor} font-semibold">${confLabel} (${Math.round(a.confidence * 100)}%)</span>
                    </div>
                </div>
            `;
        }).join('');

        const winnerMaj = summary.majority_likely;

        canvas.innerHTML = `
            <h2 class="font-label-caps text-label-caps text-on-surface-variant uppercase mb-4 tracking-widest">Prediction Results</h2>
            <div class="border border-outline-variant bg-surface-container-low rounded-xl p-6 relative overflow-hidden">
                <div class="absolute inset-0 opacity-[0.03]" style="background-image: radial-gradient(#fff 1px, transparent 1px); background-size: 24px 24px;"></div>
                <div class="relative z-10">
                    <!-- Summary Banner -->
                    <div class="flex items-center justify-between mb-6 p-4 rounded-lg bg-gradient-to-r ${winnerMaj ? 'from-green-900/30 to-emerald-900/20 border border-green-800/30' : 'from-yellow-900/30 to-amber-900/20 border border-yellow-800/30'}">
                        <div>
                            <p class="text-xs text-slate-400 uppercase tracking-widest mb-1">Predicted Winner</p>
                            <p class="text-2xl font-black text-white">${summary.likely_winner}</p>
                            <p class="text-sm text-slate-300">${summary.point_estimate} seats (${summary.interval_lo} - ${summary.interval_hi})</p>
                        </div>
                        <div class="text-right">
                            <span class="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-bold ${winnerMaj ? 'bg-green-500/20 text-green-400 border border-green-500/30' : 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30'}">
                                <span class="material-symbols-outlined text-sm">${winnerMaj ? 'check_circle' : 'warning'}</span>
                                ${winnerMaj ? 'MAJORITY LIKELY' : 'HUNG ASSEMBLY'}
                            </span>
                            <p class="text-xs text-slate-500 mt-2">Dataset: ${data.dataset_used}</p>
                        </div>
                    </div>
                    <!-- Alliance Cards Grid -->
                    <div class="grid grid-cols-1 md:grid-cols-${alliances.length} gap-4">
                        ${allianceCards}
                    </div>
                </div>
            </div>
        `;

        // Update Forecasting Tab (Statistical Results)
        const tableBody = document.getElementById('statistical-results-table');
        if (tableBody) {
            tableBody.innerHTML = alliances.map(a => {
                const colors = allianceColors[a.alliance] || roleColors[a.role] || roleColors['OTHERS'];
                const confColor = a.confidence >= 0.75 ? 'bg-green-500' : a.confidence >= 0.55 ? 'bg-yellow-500' : 'bg-red-500';
                
                // Visualization bar widths
                const leftPct = (a.interval_lo / maxSeats) * 100;
                const rightPct = 100 - ((a.interval_hi / maxSeats) * 100);
                const estPct = ((a.point_estimate - a.interval_lo) / (a.interval_hi - a.interval_lo)) * 100;

                return `
                    <tr class="border-b border-surface-variant hover:bg-surface-container-high transition-colors group h-table-row-height">
                        <td class="py-3 px-4 font-h3 text-h3 text-on-surface">${a.alliance} <span class="text-xs opacity-50 ml-1">(${a.role})</span></td>
                        <td class="py-3 px-4 text-right text-primary">${a.raw_median.toFixed(1)}</td>
                        <td class="py-3 px-4 text-right text-on-surface font-bold">${a.point_estimate}</td>
                        <td class="py-3 px-4">
                            <div class="w-full flex items-center gap-2">
                                <span class="text-on-surface-variant text-xs w-6 text-right">${a.interval_lo}</span>
                                <div class="flex-grow h-2 bg-surface-variant rounded-full overflow-hidden relative">
                                    <div class="absolute h-full ${colors.bg}/30 rounded-full" style="left: ${leftPct}%; right: ${rightPct}%;"></div>
                                    <div class="absolute h-full w-[2px] bg-white z-10" style="left: ${(a.point_estimate/maxSeats)*100}%;"></div>
                                </div>
                                <span class="text-on-surface-variant text-xs w-6">${a.interval_hi}</span>
                            </div>
                        </td>
                        <td class="py-3 px-4">
                            <div class="flex items-center justify-end gap-2">
                                <div class="w-16 h-1.5 bg-surface-variant rounded-full overflow-hidden">
                                    <div class="h-full ${confColor}" style="width: ${a.confidence * 100}%"></div>
                                </div>
                                <span class="text-on-surface">${a.confidence.toFixed(2)}</span>
                            </div>
                        </td>
                    </tr>
                `;
            }).join('');
        }

        // Update AI Prompt
        const promptBox = document.getElementById('ai-prompt-box');
        if (promptBox && data.ai_prompt) {
            promptBox.textContent = data.ai_prompt;
        }
    }

    // ── Apply AI Swing Logic ────────────────────────────────────────────────
    const applyAiBtn = document.getElementById('apply-ai-btn');
    const aiJsonInput = document.getElementById('ai-json-input');

    if (applyAiBtn && aiJsonInput) {
        applyAiBtn.addEventListener('click', async () => {
            if (!selectedDataset) {
                alert("Please select a dataset in Data Manager first.");
                return;
            }

            let sentimentData;
            try {
                sentimentData = JSON.parse(aiJsonInput.value);
            } catch (e) {
                alert("Invalid JSON in AI input. Please check the format.");
                return;
            }

            const originalHTML = applyAiBtn.innerHTML;
            applyAiBtn.disabled = true;
            applyAiBtn.innerHTML = `
                <svg class="animate-spin h-4 w-4 mr-2 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
                </svg>
                Processing...
            `;

            try {
                const response = await fetch('/api/apply_ai', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ dataset: selectedDataset, sentiment_data: sentimentData }),
                });

                if (!response.ok) {
                    throw new Error('AI Application failed');
                }

                const data = await response.json();
                renderFinalForecastResults(data);
                
                // Switch to Final Forecast tab
                switchView('view-final-forecast');
            } catch (err) {
                console.error(err);
                alert("Failed to apply AI swing: " + err.message);
            } finally {
                applyAiBtn.innerHTML = originalHTML;
                applyAiBtn.disabled = false;
            }
        });
    }

    // ── Render Final Forecast ───────────────────────────────────────────────
    function renderFinalForecastResults(data) {
        const results = data.results;
        const summary = data.summary;
        
        const hero = document.getElementById('final-forecast-hero');
        const bars = document.getElementById('final-forecast-bars');
        const table = document.getElementById('final-forecast-table');

        if (!hero || !bars || !table) return;

        // 1. Update Hero
        const winner = results[0];
        const majStatus = summary.majority_likely ? "Projected to secure absolute majority" : "Hung assembly likely; no clear majority";
        const majColor = summary.majority_likely ? "bg-green-500" : "bg-yellow-500";
        const majText = summary.majority_likely ? "High Confidence" : "Low Confidence";

        hero.innerHTML = `
            <div class="absolute -right-20 -top-20 w-64 h-64 bg-primary-container/10 rounded-full blur-3xl group-hover:bg-primary-container/20 transition-all duration-700"></div>
            <div class="flex justify-between items-start relative z-10 border-b border-outline-variant pb-4 mb-6">
                <h3 class="font-h2 text-h2 text-white">Most Likely Winner</h3>
                <div class="bg-[#1e293b] border border-[#334155] px-3 py-1 rounded-full flex items-center gap-2">
                    <span class="w-2 h-2 rounded-full ${majColor} animate-pulse"></span>
                    <span class="font-label-caps text-label-caps text-slate-300">${majText}</span>
                </div>
            </div>
            <div class="flex flex-col md:flex-row items-center gap-8 z-10 relative">
                <div class="w-32 h-32 rounded-xl bg-gradient-to-br from-blue-900 to-slate-900 border-2 border-blue-500/30 flex items-center justify-center shadow-[0_0_30px_rgba(37,99,235,0.2)]">
                    <span class="material-symbols-outlined text-6xl text-blue-400">assured_workload</span>
                </div>
                <div class="flex-1 text-center md:text-left">
                    <h1 class="text-5xl font-black text-white tracking-tighter mb-2">${winner.alliance}</h1>
                    <p class="text-slate-400 font-body-md text-body-md mb-6">${majStatus}</p>
                    <div class="flex items-end gap-4 justify-center md:justify-start">
                        <div class="bg-surface-container border border-outline-variant rounded-DEFAULT p-4 w-40 text-center md:text-left">
                            <p class="font-label-caps text-label-caps text-slate-500 mb-1">Confidence Score</p>
                            <p class="font-data-lg text-data-lg text-white text-3xl">${(winner.confidence * 100).toFixed(0)}<span class="text-slate-500 text-xl">%</span></p>
                        </div>
                        <div class="bg-surface-container border border-outline-variant rounded-DEFAULT p-4 w-40 text-center md:text-left">
                            <p class="font-label-caps text-label-caps text-slate-500 mb-1">Projected Seats</p>
                            <p class="font-data-lg text-data-lg text-white text-3xl">${winner.final_estimate}</p>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // 2. Update Bars
        const maxSeats = Math.max(...results.map(r => r.final_estimate)) * 1.2;
        let barHtml = `
            <div class="absolute inset-0 flex flex-col justify-between pointer-events-none opacity-20">
                <div class="border-t border-slate-500 w-full"></div>
                <div class="border-t border-slate-500 w-full"></div>
                <div class="border-t border-slate-500 w-full"></div>
                <div class="border-t border-slate-500 w-full"></div>
            </div>
        `;

        results.forEach(r => {
            const basePct = (r.stat_estimate / maxSeats) * 100;
            const finalPct = (r.final_estimate / maxSeats) * 100;
            
            barHtml += `
                <div class="flex flex-col items-center gap-2 w-full max-w-[100px] z-10 group relative">
                    <div class="flex items-end gap-1 w-full justify-center h-48">
                        <div class="w-1/2 bg-slate-600 rounded-t-sm transition-all group-hover:opacity-80 relative" style="height: ${basePct}%">
                            <div class="absolute -top-6 left-1/2 -translate-x-1/2 opacity-0 group-hover:opacity-100 font-data-caps text-data-caps text-slate-400 transition-opacity">${r.stat_estimate}</div>
                        </div>
                        <div class="w-1/2 bg-blue-500 rounded-t-sm relative transition-all group-hover:opacity-80" style="height: ${finalPct}%">
                            <div class="absolute -top-6 left-1/2 -translate-x-1/2 opacity-0 group-hover:opacity-100 font-data-caps text-data-caps text-blue-400 transition-opacity">${r.final_estimate}</div>
                        </div>
                    </div>
                    <span class="font-label-caps text-label-caps text-slate-400 uppercase">${r.alliance}</span>
                </div>
            `;
        });
        bars.innerHTML = barHtml;

        // 3. Update Table
        table.innerHTML = results.map(r => {
            const deltaClass = r.ai_delta > 0 ? "bg-green-900/50 text-green-400 border-green-800" : (r.ai_delta < 0 ? "bg-red-900/50 text-red-400 border-red-800" : "bg-slate-800 text-slate-300 border-slate-700");
            const deltaSign = r.ai_delta > 0 ? "+" : "";

            return `
                <tr class="border-b border-slate-800/50 hover:bg-surface-variant transition-colors h-table-row-height">
                    <td class="py-2 px-4 font-semibold text-white">${r.alliance}</td>
                    <td class="py-2 px-4 text-right">${r.stat_estimate}</td>
                    <td class="py-2 px-4 text-right">
                        <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium border ${deltaClass}">${deltaSign}${r.ai_delta.toFixed(1)}</span>
                    </td>
                    <td class="py-2 px-4 text-right text-white font-bold">${r.final_estimate}</td>
                    <td class="py-2 px-4 text-right text-slate-400">${r.final_lo} - ${r.final_hi}</td>
                </tr>
            `;
        }).join('');
    }
});
