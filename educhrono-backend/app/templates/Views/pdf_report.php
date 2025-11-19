<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title><?= esc($title ?? 'AI Report') ?></title>
</head>
<body>
  <main class="pdf-content">

    <?php if (!empty($narrative)): ?>
      <section class="section-box ai-section compact-block" id="ai-narrative">
        <h2>Analyst’s Narrative Analysis</h2>
        <div class="ai-body"><?= $narrative ?></div>
      </section>
    <?php endif; ?>

    <?php if (!empty($actionPlan)): ?>
      <section class="section-box ai-section compact-block" id="ai-action-plan">
        <h2>Personalized Action Plan</h2>
        <div class="ai-body"><?= $actionPlan ?></div>
      </section>
    <?php endif; ?>

    <?php if (!empty($nextSteps)): ?>
      <section class="section-box ai-section compact-block" id="ai-next-steps">
        <h2>Next Steps: Turning Insight Into Action</h2>
        <div class="ai-body"><?= $nextSteps ?></div>
      </section>
    <?php endif; ?>

  </main>
</body>
</html>
