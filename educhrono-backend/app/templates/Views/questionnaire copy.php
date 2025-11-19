<!DOCTYPE html>
<html lang="en">
<head>
<?php
if (!session()->get('isLoggedIn')) {
    header('Location: ' . base_url('login'));
    exit;
}

$userName = session()->get('user_name');
?>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MindXTrading | Report</title>
    <!-- Load Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- Load Inter Font -->
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@100..900&display=swap');
        body { font-family: 'Inter', sans-serif; background-color: #f7f7f7; padding: 0; margin: 0; }
        ::-webkit-scrollbar { width: 8px; }
        ::-webkit-scrollbar-thumb { background: #4f46e5; border-radius: 4px; }
        .step-container { transition: opacity 0.3s ease-in-out; }
        .step-container.hidden { display: none; opacity: 0; }
        .custom-range-slider { -webkit-appearance: none; appearance: none; width: 100%; height: 8px; background: #d1d5db; outline: none; opacity: 0.9; transition: opacity .15s; border-radius: 4px; }
        .custom-range-slider::-webkit-slider-thumb { -webkit-appearance: none; appearance: none; width: 20px; height: 20px; border-radius: 50%; background: #4f46e5; cursor: pointer; box-shadow: 0 0 5px rgba(0,0,0,0.2); border: 3px solid #fff; }
        #report-container { min-height: 100vh; display: none; }

        /* Custom style for the diagnostic blocks */
        .diagnostic-block {
            transition: all 0.3s ease;
            position: relative;
            z-index: 10;
        }

        /* Severity color classes for border accent */
        .severity-low { border-left-color: #10b981; /* Green-500 */ }
        .severity-medium { border-left-color: #f59e0b; /* Amber-500 */ }
        .severity-high { border-left-color: #dc2626; /* Red-600 */ }
        
        .question-card {
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.06);
        }
          body {
    font-family: 'Poppins', sans-serif;
    background: linear-gradient(to bottom, #f9fbff 0%, #eef3ff 100%);
    color: #1e293b;
    margin: 0;
  }

  .dashboard-header {
    background: #ffffff;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    padding: 15px 8%;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .dashboard-header h2 {
    font-size: 1.4rem;
    color: #1e293b;
    font-weight: 600;
  }

  .user-info {
    display: flex;
    align-items: center;
    gap: 15px;
  }

  .user-info span {
    font-weight: 500;
    color: #334155;
  }

  .logout-btn {
    background: #2563eb;
    color: #fff;
    border: none;
    padding: 8px 14px;
    border-radius: 6px;
    font-weight: 500;
    cursor: pointer;
    transition: background 0.3s ease;
  }

  .logout-btn:hover {
    background: #1d4ed8;
  }

  .ctpa-section {
    max-width: 1100px;
    margin: 60px auto;
    background: #ffffff;
    border-radius: 12px;
    padding: 50px 40px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
    border-top: 4px solid #2563eb;
  }

  .ctpa-section h1 {
    text-align: center;
    font-size: 2rem;
    font-weight: 700;
    color: #1e3a8a;
    margin-bottom: 20px;
  }

  .ctpa-section h2 {
    text-align: center;
    font-size: 1.2rem;
    font-weight: 500;
    color: #475569;
    margin-bottom: 30px;
  }

  footer {
    background: #f9fbff;
    text-align: center;
    padding: 40px 0 20px;
    border-top: 1px solid #e2e8f0;
    color: #64748b;
    font-size: 14px;
  }

  footer a {
    color: #2563eb;
    text-decoration: none;
    font-weight: 500;
  }

  footer a:hover {
    text-decoration: underline;
  }
  input:invalid {
  border-color: #ef4444;
}

#ai-narrative, #ai-action-plan, #ai-next-steps {
  font-family: 'Poppins', sans-serif;
  font-size: 15px;
  line-height: 1.6;
  color: #1e293b;
  padding: 15px 25px;
  background: #f9fafb;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  margin-top: 10px;
}

#ai-narrative h3, #ai-action-plan h3, #ai-next-steps h3 {
  color: #1e3a8a;
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 8px;
}

#ai-narrative strong, #ai-action-plan strong, #ai-next-steps strong {
  color: #0f172a;
  font-weight: 600;
}

#ai-narrative ul, #ai-action-plan ul, #ai-next-steps ul {
  padding-left: 20px;
  margin-top: 6px;
}

#ai-narrative table, #ai-action-plan table, #ai-next-steps table {
  border-collapse: collapse;
  width: 100%;
  margin: 10px 0;
}
#ai-narrative table td, #ai-action-plan table td, #ai-next-steps table td {
  border: 1px solid #e2e8f0;
  padding: 6px 8px;
}

.invite-box {
  background: #0f172a;
  color: white;
  padding: 20px;
  border-radius: 12px;
  margin-top: 25px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.2);
}
.invite-box h4 { color: #38bdf8; margin-bottom: 8px; }
.invite-box a { color: #38bdf8; text-decoration: none; }

.disclaimer-box {
  background: #fef9c3;
  color: #78350f;
  padding: 20px;
  border-radius: 12px;
  margin-top: 15px;
  border: 1px solid #fde68a;
  box-shadow: 0 2px 6px rgba(0,0,0,0.05);
}
.disclaimer-box h4 { color: #92400e; margin-bottom: 8px; }

    </style>
</head>
<body class="bg-gray-50">
<!-- Dashboard Header -->
<header class="dashboard-header">
  <h2><a href="<?= base_url('/') ?>" style="text-decoration: none; color: inherit;">
    MindXTrading
  </a></h2>
  <div class="user-info">
    <span>👋 Welcome, <strong><?= ucfirst($userName) ?></strong></span>
    <form action="<?= base_url('logout') ?>" method="post" style="margin:0;">
      <button type="submit" class="logout-btn">Logout</button>
    </form>
  </div>
</header>
    <!-- Assessment Container (Steps) -->
    <div id="assessment-container" class="max-w-4xl mx-auto p-4 sm:p-8 pt-10">
        <header class="text-center mb-10">
            <h1 class="text-3xl sm:text-4xl font-extrabold text-indigo-700">C.T.P.A.</h1>
            <h2 class="text-xl sm:text-2xl font-semibold text-gray-800 mt-1">Advanced Trader Diagnostic</h2>
            <div id="progress-bar" class="w-full bg-gray-200 rounded-full h-2.5 mt-4">
                <div id="progress-fill" class="bg-indigo-500 h-2.5 rounded-full transition-all duration-300" style="width: 0%;"></div>
            </div>
        </header>

        <div id="steps-wrapper">
            <!-- Step 1: Trader Profile -->
            <div id="step-1" class="step-container p-6 bg-white shadow-xl rounded-2xl">
                <h3 class="text-2xl font-bold mb-6 text-gray-700 border-b pb-3">Section 1: Profile and Metric</h3>
                <div class="space-y-6">
                    <div>
                        <!-- <label for="name" class="block text-sm font-medium text-gray-700 mb-2">Your Name</label>
                        <input type="text" id="name" class="w-full p-3 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500" placeholder="e.g., Alex" required/>
                         -->
                        <label for="name" class="block text-sm font-medium text-gray-700 mb-2">Your Name</label>
<input 
  type="text" 
  id="name" 
  class="w-full p-3 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500" 
  placeholder="e.g., Alex" 
  required
>

                    </div>
                    <div>
                        <label for="experience" class="block text-sm font-medium text-gray-700 mb-2">Years of Trading Experience</label>
                        <select id="experience" class="w-full p-3 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500">
                            <option value="0">Less than 1 year</option>
                            <option value="1">1-2 Years</option>
                            <option value="2">2-5 Years</option>
                            <option value="3">5-10 Years</option>
                            <option value="4">10+ Years</option>
                        </select>
                    </div>
                     <!-- Performance Q (Metric: Average Win Rate) -->
                    <div class="bg-indigo-50 p-4 rounded-xl border border-indigo-200">
                        <label for="c1" class="block text-base font-semibold text-gray-700 mb-3">Performance Metric: Approximate Average Win Rate (%)</label>
                        <input type="range" id="c1" min="0" max="100" value="50" class="custom-range-slider" oninput="document.getElementById('c1-value').innerText = this.value + '%'">
                        <div class="flex justify-between text-sm text-gray-600 mt-2">
                            <span>0%</span>
                            <span id="c1-value" class="font-bold text-indigo-600">50%</span>
                            <span>100%</span>
                        </div>
                    </div>
                </div>
                <div class="mt-8 flex justify-end">
                    <button onclick="validateStep1()" class="px-6 py-3 bg-indigo-600 text-white font-semibold rounded-xl shadow-md hover:bg-indigo-700 transition duration-150">Next Section &rarr;</button>
                </div>
            </div>

            <!-- Step 2: Behavioral Assessment (10 Questions) -->
            <div id="step-2" class="step-container p-6 bg-white shadow-xl rounded-2xl hidden">
                <h3 class="text-2xl font-bold mb-6 text-gray-700 border-b pb-3">Section 2: Critical Behavior Assessment (1-5 Scale)</h3>
                <div class="space-y-8">
                    
                    <!-- Emotional Triggers (Pillar G) -->
                    <div class="bg-red-50 p-5 rounded-xl border border-red-200 question-card">
                        <p class="text-lg font-bold text-red-700 mb-3">Emotional Triggers (G)</p>
                        <div class="space-y-4">
                            <label class="block text-base font-medium text-gray-700">1. Do you continue trading after hitting your loss limit? (Revenge trading)</label>
                            <select id="g1" class="w-full p-3 border border-gray-300 rounded-lg">
                                <option value="0">Always</option>
                                <option value="33">Often</option>
                                <option value="66">Sometimes</option>
                                <option value="100">Never</option>
                            </select>
                            
                            <label class="block text-base font-medium text-gray-700">2. Do you enter trades out of fear of missing out (FOMO)?</label>
                            <select id="g2" class="w-full p-3 border border-gray-300 rounded-lg">
                                <option value="0">Always</option>
                                <option value="33">Often</option>
                                <option value="66">Sometimes</option>
                                <option value="100">Never</option>
                            </select>

                            <label class="block text-base font-medium text-gray-700">3. Do you feel intensely angry or anxious after a losing trade?</label>
                            <select id="g3" class="w-full p-3 border border-gray-300 rounded-lg">
                                <option value="0">Always</option>
                                <option value="33">Often</option>
                                <option value="66">Sometimes</option>
                                <option value="100">Never</option>
                            </select>
                        </div>
                    </div>

                    <!-- Planning & Consistency (Pillar J) -->
                    <div class="bg-teal-50 p-5 rounded-xl border border-teal-200 question-card">
                        <p class="text-lg font-bold text-teal-700 mb-3">Planning & Consistency (J)</p>
                        <div class="space-y-4">
                            <label class="block text-base font-medium text-gray-700">4. Do you trade with a written, defined plan each day?</label>
                            <select id="j1" class="w-full p-3 border border-gray-300 rounded-lg">
                                <option value="100">Always</option>
                                <option value="66">Often</option>
                                <option value="33">Sometimes</option>
                                <option value="0">Never</option>
                            </select>
                            
                            <label class="block text-base font-medium text-gray-700">5. Do you predefine your stop-loss and target (R:R) every time?</label>
                            <select id="j2" class="w-full p-3 border border-gray-300 rounded-lg">
                                <option value="100">Always</option>
                                <option value="66">Often</option>
                                <option value="33">Sometimes</option>
                                <option value="0">Never</option>
                            </select>
                        </div>
                    </div>

                    <!-- Execution & Control (Pillar I) -->
                    <div class="bg-purple-50 p-5 rounded-xl border border-purple-200 question-card">
                        <p class="text-lg font-bold text-purple-700 mb-3">Execution & Control (I)</p>
                        <div class="space-y-4">
                            <label class="block text-base font-medium text-gray-700">6. Do you exit trades early even when your setup remains valid?</label>
                            <select id="i1" class="w-full p-3 border border-gray-300 rounded-lg">
                                <option value="0">Always</option>
                                <option value="33">Often</option>
                                <option value="66">Sometimes</option>
                                <option value="100">Never</option>
                            </select>
                            
                            <label class="block text-base font-medium text-gray-700">7. Do you take trades outside your system because of urge or noise?</label>
                            <select id="i2" class="w-full p-3 border border-gray-300 rounded-lg">
                                <option value="0">Always</option>
                                <option value="33">Often</option>
                                <option value="66">Sometimes</option>
                                <option value="100">Never</option>
                            </select>
                        </div>
                    </div>
                    
                    <!-- Growth & Reflection (Pillar K) -->
                    <div class="bg-blue-50 p-5 rounded-xl border border-blue-200 question-card">
                        <p class="text-lg font-bold text-blue-700 mb-3">Growth & Reflection (K)</p>
                        <div class="space-y-4">
                            <label class="block text-base font-medium text-gray-700">8. Do you maintain a detailed journal or log your trades weekly?</label>
                            <select id="k1" class="w-full p-3 border border-gray-300 rounded-lg">
                                <option value="100">Always</option>
                                <option value="66">Often</option>
                                <option value="33">Sometimes</option>
                                <option value="0">Never</option>
                            </select>
                            
                            <label class="block text-base font-medium text-gray-700">9. Do you review past mistakes and actively work to correct them, or do you repeat them?</label>
                            <select id="k2" class="w-full p-3 border border-gray-300 rounded-lg">
                                <option value="100">Actively Review and Correct</option>
                                <option value="66">Review Occasionally</option>
                                <option value="33">Rarely Review</option>
                                <option value="0">Tend to Repeat Them</option>
                            </select>
                        </div>
                    </div>

                </div>
                <div class="mt-8 flex justify-between">
                    <button onclick="prevStep()" class="px-4 py-2 bg-gray-300 text-gray-700 font-semibold rounded-xl hover:bg-gray-400 transition duration-150">&larr; Back</button>
                    <button onclick="calculateAndDisplayReport()" class="px-6 py-3 bg-indigo-600 text-white font-semibold rounded-xl shadow-md hover:bg-indigo-700 transition duration-150">Generate Diagnostic Report &rarr;</button>
                </div>
            </div>
        </div>
    </div>

    <!-- Report Container -->
    <div id="report-container" class="max-w-6xl mx-auto p-4 sm:p-10 bg-white shadow-2xl rounded-3xl my-8">
        <div class="text-center mb-12">
            <h1 class="text-4xl sm:text-5xl font-extrabold text-gray-800">Your Basic Diagnostic Report</h1>
            <p class="text-xl text-indigo-600 mt-2" id="report-name"></p>
        </div>

        <!-- Section 1: Executive Summary -->
        <h2 class="text-3xl font-bold text-gray-700 mb-6 border-b pb-2">High-Impact Snapshot</h2>
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-12">
            <!-- Summary Card 1: Final Score -->
            <div class="bg-indigo-50 p-6 rounded-2xl text-center shadow-lg border-b-4 border-indigo-600">
                <span class="text-4xl font-extrabold text-indigo-700 block mb-2">⭐</span>
                <p class="text-lg font-semibold text-gray-600">Final CTPA Score</p>
                <div class="text-6xl font-extrabold mt-2 text-indigo-800" id="final-score">--</div>
                <p class="text-xl font-bold mt-1" id="final-classification"></p>
            </div>
            <!-- Summary Card 2: Trader Identity -->
            <div class="bg-red-50 p-6 rounded-2xl text-center shadow-lg border-b-4 border-red-600">
                <span class="text-4xl font-extrabold text-red-700 block mb-2">🧠</span>
                <p class="text-lg font-semibold text-gray-600">Trader Identity Bias</p>
                <p class="text-2xl font-extrabold mt-3 text-red-800" id="trader-identity">--</p>
                <p class="text-sm mt-2 text-gray-500">How decisions are currently driven.</p>
            </div>
            <!-- Summary Card 3: Top Strength -->
            <div class="bg-teal-50 p-6 rounded-2xl text-center shadow-lg border-b-4 border-teal-600">
                <span class="text-4xl font-extrabold text-teal-700 block mb-2">✅</span>
                <p class="text-lg font-semibold text-gray-600">Top Strength Category</p>
                <p class="text-2xl font-extrabold mt-3 text-teal-800" id="top-strength-title">--</p>
                <p class="text-sm mt-2 text-gray-500">Score: <span id="top-strength-score">--</span>%</p>
            </div>
        </div>

        <!-- Section 2: Gap Diagnostic Infographic -->
        <h2 class="text-3xl font-bold text-gray-700 mb-6 border-b pb-2">Critical Gap Diagnostic: Layering the Root Cause</h2>
        <p class="text-lg text-gray-500 mb-8 max-w-4xl mx-auto text-center">Your top weakness is broken down from the visible **Behavior** to the invisible **Root Cause**, giving you a clear focus for intervention.</p>
        
        <div id="diagnostic-error" class="text-center text-2xl text-green-700 font-semibold bg-green-100 p-6 rounded-xl mb-8 border-2 border-green-300 hidden">
            <p>Congratulations! No critical gaps detected (all core parameters &gt; 75%). Focus on optimizing R:R and advanced strategies.</p>
        </div>

        <!-- The visually enhanced diagnostic grid with flow -->
        <div id="diagnostic-flow" class="grid grid-cols-1 lg:grid-cols-4 gap-6 relative mb-10">
            
            <!-- Block 1: Behavior Tag (Symptom - Layer 1) -->
            <div class="diagnostic-block p-6 rounded-xl border-l-4 border-gray-300 shadow-xl bg-white" id="block-tag">
                <div class="mb-2 flex items-center">
                    <span class="text-sm font-extrabold text-gray-400 mr-2">Layer 1</span>
                    <p class="text-xs font-bold uppercase text-gray-600">Behavior Tag (Symptom)</p>
                </div>
                <p class="text-3xl font-extrabold mt-1 text-indigo-700" id="behavior-tag">--</p>
                <p class="text-sm text-gray-500 mt-2">The surface-level action costing money.</p>
            </div>
            
            <!-- Block 2: Severity (Measurement - Layer 2) -->
            <div class="diagnostic-block p-6 rounded-xl border-l-4 border-gray-300 shadow-xl bg-white" id="block-severity">
                <div class="mb-2 flex items-center">
                    <span class="text-sm font-extrabold text-gray-400 mr-2">Layer 2</span>
                    <p class="text-xs font-bold uppercase text-gray-600">Severity (1-10)</p>
                </div>
                <p class="text-5xl font-extrabold text-red-600" id="severity-score">--</p>
                <p class="text-sm text-gray-500 mt-2">How critical this weakness is.</p>
            </div>
            
            <!-- Block 3: Root Cause Layer (Cause - Layer 3) -->
            <div class="diagnostic-block p-6 rounded-xl border-l-4 border-gray-300 shadow-xl bg-white" id="block-root-cause">
                <div class="mb-2 flex items-center">
                    <span class="text-sm font-extrabold text-gray-400 mr-2">Layer 3</span>
                    <p class="text-xs font-bold uppercase text-gray-600">Root Cause Layer (Focus)</p>
                </div>
                <p class="text-xl font-extrabold mt-1 text-teal-700" id="root-cause-layer">--</p>
                <p class="text-sm text-gray-500 mt-2">The fundamental psychological trigger.</p>
            </div>
            
            <!-- Block 4: Impact Type (Consequence - Layer 4) -->
            <div class="diagnostic-block p-6 rounded-xl border-l-4 border-gray-300 shadow-xl bg-white" id="block-impact-type">
                <div class="mb-2 flex items-center">
                    <span class="text-sm font-extrabold text-gray-400 mr-2">Layer 4</span>
                    <p class="text-xs font-bold uppercase text-gray-600">Impact Type (Consequence)</p>
                </div>
                <p class="text-xl font-extrabold mt-1 text-purple-700" id="impact-type">--</p>
                <p class="text-sm text-gray-500 mt-2">The resulting damage to your P&L.</p>
            </div>
        </div>

        <!-- Section 3: Summary and Action Plan -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mt-12">
             <!-- Left: Narrative Summary -->
            <div class="bg-gray-100 p-8 rounded-2xl shadow-xl">
                <p class="text-xl font-bold text-gray-800 mb-4" id="top-weakness-title">--</p>
                <p class="text-gray-600 leading-relaxed" id="top-weakness-narrative">--</p>
            </div>
            <!-- Right: 7-Day Action Plan (High Contrast) -->
            <div class="bg-gray-900 text-white p-8 rounded-2xl shadow-2xl border-b-4 border-indigo-500">
                <p class="text-2xl font-bold mb-4 text-indigo-400 flex items-center">
                    <svg class="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"></path></svg>
                    7-Day Action Plan
                </p>
                <div class="space-y-3 text-lg" id="action-plan-list">
                    <!-- Action steps will be injected here -->
                </div>
            </div>
        </div>

        <div class="mt-12">
            <section class="mt-10 space-y-6" id="ai-insights">
<div class="rounded-2xl p-6 shadow-lg bg-indigo-50 border-l-4 border-indigo-500">
<h3 class="text-xl font-bold text-indigo-700 flex items-center gap-2">
      🧠 Analyst’s Narrative Analysis
    </h3>
<p class="text-gray-700 mt-2" id="ai-narrative">Generating personalized report insights...</p>
</div>
<div class="rounded-2xl p-6 shadow-lg bg-emerald-50 border-l-4 border-emerald-500">
<h3 class="text-xl font-bold text-emerald-700 flex items-center gap-2">
      ⚙️ Personalized Action Plan
    </h3>
<p class="text-gray-700 mt-2" id="ai-action-plan">Preparing actionable recommendations...</p>
</div>
<div class="rounded-2xl p-6 shadow-lg bg-green-50 border-l-4 border-green-500">
<h3 class="text-xl font-bold text-green-700 flex items-center gap-2">
      🚀 Next Steps: Turn Insight Into Action
    </h3>
<p class="text-gray-700 mt-2" id="ai-next-steps">Evaluating next best strategies...</p>
</div>
</section>
<br/>
            <h3 class="text-2xl font-bold text-gray-700 mb-4 border-b pb-2">Full Weakness Ranking (Top 3)</h3>
            <div id="top-three-list" class="space-y-3 text-lg text-gray-700 p-6 border border-gray-200 rounded-xl bg-gray-50 shadow-inner">
                <!-- Top 3 List will be injected here -->
            </div>
        </div>
        <div class="text-center mt-8">
            <button id="generatePdfBtn"
                class="px-6 py-3 bg-indigo-600 text-white font-semibold rounded-xl shadow-md hover:bg-indigo-700 transition duration-150">
                📄 Send Report
            </button>
        </div>
    </div>

    <!-- Footer -->
<footer>
  <div>
    <strong>MindXTrading</strong> — Behavioral Coaching for Strategic Traders<br>
    © 2025 MindXTrading Performance Coaching. Designed & Developed by 
    <a href="https://functionx.in" target="_blank">FunctionX Technologies</a>
  </div>
</footer>

    <script>
        document.getElementById("generatePdfBtn").addEventListener("click", function() {
            // const html = document.getElementById("report-container").innerHTML;
             const name = document.getElementById("report-name").innerText || "Trader_Report";
            let htmlClone = document.documentElement.cloneNode(true);

            // ✅ Remove elements not needed in PDF (like buttons)
            const buttons = htmlClone.querySelectorAll('button, #generatePdfBtn');
            buttons.forEach(btn => btn.remove());

            // ✅ Serialize to HTML string
            const html = "<!DOCTYPE html>\n" + htmlClone.outerHTML;
            fetch("<?= base_url('report/generatePdf') ?>", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ html: html, name: name })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    alert("✅ PDF Created & Sent Successfully!");
                } else {
                    alert("❌ " + data.message);
                }
            })
            .catch(err => console.error("Error:", err));
        });
    </script>

    <script>
const inviteSection = `
<div class="invite-box">
  <h4>💡 Invite to the MindX Program</h4>
  <p>We invite you to schedule a <strong>1-on-1 Diagnostic Session</strong> to analyze your full report and build a custom 30-day plan to address your weakest pillar.</p>
  <p><strong>Email us today to book your session:</strong><br>
  <a href="mailto:coach@mindxtrading.com">coach@mindxtrading.com</a></p>
</div>
`;

const disclaimerSection = `
<div class="disclaimer-box">
  <h4>⚠ Statutory SEBI Disclaimer</h4>
  <p><strong>Disclaimer:</strong> Investment in securities market is subject to market risks, read all related documents carefully before investing. This report is purely an educational and informational tool designed for psychological self-assessment and <strong>is not a recommendation or advice</strong> to buy, sell, or hold any security. We are not SEBI registered financial advisors or research analysts. All trading decisions based on this self-assessment are solely the responsibility of the user.</p>
</div>
`;

document.getElementById("ai-narrative").insertAdjacentHTML("afterend", inviteSection + disclaimerSection);

document.addEventListener("DOMContentLoaded", () => {
  console.log("🚀 v17 AI Auto-Generation Active");

  async function generateAIReportWithPerplexity() {
  const badge = document.createElement("div");
  badge.textContent = "✅ AI Insights Generated";
  Object.assign(badge.style, {
    position: "fixed", top: "20px", right: "20px", background: "#22c55e",
    color: "#fff", padding: "8px 16px", borderRadius: "8px",
    fontSize: "14px", fontWeight: "600", zIndex: "9999",
    transition: "opacity 1s ease-in-out"
  });
  document.body.appendChild(badge);

  // --- Helper to get actual answer text ---
  const getAnswerText = (id) => {
    const el = document.getElementById(id);
    if (!el) return "Not answered";

    // If the answer is stored in a label next to slider
    if (el.type === "range" && el.dataset.label) return el.dataset.label;

    // If it's a select input
    if (el.tagName === "SELECT") return el.options[el.selectedIndex].text;

    // If it's a text input or any other field
    return el.value || "Not answered";
  };

  // --- Collect dynamic user data ---
  const traderName = document.getElementById("name")?.value?.trim() || "Trader";
  const expElement = document.getElementById("experience");
  const experience = expElement ? expElement.options[expElement.selectedIndex].text : "N/A";
  const winRate = document.getElementById("c1")?.value || "N/A";

  // --- Behavioral Question Mapping ---
  const qna = [
    `1. Do you continue trading after hitting your loss limit? → ${getAnswerText("g1")}`,
    `2. Do you enter trades out of fear of missing out (FOMO)? → ${getAnswerText("g2")}`,
    `3. Do you feel anxious after a losing trade? → ${getAnswerText("g3")}`,
    `4. Do you trade with a written plan each day? → ${getAnswerText("j1")}`,
    `5. Do you predefine stop-loss and target? → ${getAnswerText("j2")}`,
    `6. Do you exit trades early even when valid? → ${getAnswerText("i1")}`,
    `7. Do you take trades outside your system? → ${getAnswerText("i2")}`,
    `8. Do you maintain a trading journal? → ${getAnswerText("k1")}`,
    `9. Do you review past mistakes? → ${getAnswerText("k2")}`,
    `10. Approximate average win rate: ${winRate}%`
  ].join("\n");

  const finalScore = window.finalScore || 40;
  const classification = window.classificationLabel || "Reactive-Trader";
  const weakness = window.topWeakness?.name || "Loss-Driven Impulsivity";

  // --- Build dynamic prompt ---
  const prompt = `
You are a behavioral performance analyst specializing in trader psychology. 
Based on the following assessment responses, generate a detailed report covering these sections:
1. Narrative Analysis
2. Personalized Action Plan
3. Next Steps & Maintenance

Trader Name: ${traderName}
Experience: ${experience}
Performance Metric: ${winRate}%

Question–Answer Data:
${qna}

Derived metrics:
Final Score: ${finalScore}
Classification: ${classification}
Primary Weakness: ${weakness}

Generate a comprehensive psychological diagnostic report that infers trader behavior, identifies emotional or systematic tendencies, classifies trader type (Systematic / Emotional / Reactive), and provides a structured, actionable roadmap to improve emotional stability, discipline, and consistency.
`;

  console.log("🧠 Dynamic Prompt Generated:", prompt);

  let text = "";
  try {
    const res = await fetch("https://api.perplexity.ai/chat/completions", {
      method: "POST",
      headers: {
        "Authorization": "Bearer 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",
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        model: "sonar-reasoning",
        messages: [
          {
            role: "system",
            content:
              "You are a behavioral performance analyst generating professional trader psychology diagnostic reports with three sections: Narrative Analysis, Personalized Action Plan, and Next Steps & Maintenance."
          },
          { role: "user", content: prompt }
        ],
        temperature: 0.7,
        stream: false
      })
    });

    if (res.ok) {
      const data = await res.json();
      console.log("✅ Perplexity result:", data);
      text = data?.choices?.[0]?.message?.content || "";
    }

    // --- If empty response ---
    if (!text) {
      text = `
## 1. NARRATIVE ANALYSIS
Default fallback: Maintain emotional balance and focus on discipline.

## 2. PERSONALIZED ACTION PLAN
Keep a journal and follow consistent risk management.

## 3. NEXT STEPS & MAINTENANCE
Review performance weekly and refine psychological discipline.
`;
    }

    console.log("📘 Raw AI Text:", text);

    // --- Robust parsing (supports numbered headings and variations) ---
// --- Improved Section Parsing ---
let narrative = "";
let plan = "";
let nextSteps = "";

// Normalize line breaks and ensure all headings have consistent format
let cleanText = text.replace(/\r/g, "").trim();

// Use regex to split based on the 3 headings
const sections = cleanText.split(/##\s*(?:\d+\.\s*)?(?:NARRATIVE ANALYSIS|PERSONALIZED ACTION PLAN|NEXT STEPS(?:\s*&\s*MAINTENANCE)?)/i);

if (sections.length > 1) {
  // sections[0] = intro or unused
  narrative = sections[1]?.trim() || "";
  plan = sections[2]?.trim() || "";
  nextSteps = sections[3]?.trim() || "";
}

// --- Fallback check ---
if (!narrative) narrative = "No narrative generated.";
if (!plan) plan = "No plan generated.";
if (!nextSteps) nextSteps = "No next steps generated.";

// --- Markdown → HTML converter (basic) ---
// function renderMarkdown(md) {
//   return md
//     .replace(/^### (.*$)/gim, "<h4>$1</h4>")
//     .replace(/^## (.*$)/gim, "<h3>$1</h3>")
//     .replace(/^# (.*$)/gim, "<h2>$1</h2>")
//     .replace(/\*\*(.*?)\*\*/gim, "<strong>$1</strong>")
//     .replace(/\*(.*?)\*/gim, "<em>$1</em>")
//     .replace(/\n/gim, "<br>");
// }
function renderMarkdown(md) {
  if (!md) return "";
  return md
    // Headings
    .replace(/^### (.*$)/gim, "<h4>$1</h4>")
    .replace(/^## (.*$)/gim, "<h3>$1</h3>")
    .replace(/^# (.*$)/gim, "<h2>$1</h2>")
    // Bold + italic
    .replace(/\*\*(.*?)\*\*/gim, "<strong>$1</strong>")
    .replace(/\*(.*?)\*/gim, "<em>$1</em>")
    // Lists
    .replace(/^\s*[-•]\s+(.*)/gim, "<li>$1</li>")
    .replace(/(<li>.*<\/li>)/gim, "<ul>$1</ul>")
    // Tables (basic)
    .replace(/\|(.+)\|/gim, (m) => {
      const cells = m.split("|").filter(Boolean).map(c => `<td>${c.trim()}</td>`).join("");
      return `<table><tr>${cells}</tr></table>`;
    })
    // Line breaks
    .replace(/\n{2,}/g, "</p><p>")
    .replace(/\n/g, "<br>")
    // Paragraphs
    .replace(/^(.+?)$/gim, "<p>$1</p>");
}

const fullReportHTML = `
  <div class="full-report">
    <h3>🧠 Analyst’s Narrative Analysis</h3>
    ${renderMarkdown(narrative)}
    <h3>⚙ Personalized Action Plan</h3>
    ${renderMarkdown(plan)}
    <h3>🚀 Next Steps: Turn Insight Into Action</h3>
    ${renderMarkdown(nextSteps)}
    ${inviteSection}
    ${disclaimerSection}
  </div>
`;

// Send to backend to save
fetch(`${base_url}/save_full_report`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    userId: window.userId, // dynamic user ID
    reportHTML: fullReportHTML,
  }),
})
.then(res => res.json())
.then(data => console.log("✅ Full report saved on server:", data))
.catch(err => console.error("⚠️ Report save failed:", err));


// --- Render Markdown to HTML ---
document.getElementById("ai-narrative").innerHTML = renderMarkdown(narrative);
// Hide Action Plan and Next Steps from public view
document.getElementById("ai-action-plan").style.display = "none";
document.getElementById("ai-next-steps").style.display = "none";

// Remove Full Weakness Ranking (Top 3)
const weaknessSection = document.getElementById("weakness-ranking");
if (weaknessSection) weaknessSection.remove();
document.getElementById("ai-action-plan").innerHTML = renderMarkdown(plan);
document.getElementById("ai-next-steps").innerHTML = renderMarkdown(nextSteps);

// --- Smooth fade-in animation for generated sections ---
["ai-narrative", "ai-action-plan", "ai-next-steps"].forEach((id, i) => {
  const el = document.getElementById(id);
  if (el) {
    el.style.opacity = 0;
    el.style.transition = "opacity 1s ease";
    setTimeout(() => (el.style.opacity = 1), 400 * i);
  }
});

  } catch (err) {
    console.error("⚠️ Perplexity failed:", err);
  }

    window.scrollTo({ top: document.getElementById("ai-insights").offsetTop - 50, behavior: "smooth" });
    setTimeout(() => (badge.style.opacity = "0"), 4000);
    setTimeout(() => badge.remove(), 5000);
  }

  // Hook into main report generator
  const oldCalc = window.calculateAndDisplayReport;
  window.calculateAndDisplayReport = async function() {
    if (typeof oldCalc === "function") await oldCalc();
    generateAIReportWithPerplexity();
  };
});

        let currentStep = 1;
        // Weights for the core pillars (C, I, J, G, K). B, H, E are simulated/minor.
        const WEIGHTS = { 'C': 0.25, 'G': 0.25, 'I': 0.25, 'J': 0.15, 'K': 0.10 };
        // Simulated scores for minor, non-assessed pillars
        const SIMULATED_SCORES = { 'B': 85, 'H': 80, 'E': 80 }; 

        // --- ADVANCED DIAGNOSTIC MATRIX ---
        // Maps the primary weakness category (I, J, G, K) and the severity of its score
        const DIAGNOSTIC_MATRIX = {
            'I': [ // Execution & Control Weakness (I1, I2)
                { score_min: 0, score_max: 30, root: 'Discipline Gap', impact: 'Inconsistent P&L', tag: 'Trade System Violation', narrative: 'Your core issue is the failure to trust your own system. You frequently override defined entry/exit rules, often resulting in missed targets or unnecessary losses. This sabotages your edge.' },
                { score_min: 31, score_max: 60, root: 'Emotional Gap', impact: 'Inconsistent P&L', tag: 'Premature Exit/Entry', narrative: 'The inability to manage small levels of stress or excitement causes you to deviate from exit plans (fear of losing profit) or chase entries (FOMO). Fix your execution first.' },
                { score_min: 61, score_max: 100, root: 'Minor Flaw', impact: 'Inconsistent P&L', tag: 'Technical Slip', narrative: 'Your execution is generally strong. Any minor weaknesses likely stem from occasional distraction or slight hesitations. Maintain focus.' }
            ],
            'J': [ // Planning & Consistency Weakness (J1, J2)
                { score_min: 0, score_max: 30, root: 'Structural Gap', impact: 'Strategy Clarity', tag: 'Absence of Edge/Plan', narrative: 'You lack a written, quantified plan, meaning every trade is an ad-hoc decision. Without predefined rules for SL, target, and entry, you are trading on luck and hope, not an edge.' },
                { score_min: 31, score_max: 60, root: 'Habit Gap', impact: 'Strategy Clarity', tag: 'Weak Preparation Routine', narrative: 'You have a plan, but fail to implement the planning process consistently (pre-trade checklist, R:R calculation). Inconsistency in preparation leads directly to inconsistency in results.' },
                { score_min: 61, score_max: 100, root: 'Minor Flaw', impact: 'Strategy Clarity', tag: 'Process Oversight', narrative: 'Your process is robust. Minor flaws might be due to rushing the preparation phase before high-conviction trades. Maintain your detailed checklist.' }
            ],
            'G': [ // Emotional Triggers Weakness (G1, G2, G3)
                { score_min: 0, score_max: 30, root: 'Emotional Gap', impact: 'Account Drawdown', tag: 'Loss-Driven Impulsivity', narrative: 'This is the most dangerous area. Your identity is tied to your P&L, causing immediate, aggressive attempts to recover losses (revenge trading) or chasing market momentum. You MUST separate your emotions from the trade outcome.' },
                { score_min: 31, score_max: 60, root: 'Mindset Gap', impact: 'Account Drawdown', tag: 'Anger/Anxiety Cycle', narrative: 'While you may not always violate hard risk rules, the emotional toll of losses (anger, anxiety) significantly affects the clarity of your next few trades. This creates psychological tilt.' },
                { score_min: 61, score_max: 100, root: 'Minor Flaw', impact: 'Emotional Resilience', tag: 'Post-Trade Fatigue', narrative: 'Your emotional control is strong. Minor issues are likely related to post-trade psychological fatigue on high-volatility days. Ensure long breaks after intense sessions.' }
            ],
            'K': [ // Growth & Reflection Weakness (K1, K2)
                { score_min: 0, score_max: 30, root: 'Accountability Gap', impact: 'Stagnant Growth', tag: 'Mistake Repetition', narrative: 'You do not close the feedback loop necessary for improvement. Without a journal or structured mistake review, you are destined to repeat costly errors. This prevents learning and growth.' },
                { score_min: 31, score_max: 60, root: 'Habit Gap', impact: 'Stagnant Growth', tag: 'Inconsistent Journaling', narrative: 'You understand the value of a journal but fail to maintain consistency or depth. Reviewing trades randomly is insufficient; you need weekly, structured analysis focused on behavioral and systemic failures.' },
                { score_min: 61, score_max: 100, root: 'Minor Flaw', impact: 'Growth Friction', tag: 'Lagging Data Collection', narrative: 'Your reflection habits are excellent. Minor issues might involve slightly lagging data collection or not spending enough time analyzing non-financial metrics (sleep, stress levels) alongside P&L.' }
            ],
        };

        // --- Step Management ---

        function updateProgressBar() {
            const totalSteps = 2;
            const progress = (currentStep - 1) / totalSteps * 100;
            document.getElementById('progress-fill').style.width = progress + '%';
        }

        function validateStep1() {
  const nameField = document.getElementById('name');
  
  if (!nameField.value.trim()) {
    nameField.reportValidity();  // shows the browser’s built-in “please fill out this field” tooltip
    nameField.focus();
    return;
  }

  // ✅ if valid, move to next step
  nextStep();
}

        function nextStep() {
            if (currentStep < 2) {
                document.getElementById(`step-${currentStep}`).classList.add('hidden');
                currentStep++;
                document.getElementById(`step-${currentStep}`).classList.remove('hidden');
                updateProgressBar();
            }
        }

        function prevStep() {
            if (currentStep > 1) {
                document.getElementById(`step-${currentStep}`).classList.add('hidden');
                currentStep--;
                document.getElementById(`step-${currentStep}`).classList.remove('hidden');
                updateProgressBar();
            }
        }
        
        // Helper function to map score to severity color class
        function getSeverityColor(severity) {
            // Returns Tailwind classes for the severity color accent
            if (severity >= 7) return 'severity-high border-l-red-600';
            if (severity >= 4) return 'severity-medium border-l-amber-500';
            return 'severity-low border-l-green-500';
        }

        function getSeverityTextColor(severity) {
             // Returns Tailwind class for text color
            if (severity >= 7) return 'text-red-600';
            if (severity >= 4) return 'text-amber-500';
            return 'text-green-600';
        }

        // --- Core Calculation and Report Generation ---

        function calculateAndDisplayReport() {
            // 1. Gather scores from the form
            const name = document.getElementById('name').value || 'Valued Trader';
            const experienceIndex = parseInt(document.getElementById('experience').value);
            
            // Pillar G: Emotional Triggers (g1, g2, g3) - Lower score is worse
            const g1 = parseInt(document.getElementById('g1').value);
            const g2 = parseInt(document.getElementById('g2').value);
            const g3 = parseInt(document.getElementById('g3').value);
            const G_Score = Math.round((g1 + g2 + g3) / 3);

            // Pillar J: Planning & Consistency (j1, j2) - Lower score is worse
            const j1 = parseInt(document.getElementById('j1').value);
            const j2 = parseInt(document.getElementById('j2').value);
            const J_Score = Math.round((j1 + j2) / 2);

            // Pillar I: Execution & Control (i1, i2) - Lower score is worse
            const i1 = parseInt(document.getElementById('i1').value);
            const i2 = parseInt(document.getElementById('i2').value);
            const I_Score = Math.round((i1 + i2) / 2);

            // Pillar K: Growth & Reflection (k1, k2) - Lower score is worse
            const k1 = parseInt(document.getElementById('k1').value);
            const k2 = parseInt(document.getElementById('k2').value);
            const K_Score = Math.round((k1 + k2) / 2);
            
            // Pillar C: Performance Metric (c1)
            const C_Score = parseInt(document.getElementById('c1').value);

            // Calculate B (Profile) score
            const B_Score = 100 - (experienceIndex * 10); // Simple proxy: less experience = lower profile score
            
            // Compile all scores (real and simulated)
            let scoreData = { 'B': B_Score, 'C': C_Score, 'I': I_Score, 'J': J_Score, 'G': G_Score, 'K': K_Score, ...SIMULATED_SCORES };
            
            // 2. Calculate Weighted Final Score
            let weightedSum = 0;
            for (const category in WEIGHTS) {
                weightedSum += scoreData[category] * WEIGHTS[category];
            }
            const finalScore = Math.round(weightedSum);

            // 3. Determine Final Classification
            let classification;
            if (finalScore >= 86) classification = "Elite Trader";
            else if (finalScore >= 71) classification = "Competent Trader";
            else if (finalScore >= 51) classification = "Developing Trader";
            else if (finalScore >= 31) classification = "Struggling Trader";
            else classification = "Critical Zone";

            // 4. Determine Trader Identity (Compare Discipline/Execution vs. Emotion/Reflection)
            const systemScore = I_Score + J_Score; // How well they follow a system
            const emotionScore = G_Score + K_Score; // How well they manage the human element
            const biasFactor = systemScore - emotionScore; 

            let traderIdentity; 
            if (biasFactor > 15) traderIdentity = "Systematic-Driver (Needs Flexibility)";
            else if (biasFactor < -15) traderIdentity = "Emotion-Driven (Needs Structure)";
            else traderIdentity = "Reactive-Trader (Needs Focus)";
            
            // 5. --- ADVANCED DIAGNOSTICS: FIND TOP WEAKNESS ---
            const pillarWeaknesses = [
                { category: 'G', name: 'Emotional Triggers', score: G_Score, narrative: 'Based on high reactivity to losses, FOMO, and emotional responses post-trade.' },
                { category: 'I', name: 'Execution & Control', score: I_Score, narrative: 'Based on overriding your system rules, taking trades outside your plan, and exiting valid setups early.' },
                { category: 'J', name: 'Planning & Consistency', score: J_Score, narrative: 'Based on lack of a written plan, and failing to consistently pre-define risk and targets.' },
                { category: 'K', name: 'Growth & Reflection', score: K_Score, narrative: 'Based on a weak feedback loop, poor journaling habits, and tendency to repeat mistakes.' },
            ];

            // Sort pillars by score (ascending) to find weaknesses
            pillarWeaknesses.sort((a, b) => a.score - b.score);
            const topWeakness = pillarWeaknesses[0]; 
            const topStrength = pillarWeaknesses[pillarWeaknesses.length - 1]; 

            // Check if scores are too high to warrant a diagnostic breakdown
            if (topWeakness.score >= 75) {
                document.getElementById('diagnostic-flow').classList.add('hidden');
                document.getElementById('top-weakness-title').innerText = "System Optimization Focus";
                document.getElementById('top-weakness-narrative').innerText = "Your scores indicate a strong psychological foundation. Your primary focus should now shift to advanced system optimization, reducing minor execution friction, and fine-tuning your edge (R:R ratio, win rate). You have successfully mitigated the human risks.";
                document.getElementById('action-plan-list').innerHTML = `<p><span class="font-extrabold text-indigo-400">1.</span> Deep dive R:R optimization.</p><p><span class="font-extrabold text-indigo-400">2.</span> Perform detailed review of 20 best/worst trades to find edge erosion.</p><p><span class="font-extrabold text-indigo-400">3.</span> Increase size slightly to test emotional capacity.</p>`;
                document.getElementById('diagnostic-error').classList.remove('hidden');
            } else {
                document.getElementById('diagnostic-flow').classList.remove('hidden');
                document.getElementById('diagnostic-error').classList.add('hidden');

                // A. Calculate Severity (1-10)
                const severity = Math.min(10, Math.max(1, Math.round((100 - topWeakness.score) / 10)));
                const severityColorClass = getSeverityColor(severity);
                const severityTextColorClass = getSeverityTextColor(severity);

                // B. Look up Diagnostic Data
                const categoryMatrix = DIAGNOSTIC_MATRIX[topWeakness.category];
                const diagnostic = categoryMatrix.find(d => topWeakness.score >= d.score_min && topWeakness.score <= d.score_max);
                
                // C. Inject Diagnostic Data
                if (diagnostic) {
                    document.getElementById('behavior-tag').innerText = diagnostic.tag;
                    document.getElementById('root-cause-layer').innerText = diagnostic.root;
                    document.getElementById('impact-type').innerText = diagnostic.impact;
                    document.getElementById('top-weakness-narrative').innerText = topWeakness.narrative + " " + diagnostic.narrative;
                    
                    // D. Apply Style based on Severity
                    document.getElementById('block-tag').className = 'diagnostic-block p-6 rounded-xl shadow-xl bg-white border-l-4 border-indigo-700';
                    document.getElementById('block-severity').className = 'diagnostic-block p-6 rounded-xl shadow-xl bg-white border-l-4 ' + severityColorClass;
                    document.getElementById('block-root-cause').className = 'diagnostic-block p-6 rounded-xl shadow-xl bg-white border-l-4 border-teal-700';
                    document.getElementById('block-impact-type').className = 'diagnostic-block p-6 rounded-xl shadow-xl bg-white border-l-4 border-purple-700';

                    // E. Inject Action Plan 
                    let actionPlan = '';
                    if (topWeakness.category === 'G' || topWeakness.category === 'I') {
                        actionPlan = `<p><span class="font-extrabold text-indigo-400">Goal:</span> Implement a **Hard Stop** against the **${diagnostic.root}**.</p>
                                      <p><span class="font-extrabold text-indigo-400">Day 1:</span> Write down and sign a commitment to the max daily loss limit.</p>
                                      <p><span class="font-extrabold text-indigo-400">Day 2-3:</span> Use a "cooling-off" timer (30 min minimum) every time you take a loss.</p>
                                      <p><span class="font-extrabold text-indigo-400">Day 4-7:</span> Shift focus from P&L to following your pre-trade checklist (100% compliance).</p>`;
                    } else if (topWeakness.category === 'J') {
                         actionPlan = `<p><span class="font-extrabold text-indigo-400">Goal:</span> Establish **Strategy Clarity** and **Routines**.</p>
                                      <p><span class="font-extrabold text-indigo-400">Day 1:</span> Document your 3 key entry rules and 3 exit rules on paper.</p>
                                      <p><span class="font-extrabold text-indigo-400">Day 2-3:</span> Practice calculating and setting R:R and SL on a demo account before *every* trade.</p>
                                      <p><span class="font-extrabold text-indigo-400">Day 4-7:</span> Develop a 15-minute pre-market routine (chart mark-up, risk check, mental state check).</p>`;
                    } else if (topWeakness.category === 'K') {
                        actionPlan = `<p><span class="font-extrabold text-indigo-400">Goal:</span> Close the **Feedback Loop** and **Master Accountability**.</p>
                                      <p><span class="font-extrabold text-indigo-400">Day 1:</span> Create a simple trade journal template with 4 fields: Entry Reason, Exit Reason, Emotion, What I did wrong.</p>
                                      <p><span class="font-extrabold text-indigo-400">Day 2-3:</span> Log every single trade immediately after closing it for the next 5 sessions.</p>
                                      <p><span class="font-extrabold text-indigo-400">Day 4-7:</span> Review your journal weekly, focusing only on the "What I did wrong" column and creating a single rule to fix it.</p>`;
                    }
                    document.getElementById('action-plan-list').innerHTML = actionPlan;
                    document.getElementById('severity-score').className = 'text-5xl font-extrabold ' + severityTextColorClass;
                }

                // Inject dynamic titles
                document.getElementById('top-weakness-title').innerText = `Primary Weakness: ${topWeakness.name} (${topWeakness.score}%)`;
                document.getElementById('severity-score').innerText = severity;
            }
// --- Save calculated metrics globally for the AI report ---
window.finalScore = finalScore;                   // e.g., 72
window.classificationLabel = classification; // e.g., "Competent Trader"
window.topWeakness = topWeakness.name;                 // e.g., { name: "Emotional Triggers", score: 42 }

            // 6. Inject General Data
            document.getElementById('report-name').innerText = `Report for ${name}`;
            document.getElementById('final-score').innerText = `${finalScore}%`;
            document.getElementById('final-classification').innerText = classification;
            document.getElementById('trader-identity').innerText = traderIdentity;
            document.getElementById('top-strength-title').innerText = topStrength.name;
            document.getElementById('top-strength-score').innerText = topStrength.score;
            
            // Inject Top 3 Weaknesses List
            document.getElementById('top-three-list').innerHTML = pillarWeaknesses.slice(0, 3).map((item, index) => 
                `<div class="flex justify-between items-center pb-1 border-b border-gray-200">
                    <span class="font-bold">${index + 1}. ${item.name}</span> 
                    <span class="px-3 py-1 text-sm font-semibold rounded-full bg-red-100 text-red-800 shadow-sm">${item.score}%</span>
                </div>`
            ).join('');

            // 7. Show the Report
            document.getElementById('assessment-container').style.display = 'none';
            document.getElementById('report-container').style.display = 'block';
        }

        // Initialize the progress bar on load
        window.onload = function() {
            updateProgressBar();
            // Listener for the slider in Step 1
            document.getElementById('c1').addEventListener('input', function() {
                document.getElementById('c1-value').innerText = this.value + '%';
            });
        };
    </script>
</body>
</html>
