<?php
  $isLoggedIn = session()->get('isLoggedIn');
  $currentUrl = current_url(); // gets full URL
  $hideMenu = (strpos($currentUrl, 'login') !== false || strpos($currentUrl, 'register') !== false);
?>
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>MindXTrading | Transform Your Trading Psychology</title>
<link rel="stylesheet" href="<?= base_url('public/assets/css/style.css'); ?>">
<!-- Font Awesome Icons -->
<link
  rel="stylesheet"
  href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"
/>

  <!-- <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap" rel="stylesheet" /> -->
</head>
<body>
  <!-- Header -->
  <header id="navbar">
    <div class="container nav-content">
      <h1 class="logo">MindXTrading</h1>
      <?php if (!$hideMenu): ?>
      <nav>
        <ul>
          <li><a href="#home">Home</a></li>
          <li><a href="#about">About</a></li>
          <li><a href="#programs">Programs</a></li>
          <li><a href="#testimonials">Testimonials</a></li>
          <li><a href="#contact">Contact</a></li>
        </ul>
      </nav>
      <a href="/mindxtrading/login" class="cta-btn">Book a Clarity Call</a>
      <?php endif; ?>
    </div>
  </header>