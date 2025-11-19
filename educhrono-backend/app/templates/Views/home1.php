<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>MindX Trading</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    * { margin:0; padding:0; box-sizing:border-box; scroll-behavior:smooth; }
    body { font-family: 'Poppins', sans-serif; background:#0f172a; color:white; }

    header {
      background: linear-gradient(135deg, #1e3a8a, #0ea5e9);
      padding: 100px 20px;
      text-align: center;
    }
    header h1 { font-size: 48px; color:#fff; margin-bottom:10px; }
    header p { font-size: 20px; color:#e0f2fe; margin-bottom:30px; }
    .btn {
      background:#22c55e; color:#fff; border:none; padding:15px 40px;
      border-radius:6px; cursor:pointer; font-size:18px; transition:0.3s;
    }
    .btn:hover { background:#16a34a; }

    section { padding:80px 20px; text-align:center; max-width:1000px; margin:auto; }
    section h2 { font-size:36px; color:#38bdf8; margin-bottom:20px; }
    section p { font-size:18px; line-height:1.8; color:#cbd5e1; }

    .tips {
      display:grid; grid-template-columns:repeat(auto-fit, minmax(250px, 1fr)); gap:20px; margin-top:40px;
    }
    .tip {
      background:#1e293b; padding:25px; border-radius:10px; box-shadow:0 4px 10px rgba(0,0,0,0.3);
      transition: transform .3s ease;
    }
    .tip:hover { transform:translateY(-5px); }
    .tip h3 { color:#22d3ee; margin-bottom:10px; }
    .tip p { color:#e2e8f0; font-size:16px; }

    footer {
      background:#020617; color:#94a3b8; padding:30px; text-align:center;
    }

    /* Smooth fade animation */
    @keyframes fadeInUp { from {opacity:0; transform:translateY(20px);} to {opacity:1; transform:translateY(0);} }
    header, section { animation:fadeInUp 0.7s ease-in-out; }
  </style>
</head>
<body>

  <!-- Hero Section -->
  <header>
    <h1>MindX Trading</h1>
    <p>Empowering Traders with Smart Insights and Real-Time Analysis</p>
    <a href="register"><button class="btn">Register Here</button></a>
  </header>

  <!-- About Section -->
  <section id="about">
    <h2>About Us</h2>
    <p>
      MindX Trading is a next-generation financial insights platform designed to help traders make data-driven decisions. 
      Our mission is to simplify market analytics and deliver accurate trading signals that enhance profitability.
      With expert mentors and AI-powered score prediction, we empower individuals to trade with confidence.
    </p>
  </section>

  <!-- Trading Tips Section -->
  <section id="tips">
    <h2>Trading Tips</h2>
    <div class="tips">
      <div class="tip">
        <h3>1. Manage Risk Wisely</h3>
        <p>Never risk more than 2% of your total capital on a single trade. Discipline is the key to survival in the markets.</p>
      </div>
      <div class="tip">
        <h3>2. Follow the Trend</h3>
        <p>Trade in the direction of the prevailing market trend — the trend is your friend until it ends!</p>
      </div>
      <div class="tip">
        <h3>3. Keep Emotions Aside</h3>
        <p>Stay calm and logical. Avoid impulsive decisions based on fear or greed; let data guide your trades.</p>
      </div>
    </div>
  </section>

  <!-- Register Section -->
  <section id="register">
    <h2>Join the MindX Community</h2>
    <p>Stay updated with our latest strategies, trading insights, and market analysis tools.</p>
    <a href="mailto:info@mindxtrading.com"><button class="btn">Register Now</button></a>
  </section>

  <footer>
    <p>© <?= date('Y') ?> MindX Trading. All rights reserved.</p>
  </footer>

</body>
</html>
