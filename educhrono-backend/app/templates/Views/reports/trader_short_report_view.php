<!DOCTYPE html>
<html lang="en">
<head>
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
        .step-container.hidden { display: block; opacity: 0; }
        .custom-range-slider { -webkit-appearance: none; appearance: none; width: 100%; height: 8px; background: #d1d5db; outline: none; opacity: 0.9; transition: opacity .15s; border-radius: 4px; }
        .custom-range-slider::-webkit-slider-thumb { -webkit-appearance: none; appearance: none; width: 20px; height: 20px; border-radius: 50%; background: #4f46e5; cursor: pointer; box-shadow: 0 0 5px rgba(0,0,0,0.2); border: 3px solid #fff; }
        #report-container { min-height: 100vh; display: block; }

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

    </style>
<style>
  @media print {
    .page-break {
      page-break-before: always;
    }

    .avoid-break {
      page-break-inside: avoid;
    }
  }

  /* Also helpful for Puppeteer */
  .avoid-break {
    break-inside: avoid;
  }

  .page-break {
    break-before: page;
  }
</style>

</head>
<body class="bg-gray-50">
    <!-- Assessment Container (Steps) -->
    <div id="assessment-container" class="max-w-4xl mx-auto p-4 sm:p-8 pt-10">
        <header class="text-center mb-10">
            <h1 class="text-3xl sm:text-4xl font-extrabold text-indigo-700">C.T.P.A.</h1>
            <h2 class="text-xl sm:text-2xl font-semibold text-gray-800 mt-1">Advanced Trader Diagnostic</h2>
            <div id="progress-bar" class="w-full bg-gray-200 rounded-full h-2.5 mt-4">
                <div id="progress-fill" class="bg-indigo-500 h-2.5 rounded-full transition-all duration-300" style="width: 0%;"></div>
            </div>
        </header>

    <!-- Report Container -->
<div id="report-container" class="max-w-6xl mx-auto p-4 sm:p-10 bg-white shadow-2xl rounded-3xl my-8">
    <div class="text-center mb-12">
        <h1 class="text-4xl sm:text-5xl font-extrabold text-gray-800">
            Your Basic Diagnostic Report
        </h1>
        <p class="text-xl text-indigo-600 mt-2" id="report-name">
            <?= esc($report['name'] ?? 'Trader Report') ?>
        </p>
    </div>

    <!-- Section 1: Executive Summary -->
    <h2 class="text-3xl font-bold text-gray-700 mb-6 border-b pb-2">High-Impact Snapshot</h2>
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-12">
        
        <!-- Final Score -->
        <div class="bg-indigo-50 p-6 rounded-2xl text-center shadow-lg border-b-4 border-indigo-600 avoid-break">
            <span class="text-4xl font-extrabold text-indigo-700 block mb-2">⭐</span>
            <p class="text-lg font-semibold text-gray-600">Final CTPA Score</p>
            <div class="text-6xl font-extrabold mt-2 text-indigo-800" id="final-score">
                <?= esc($report['final_score'] ?? '--') ?>%
            </div>
            <p class="text-xl font-bold mt-1" id="final-classification">
                <?= esc($report['classification'] ?? '--') ?>
            </p>
        </div>

        <!-- Trader Identity -->
        <div class="bg-red-50 p-6 rounded-2xl text-center shadow-lg border-b-4 border-red-600 avoid-break">
            <span class="text-4xl font-extrabold text-red-700 block mb-2">🧠</span>
            <p class="text-lg font-semibold text-gray-600">Trader Identity Bias</p>
            <p class="text-2xl font-extrabold mt-3 text-red-800" id="trader-identity">
                <?= esc($report['trader_identity'] ?? '--') ?>
            </p>
            <p class="text-sm mt-2 text-gray-500">How decisions are currently driven.</p>
        </div>

        <!-- Top Strength -->
        <div class="bg-teal-50 p-6 rounded-2xl text-center shadow-lg border-b-4 border-teal-600 avoid-break">
            <span class="text-4xl font-extrabold text-teal-700 block mb-2">✅</span>
            <p class="text-lg font-semibold text-gray-600">Top Strength Category</p>
            <p class="text-2xl font-extrabold mt-3 text-teal-800" id="top-strength-title">
                <?= esc($report['top_strength'] ?? '--') ?>
            </p>
            <p class="text-sm mt-2 text-gray-500">
                Score: <span id="top-strength-score"><?= esc($report['top_strength_score'] ?? '--') ?></span>%
            </p>
        </div>
    </div>

    <!-- Diagnostic Flow -->
    <h2 class="text-3xl font-bold text-gray-700 mb-6 border-b pb-2">
        Critical Gap Diagnostic: Layering the Root Cause
    </h2>

    <div class="grid grid-cols-1 lg:grid-cols-4 gap-6 relative mb-10">
        <div class="diagnostic-block p-6 rounded-xl border-l-4 border-gray-300 shadow-xl bg-white avoid-break">
            <span class="text-sm font-extrabold text-gray-400 mr-2">Layer 1</span>
            <p class="text-xs font-bold uppercase text-gray-600">Behavior Tag (Symptom)</p>
            <p class="text-3xl font-extrabold mt-1 text-indigo-700">
                <?= esc($report['behavior_tag'] ?? '--') ?>
            </p>
            <p class="text-sm text-gray-500 mt-2">The surface-level action costing money.</p>
        </div>

        <div class="diagnostic-block p-6 rounded-xl border-l-4 border-gray-300 shadow-xl bg-white avoid-break">
            <span class="text-sm font-extrabold text-gray-400 mr-2">Layer 2</span>
            <p class="text-xs font-bold uppercase text-gray-600">Severity (1–10)</p>
            <p class="text-5xl font-extrabold text-red-600">
                <?= esc($report['severity_score'] ?? '--') ?>
            </p>
            <p class="text-sm text-gray-500 mt-2">How critical this weakness is.</p>
        </div>

        <div class="diagnostic-block p-6 rounded-xl border-l-4 border-gray-300 shadow-xl bg-white avoid-break">
            <span class="text-sm font-extrabold text-gray-400 mr-2">Layer 3</span>
            <p class="text-xs font-bold uppercase text-gray-600">Root Cause Layer (Focus)</p>
            <p class="text-xl font-extrabold mt-1 text-teal-700">
                <?= esc($report['root_cause_layer'] ?? '--') ?>
            </p>
            <p class="text-sm text-gray-500 mt-2">The fundamental psychological trigger.</p>
        </div>

        <div class="diagnostic-block p-6 rounded-xl border-l-4 border-gray-300 shadow-xl bg-white avoid-break">
            <span class="text-sm font-extrabold text-gray-400 mr-2">Layer 4</span>
            <p class="text-xs font-bold uppercase text-gray-600">Impact Type (Consequence)</p>
            <p class="text-xl font-extrabold mt-1 text-purple-700">
                <?= esc($report['impact_type'] ?? '--') ?>
            </p>
            <p class="text-sm text-gray-500 mt-2">The resulting damage to your P&L.</p>
        </div>
    </div>

    <!-- Summary & AI Sections -->
  <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mt-12">
        <div class="bg-gray-100 p-8 rounded-2xl shadow-xl avoid-break">
            <p class="text-xl font-bold text-gray-800 mb-4" id="top-weakness-title">
                <?= esc($report['top_weakness_title'] ?? '--') ?>
            </p>
            <p class="text-gray-600 leading-relaxed" id="top-weakness-narrative">
                <?= nl2br(esc($report['top_weakness_narrative'] ?? '--')) ?>
            </p>
        </div>

        <div class="bg-gray-900 text-white p-8 rounded-2xl shadow-2xl border-b-4 border-indigo-500 avoid-break">
            <p class="text-2xl font-bold mb-4 text-indigo-400 flex items-center">
                7-Day Action Plan
            </p>
            <div class="space-y-3 text-lg" id="action-plan-list">
                <?= nl2br(esc($report['action_plan_list'] ?? 'No actions available.')) ?>
            </div>
        </div>
    </div>

    <!-- AI Insight Section -->
    <section class="mt-10 space-y-6" id="ai-insights">

  <!-- Analyst Narrative -->
    <div class="rounded-2xl p-6 shadow-lg bg-indigo-50 border-l-4 border-indigo-500 leading-relaxed page-break avoid-break">
  <h3 class="text-xl font-bold text-indigo-700 mb-3 flex items-center gap-2">
    🧠 Analyst’s Narrative Analysis
  </h3>

  <div class="text-gray-800 prose prose-indigo max-w-none space-y-3 ">
    <?php
      $narrative = esc($report['ai_narrative'] ?? '--');

      // Convert markdown-like **bold** and *italic*
      $narrative = preg_replace(
          ['/\*\*(.*?)\*\*/', '/\*(.*?)\*/'],
          ['<strong>$1</strong>', '<em>$1</em>'],
          $narrative
      );

      // Split into sentences/points
      $sentences = preg_split('/(?<=\.|\?|!)\s+/', trim($narrative));

      echo "<ul class='list-disc pl-6 marker:text-indigo-600'>";
      foreach ($sentences as $s) {
          if (strlen(trim($s)) > 0) {
              echo "<li class='mb-2 text-justify'>$s</li>";
          }
      }
      echo "</ul>";
    ?>
  </div>
 </div>

  </section>

  </div>

</div>

</body>
</html>
