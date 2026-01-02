'use client';

/**
 * Register Page
 * User registration form with validation
 */

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
{%- if cookiecutter.auth_strategy == 'jwt_builtin' %}
import { useAuth } from '@/context/AuthContext';
{%- endif %}
import styles from '../login/auth.module.css';

export default function RegisterPage() {
  const router = useRouter();
  {%- if cookiecutter.auth_strategy == 'jwt_builtin' %}
  const { register } = useAuth();
  {%- endif %}
  
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    firstName: '',
    lastName: '',
  });
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [passwordStrength, setPasswordStrength] = useState(0);

  const checkPasswordStrength = (password: string) => {
    let strength = 0;
    if (password.length >= 8) strength++;
    if (/[A-Z]/.test(password)) strength++;
    if (/[a-z]/.test(password)) strength++;
    if (/[0-9]/.test(password)) strength++;
    if (/[^A-Za-z0-9]/.test(password)) strength++;
    setPasswordStrength(strength);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    
    if (name === 'password') {
      checkPasswordStrength(value);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    // Validation
    if (formData.password !== formData.confirmPassword) {
      setError('{% if cookiecutter.default_language == "fa" %}رمز عبور و تکرار آن مطابقت ندارند{% else %}Passwords do not match{% endif %}');
      return;
    }

    if (formData.password.length < 8) {
      setError('{% if cookiecutter.default_language == "fa" %}رمز عبور باید حداقل ۸ کاراکتر باشد{% else %}Password must be at least 8 characters{% endif %}');
      return;
    }

    setIsLoading(true);

    try {
      {%- if cookiecutter.auth_strategy == 'jwt_builtin' %}
      await register({
        email: formData.email,
        password: formData.password,
        first_name: formData.firstName,
        last_name: formData.lastName,
      });
      router.push('/login?registered=true');
      {%- elif cookiecutter.auth_strategy == 'keycloak' %}
      // Redirect to Keycloak registration
      const config = await fetch('/api/auth/config').then(r => r.json());
      window.location.href = `${config.keycloak_url}/realms/${config.realm}/protocol/openid-connect/registrations?client_id=${config.client_id}&redirect_uri=${window.location.origin}/auth/callback&response_type=code&scope=openid`;
      {%- else %}
      router.push('/dashboard');
      {%- endif %}
    } catch (err: any) {
      setError(err.message || '{% if cookiecutter.default_language == "fa" %}خطا در ثبت‌نام{% else %}Registration failed{% endif %}');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={styles.container}>
      <div className={styles.card}>
        <div className={styles.header}>
          <h1 className={styles.logo}>{{ cookiecutter.project_name }}</h1>
          <h2 className={styles.title}>
            {% if cookiecutter.default_language == 'fa' %}ایجاد حساب کاربری{% else %}Create your account{% endif %}
          </h2>
          <p className={styles.subtitle}>
            {% if cookiecutter.default_language == 'fa' %}همین الان شروع کنید{% else %}Get started in minutes{% endif %}
          </p>
        </div>

        {error && (
          <div className={styles.error}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className={styles.form}>
          <div style={% raw %}{{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-4)' }}{% endraw %}>
            <div className={styles.field}>
              <label htmlFor="firstName" className={styles.label}>
                {% if cookiecutter.default_language == 'fa' %}نام{% else %}First name{% endif %}
              </label>
              <input
                id="firstName"
                name="firstName"
                type="text"
                value={formData.firstName}
                onChange={handleChange}
                className={styles.input}
                placeholder="{% if cookiecutter.default_language == 'fa' %}نام{% else %}First name{% endif %}"
                disabled={isLoading}
              />
            </div>

            <div className={styles.field}>
              <label htmlFor="lastName" className={styles.label}>
                {% if cookiecutter.default_language == 'fa' %}نام خانوادگی{% else %}Last name{% endif %}
              </label>
              <input
                id="lastName"
                name="lastName"
                type="text"
                value={formData.lastName}
                onChange={handleChange}
                className={styles.input}
                placeholder="{% if cookiecutter.default_language == 'fa' %}نام خانوادگی{% else %}Last name{% endif %}"
                disabled={isLoading}
              />
            </div>
          </div>

          <div className={styles.field}>
            <label htmlFor="email" className={styles.label}>
              {% if cookiecutter.default_language == 'fa' %}ایمیل{% else %}Email{% endif %}
            </label>
            <input
              id="email"
              name="email"
              type="email"
              value={formData.email}
              onChange={handleChange}
              className={styles.input}
              placeholder="{% if cookiecutter.default_language == 'fa' %}ایمیل خود را وارد کنید{% else %}Enter your email{% endif %}"
              required
              disabled={isLoading}
            />
          </div>

          <div className={styles.field}>
            <label htmlFor="password" className={styles.label}>
              {% if cookiecutter.default_language == 'fa' %}رمز عبور{% else %}Password{% endif %}
            </label>
            <input
              id="password"
              name="password"
              type="password"
              value={formData.password}
              onChange={handleChange}
              className={styles.input}
              placeholder="{% if cookiecutter.default_language == 'fa' %}حداقل ۸ کاراکتر{% else %}At least 8 characters{% endif %}"
              required
              disabled={isLoading}
            />
            <div className={styles.passwordStrength}>
              {[1, 2, 3, 4, 5].map((level) => (
                <div
                  key={level}
                  className={`${styles.strengthBar} ${
                    passwordStrength >= level
                      ? passwordStrength <= 2
                        ? styles.weak
                        : passwordStrength <= 3
                        ? styles.medium
                        : styles.strong
                      : ''
                  }`}
                />
              ))}
            </div>
            <p className={styles.passwordHint}>
              {% if cookiecutter.default_language == 'fa' %}حروف بزرگ، کوچک، عدد و علامت{% else %}Include uppercase, lowercase, number{% endif %}
            </p>
          </div>

          <div className={styles.field}>
            <label htmlFor="confirmPassword" className={styles.label}>
              {% if cookiecutter.default_language == 'fa' %}تکرار رمز عبور{% else %}Confirm password{% endif %}
            </label>
            <input
              id="confirmPassword"
              name="confirmPassword"
              type="password"
              value={formData.confirmPassword}
              onChange={handleChange}
              className={styles.input}
              placeholder="{% if cookiecutter.default_language == 'fa' %}تکرار رمز عبور{% else %}Confirm your password{% endif %}"
              required
              disabled={isLoading}
            />
          </div>

          <label className={styles.checkbox}>
            <input type="checkbox" required />
            <span>
              {% if cookiecutter.default_language == 'fa' %}
              با <Link href="/terms" className={styles.link}>قوانین</Link> و <Link href="/privacy" className={styles.link}>حریم خصوصی</Link> موافقم
              {% else %}
              I agree to the <Link href="/terms" className={styles.link}>Terms</Link> and <Link href="/privacy" className={styles.link}>Privacy Policy</Link>
              {% endif %}
            </span>
          </label>

          <button 
            type="submit" 
            className={styles.button}
            disabled={isLoading}
          >
            {isLoading ? (
              <span className={styles.spinner}>⏳</span>
            ) : (
              '{% if cookiecutter.default_language == "fa" %}ثبت‌نام{% else %}Create account{% endif %}'
            )}
          </button>
        </form>

        <div className={styles.footer}>
          <span>{% if cookiecutter.default_language == 'fa' %}قبلاً ثبت‌نام کرده‌اید؟{% else %}Already have an account?{% endif %}</span>
          <Link href="/login" className={styles.link}>
            {% if cookiecutter.default_language == 'fa' %}ورود{% else %}Sign in{% endif %}
          </Link>
        </div>
      </div>
    </div>
  );
}
