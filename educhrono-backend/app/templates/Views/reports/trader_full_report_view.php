<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>MindXTrading | Report</title>

  <!-- Tailwind -->
  <script src="https://cdn.tailwindcss.com"></script>

  <!-- Fonts -->
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@100..900&family=Poppins:wght@400;500;600;700&display=swap');

    body {
      font-family: 'Poppins', 'Inter', sans-serif;
      background: linear-gradient(to bottom, #f9fbff 0%, #eef3ff 100%);
      color: #1e293b;
      margin: 0;
    }

    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-thumb { background: #4f46e5; border-radius: 4px; }

    .ctpa-section {
      max-width: 1100px;
      margin: 60px auto;
      background: #ffffff;
      border-radius: 12px;
      padding: 50px 40px;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
      border-top: 4px solid #2563eb;
    }

    .diagnostic-block {
      transition: all 0.3s ease;
      position: relative;
      z-index: 10;
    }

    .avoid-break {
      page-break-inside: avoid;
      break-inside: avoid;
    }

    .page-break {
      page-break-before: always;
      break-before: page;
    }

    /* ---------- PRINT OPTIMIZATION FOR PUPPETEER ---------- */
    @media print {
      html, body {
        zoom: 0.80; /* Perfect for A4 scale alignment */
        -webkit-print-color-adjust: exact !important;
        print-color-adjust: exact !important;
        background: #f9fafb !important;
      }

      section, .content-section {
        margin-bottom: 45px !important;
        padding: 25px 45px !important;
        page-break-inside: avoid !important;
      }

      .rounded-2xl, .shadow-lg, .shadow-xl, .shadow-2xl {
        transform: scale(0.98);
        margin: 10px 0;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05) !important;
      }

      .grid { gap: 24px !important; }

      h1, h2, h3 {
        line-height: 1.3;
        margin-bottom: 14px !important;
      }

      p {
        line-height: 1.7;
        font-size: 15px;
      }

      .bg-indigo-50, .bg-red-50, .bg-green-50, .bg-emerald-50, .bg-teal-50, .bg-gray-100 {
        background-color: #f8fafc !important;
        border: 1px solid #e2e8f0 !important;
        padding: 24px !important;
      }

      @page {
        size: A4;
        margin: 40px 30px 60px 30px;
      }
    }
  </style>
</head>

<body class="bg-gray-50">
  <!-- Header -->
  <div id="assessment-container" class="max-w-4xl mx-auto p-4 sm:p-8 pt-10">
    <header class="text-center mb-10">
      <h1 class="text-3xl sm:text-4xl font-extrabold text-indigo-700">C.T.P.A.</h1>
      <h2 class="text-xl sm:text-2xl font-semibold text-gray-800 mt-1">Advanced Trader Diagnostic</h2>
      <div id="progress-bar" class="w-full bg-gray-200 rounded-full h-2.5 mt-4">
        <div id="progress-fill" class="bg-indigo-500 h-2.5 rounded-full transition-all duration-300" style="width: 0%;"></div>
      </div>
    </header>

    <!-- Main Report -->
    <div id="report-container" class="max-w-6xl mx-auto p-4 sm:p-10 bg-white shadow-2xl rounded-3xl my-8">
      <div class="text-center mb-12">
        <h1 class="text-4xl sm:text-5xl font-extrabold text-gray-800">Your Basic Diagnostic Report</h1>
        <p class="text-xl text-indigo-600 mt-2" id="report-name"><?= esc($report['name'] ?? 'Trader Report') ?></p>
      </div>

      <!-- High Impact Snapshot -->
      <section id="high-impact" class="content-section">
        <h2 class="text-3xl font-bold text-gray-700 mb-6 border-b pb-2">High-Impact Snapshot</h2>
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-12">
          <!-- Final Score -->
          <div class="bg-indigo-50 p-6 rounded-2xl text-center shadow-lg border-b-4 border-indigo-600 avoid-break">
            <span class="text-4xl font-extrabold text-indigo-700 block mb-2">⭐</span>
            <p class="text-lg font-semibold text-gray-600">Final CTPA Score</p>
            <div class="text-6xl font-extrabold mt-2 text-indigo-800" id="final-score"><?= esc($report['final_score'] ?? '--') ?>%</div>
            <p class="text-xl font-bold mt-1" id="final-classification"><?= esc($report['classification'] ?? '--') ?></p>
          </div>

          <!-- Trader Identity -->
          <div class="bg-red-50 p-6 rounded-2xl text-center shadow-lg border-b-4 border-red-600 avoid-break">
            <span class="text-4xl font-extrabold text-red-700 block mb-2">🧠</span>
            <p class="text-lg font-semibold text-gray-600">Trader Identity Bias</p>
            <p class="text-2xl font-extrabold mt-3 text-red-800" id="trader-identity"><?= esc($report['trader_identity'] ?? '--') ?></p>
            <p class="text-sm mt-2 text-gray-500">How decisions are currently driven.</p>
          </div>

          <!-- Top Strength -->
          <div class="bg-teal-50 p-6 rounded-2xl text-center shadow-lg border-b-4 border-teal-600 avoid-break">
            <span class="text-4xl font-extrabold text-teal-700 block mb-2">✅</span>
            <p class="text-lg font-semibold text-gray-600">Top Strength Category</p>
            <p class="text-2xl font-extrabold mt-3 text-teal-800" id="top-strength-title"><?= esc($report['top_strength'] ?? '--') ?></p>
            <p class="text-sm mt-2 text-gray-500">Score: <span id="top-strength-score"><?= esc($report['top_strength_score'] ?? '--') ?></span>%</p>
          </div>
        </div>
      </section>

      <!-- Critical Gap Diagnostic -->
      <section id="critical-gap" class="content-section">
        <h2 class="text-3xl font-bold text-gray-700 mb-6 border-b pb-2">Critical Gap Diagnostic: Layering the Root Cause</h2>
        <div class="grid grid-cols-1 lg:grid-cols-4 gap-6 mb-10">
          <?php
            $layers = [
              ['Layer 1', 'Behavior Tag (Symptom)', $report['behavior_tag'] ?? '--', 'The surface-level action costing money.', 'text-indigo-700'],
              ['Layer 2', 'Severity (1–10)', $report['severity_score'] ?? '--', 'How critical this weakness is.', 'text-red-600'],
              ['Layer 3', 'Root Cause Layer (Focus)', $report['root_cause_layer'] ?? '--', 'The fundamental psychological trigger.', 'text-teal-700'],
              ['Layer 4', 'Impact Type (Consequence)', $report['impact_type'] ?? '--', 'The resulting damage to your P&L.', 'text-purple-700']
            ];
            foreach ($layers as $layer) {
              echo "<div class='diagnostic-block p-6 rounded-xl border-l-4 border-gray-300 shadow-xl bg-white avoid-break'>
                      <span class='text-sm font-extrabold text-gray-400 mr-2'>$layer[0]</span>
                      <p class='text-xs font-bold uppercase text-gray-600'>$layer[1]</p>
                      <p class='text-2xl lg:text-3xl font-extrabold mt-1 $layer[4]'>$layer[2]</p>
                      <p class='text-sm text-gray-500 mt-2'>$layer[3]</p>
                    </div>";
            }
          ?>
        </div>
      </section>

      <!-- Summary + Action Plan -->
      <section id="summary" class="content-section">
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mt-12">
          <div class="bg-gray-100 p-8 rounded-2xl shadow-xl avoid-break">
            <p class="text-xl font-bold text-gray-800 mb-4"><?= esc($report['top_weakness_title'] ?? '--') ?></p>
            <p class="text-gray-600 leading-relaxed"><?= nl2br(esc($report['top_weakness_narrative'] ?? '--')) ?></p>
          </div>

          <div class="bg-gray-900 text-white p-8 rounded-2xl shadow-2xl border-b-4 border-indigo-500 avoid-break">
            <p class="text-2xl font-bold mb-4 text-indigo-400">7-Day Action Plan</p>
            <div class="space-y-3 text-lg"><?= nl2br(esc($report['action_plan_list'] ?? 'No actions available.')) ?></div>
          </div>
        </div>
      </section>

      <!-- AI Insights -->
      <section id="ai-insights" class="content-section space-y-6 mt-10">
        <!-- Analyst Narrative -->
        <div class="rounded-2xl p-6 shadow-lg bg-indigo-50 border-l-4 border-indigo-500 leading-relaxed avoid-break">
          <h3 class="text-xl font-bold text-indigo-700 mb-3 flex items-center gap-2">🧠 Analyst’s Narrative Analysis</h3>
          <div class="text-gray-800 prose prose-indigo max-w-none space-y-3">
            <?php
              $narrative = esc($report['ai_narrative'] ?? '--');
              $narrative = preg_replace(['/\*\*(.*?)\*\*/', '/\*(.*?)\*/'], ['<strong>$1</strong>', '<em>$1</em>'], $narrative);
              $sentences = preg_split('/(?<=\.|\?|!)\s+/', trim($narrative));
              echo "<ul class='list-disc pl-6 marker:text-indigo-600'>";
              foreach ($sentences as $s) if (strlen(trim($s)) > 0) echo "<li class='mb-2 text-justify'>$s</li>";
              echo "</ul>";
            ?>
          </div>
        </div>

        <!-- Personalized Action Plan -->
        <div class="rounded-2xl p-6 shadow-lg bg-emerald-50 border-l-4 border-emerald-500 leading-relaxed avoid-break">
          <h3 class="text-xl font-bold text-emerald-700 mb-3 flex items-center gap-2">⚙️ Personalized Action Plan</h3>
          <div class="text-gray-800 prose prose-emerald max-w-none">
            <?= nl2br(preg_replace(
                ['/\*\*(.*?)\*\*/', '/\*(.*?)\*/'],
                ['<strong>$1</strong>', '<em>$1</em>'],
                esc($report['ai_action_plan'] ?? '--')
            )) ?>
          </div>
        </div>

        <!-- Next Steps -->
        <div class="rounded-2xl p-6 shadow-lg bg-green-50 border-l-4 border-green-500 leading-relaxed avoid-break">
          <h3 class="text-xl font-bold text-green-700 mb-3 flex items-center gap-2">🚀 Next Steps</h3>
          <div class="text-gray-800 prose prose-green max-w-none">
            <?= nl2br(preg_replace(
                ['/\*\*(.*?)\*\*/', '/\*(.*?)\*/'],
                ['<strong>$1</strong>', '<em>$1</em>'],
                esc($report['ai_next_steps'] ?? '--')
            )) ?>
          </div>
        </div>
      </section>
    </div>
  </div>
</body>
</html>
