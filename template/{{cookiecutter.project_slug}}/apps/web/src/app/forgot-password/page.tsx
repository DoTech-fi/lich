'use client';

/**
 * Forgot Password Page
 * Password reset request form
 */

import { useState } from 'react';
import Link from 'next/link';
import styles from '../login/auth.module.css';

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      // TODO: Implement password reset API call
      await new Promise(resolve => setTimeout(resolve, 1000)); // Simulated delay
      setSuccess(true);
    } catch (err: any) {
      setError(err.message || '{% if cookiecutter.default_language == "fa" %}خطایی رخ داد{% else %}An error occurred{% endif %}');
    } finally {
      setIsLoading(false);
    }
  };

  if (success) {
    return (
      <div className={styles.container}>
        <div className={styles.card}>
          <div className={styles.header}>
            <h1 className={styles.logo}>📧</h1>
            <h2 className={styles.title}>
              {% if cookiecutter.default_language == 'fa' %}ایمیل ارسال شد{% else %}Check your email{% endif %}
            </h2>
            <p className={styles.subtitle}>
              {% if cookiecutter.default_language == 'fa' %}
              لینک بازیابی رمز عبور به ایمیل شما ارسال شد
              {% else %}
              We've sent a password reset link to your email
              {% endif %}
            </p>
          </div>

          <div className={styles.success}>
            {% if cookiecutter.default_language == 'fa' %}
            اگر ایمیل را دریافت نکردید، پوشه اسپم را بررسی کنید
            {% else %}
            If you don't see the email, check your spam folder
            {% endif %}
          </div>

          <Link href="/login" className={styles.button}>
            {% if cookiecutter.default_language == 'fa' %}بازگشت به ورود{% else %}Back to login{% endif %}
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <div className={styles.card}>
        <div className={styles.header}>
          <h1 className={styles.logo}>🔑</h1>
          <h2 className={styles.title}>
            {% if cookiecutter.default_language == 'fa' %}فراموشی رمز عبور{% else %}Forgot password?{% endif %}
          </h2>
          <p className={styles.subtitle}>
            {% if cookiecutter.default_language == 'fa' %}
            ایمیل خود را وارد کنید تا لینک بازیابی ارسال شود
            {% else %}
            Enter your email and we'll send you a reset link
            {% endif %}
          </p>
        </div>

        {error && (
          <div className={styles.error}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className={styles.form}>
          <div className={styles.field}>
            <label htmlFor="email" className={styles.label}>
              {% if cookiecutter.default_language == 'fa' %}ایمیل{% else %}Email{% endif %}
            </label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className={styles.input}
              placeholder="{% if cookiecutter.default_language == 'fa' %}ایمیل خود را وارد کنید{% else %}Enter your email{% endif %}"
              required
              disabled={isLoading}
            />
          </div>

          <button 
            type="submit" 
            className={styles.button}
            disabled={isLoading}
          >
            {isLoading ? (
              <span className={styles.spinner}>⏳</span>
            ) : (
              '{% if cookiecutter.default_language == "fa" %}ارسال لینک بازیابی{% else %}Send reset link{% endif %}'
            )}
          </button>
        </form>

        <div className={styles.footer}>
          <Link href="/login" className={styles.link}>
            ← {% if cookiecutter.default_language == 'fa' %}بازگشت به ورود{% else %}Back to login{% endif %}
          </Link>
        </div>
      </div>
    </div>
  );
}
