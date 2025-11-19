<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>MindXTrading Report</title>
  <style>
    * {
      box-sizing: border-box;
      font-family: 'DejaVu Sans', sans-serif;
    }

    body {
      margin: 0;
      padding: 30px;
      background-color: #f8f9fa;
      color: #333;
      font-size: 13px;
      line-height: 1.5;
    }

    h1, h2, h3 {
      color: #1a1a1a;
      margin-bottom: 6px;
    }

    .report-container {
      max-width: 800px;
      margin: 0 auto;
      background: #fff;
      border-radius: 10px;
      padding: 25px 35px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }

    .report-header {
      text-align: center;
      margin-bottom: 25px;
      padding-bottom: 10px;
      border-bottom: 2px solid #e3e3e3;
    }

    .report-header h1 {
      font-size: 22px;
      font-weight: 700;
      color: #212121;
    }

    .section {
      margin-bottom: 18px;
      border-radius: 8px;
      padding: 18px 22px;
      border: 1px solid #e6e6e6;
    }

    .section-title {
      font-size: 16px;
      font-weight: 600;
      margin-bottom: 8px;
      color: #111;
      border-left: 4px solid #007bff;
      padding-left: 10px;
    }

    .highlight-box {
      border-radius: 10px;
      padding: 15px;
      text-align: center;
      font-size: 26px;
      font-weight: 700;
      margin: 10px 0;
    }

    .highlight-blue {
      background: #edf1ff;
      color: #2335d5;
      border: 1px solid #bfc7f9;
    }

    .highlight-red {
      background: #fff1f1;
      color: #b51c1c;
      border: 1px solid #f3cccc;
    }

    .highlight-green {
      background: #e8f8f0;
      color: #198754;
      border: 1px solid #b6e2c3;
    }

    .ai-section {
      margin-top: 25px;
      background: #fdfdfd;
      border-left: 4px solid #17a2b8;
      padding: 18px 22px;
      font-size: 13px;
    }

    .ai-section h3 {
      color: #0d6efd;
      font-size: 14px;
      margin-bottom: 6px;
    }

    .ai-section p {
      margin-bottom: 6px;
      text-align: justify;
    }

    .ai-section ul {
      margin: 6px 0;
      padding-left: 18px;
    }

    .footer-note {
      text-align: center;
      font-size: 11px;
      color: #777;
      border-top: 1px solid #ddd;
      margin-top: 20px;
      padding-top: 10px;
    }
  </style>
</head>
<body>
  <div class="report-container">
<?php if (!empty($shortSection)): ?>
<div class="section ai-section">
  <h3>AI-Generated Diagnostic Summary</h3>
  <?= $shortSection ?>
</div>
<?php endif; ?>

<?php if (!empty($fullSection)): ?>
<div class="section ai-section">
  <h3>AI-Generated Full Report</h3>
  <?= $fullSection ?>
</div>
<?php endif; ?>

    <div class="footer-note">
      © <?= date('Y') ?> MindXTrading. All rights reserved.
    </div>
  </div>
</body>
</html>
