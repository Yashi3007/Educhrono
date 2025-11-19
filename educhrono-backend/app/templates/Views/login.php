<?php include(APPPATH . 'views/includes/header.php'); ?>

<?php
if (session()->get('isLoggedIn')) {
    header('Location: ' . base_url('questionnaire'));
    exit;
}
?>

<style>
  body {
    font-family: 'Poppins', sans-serif;
    background: #f9fbff;
    color: #1e293b;
    margin: 0;
  }

  .login-section {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 80px 20px;
    min-height: calc(100vh - 250px);
    background: linear-gradient(to bottom, #f9fbff 0%, #eef3ff 100%);
  }

  .form-box {
    background: #ffffff;
    padding: 50px 40px;
    border-radius: 12px;
    width: 90%;
    max-width: 400px;
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
    border-top: 4px solid #2563eb;
  }

  h2 {
    text-align: center;
    color: #0f172a;
    font-size: 1.6rem;
    font-weight: 700;
    margin-bottom: 25px;
  }

  input {
    width: 100%;
    padding: 12px;
    margin: 10px 0 18px;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    font-size: 15px;
    transition: all 0.3s ease;
  }

  input:focus {
    border-color: #2563eb;
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
    outline: none;
  }

  button {
    width: 100%;
    background: #2563eb;
    color: white;
    border: none;
    padding: 12px;
    border-radius: 6px;
    font-size: 16px;
    cursor: pointer;
    transition: background 0.3s ease;
  }

  button:hover {
    background: #1d4ed8;
  }

  p {
    text-align: center;
    margin-top: 15px;
    color: #475569;
  }

  a {
    color: #2563eb;
    text-decoration: none;
    font-weight: 500;
  }

  a:hover {
    text-decoration: underline;
  }

  .error, .success {
    text-align: center;
    margin-bottom: 10px;
    font-weight: 500;
  }

  .error { color: #ef4444; }
  .success { color: #16a34a; }
</style>

<section class="login-section">
  <div class="form-box">
    <h2>Login</h2>

    <?php if (session()->getFlashdata('error')): ?>
      <div class="error"><?= session()->getFlashdata('error') ?></div>
    <?php endif; ?>

    <?php if (session()->getFlashdata('success')): ?>
      <div class="success"><?= session()->getFlashdata('success') ?></div>
    <?php endif; ?>

    <form method="post" action="<?= base_url('logging_in') ?>">
      <input type="email" name="email" placeholder="Email Address" required>
      <input type="password" name="password" placeholder="Password" required>
      <button type="submit">Login</button>
    </form>

    <p>Don’t have an account? <a href="<?= base_url('register') ?>">Register</a></p>
  </div>
</section>

<?php include(APPPATH . 'views/includes/footer.php'); ?>
