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

  .register-section {
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
    max-width: 420px;
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

  .error, .message, #strength {
    text-align: center;
    font-size: 14px;
    margin-bottom: 8px;
  }

  .error { color: #ef4444; }
  .message { color: #16a34a; }
  #strength { font-weight: 500; }
</style>

<section class="register-section">
  <div class="form-box">
    <h2>Register</h2>

    <!-- Success message -->
    <?php if (session()->getFlashdata('success')): ?>
      <div class="message"><?= session()->getFlashdata('success') ?></div>
    <?php endif; ?>

    <!-- Validation errors -->
    <?php if(isset($validation)): ?>
      <div class="error">
        <?= $validation->listErrors() ?>
      </div>
    <?php endif; ?>

    <form method="post" action="<?= base_url('registeration') ?>">
      <input type="text" name="fullname" placeholder="Full Name" value="<?= old('fullname') ?>" required>
      <input type="email" name="email" placeholder="Email Address" value="<?= old('email') ?>" required>
      <input type="text" name="mobile" placeholder="Mobile Number" value="<?= old('mobile') ?>" required>

      <input type="password" id="password" name="password" placeholder="Enter Password" required>
      <div id="strength"></div>

      <input type="password" id="confirm_password" name="confirm_password" placeholder="Confirm Password" required>
      <div id="passwordMessage" class="error"></div>

      <button type="submit">Register</button>
    </form>

    <p>Already have an account? <a href="<?= base_url('login') ?>">Login</a></p>
  </div>
</section>

<script>
  const password = document.getElementById('password');
  const confirm_password = document.getElementById('confirm_password');
  const passwordMessage = document.getElementById('passwordMessage');
  const strengthDiv = document.getElementById('strength');
  const form = document.querySelector('form');

  password.addEventListener('input', () => {
    const value = password.value;
    let strength = '';

    if (value.length < 8) {
      strength = '❌ Too short (min 8 chars)';
      strengthDiv.style.color = '#ef4444';
    } else if (!/[A-Z]/.test(value) || !/\d/.test(value) || !/[!@#$%^&*]/.test(value)) {
      strength = '⚠️ Weak: add uppercase, number, special char';
      strengthDiv.style.color = '#eab308';
    } else {
      strength = '✅ Strong password';
      strengthDiv.style.color = '#16a34a';
    }
    strengthDiv.textContent = strength;
  });

  form.addEventListener('submit', (e) => {
    if (password.value !== confirm_password.value) {
      e.preventDefault();
      passwordMessage.textContent = "Passwords do not match!";
      return false;
    }
    passwordMessage.textContent = "";
  });
</script>

<?php include(APPPATH . 'views/includes/footer.php'); ?>
