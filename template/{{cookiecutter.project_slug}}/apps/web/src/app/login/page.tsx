'use client';

/**
 * Login Page
 * Clean, premium login form
 */

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
{%- if cookiecutter.auth_strategy == 'jwt_builtin' %}
import { useAuth } from '@/context/AuthContext';
{%- endif %}
import styles from './auth.module.css';

export default function LoginPage() {
  const router = useRouter();
  {%- if cookiecutter.auth_strategy == 'jwt_builtin' %}
  const { login } = useAuth();
  {%- endif %}
  
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      {%- if cookiecutter.auth_strategy == 'jwt_builtin' %}
      await login({ email, password });
      router.push('/dashboard');
      {%- elif cookiecutter.auth_strategy == 'keycloak' %}
      // Redirect to Keycloak login
      const config = await fetch('/api/auth/config').then(r => r.json());
      window.location.href = `${config.keycloak_url}/realms/${config.realm}/protocol/openid-connect/auth?client_id=${config.client_id}&redirect_uri=${window.location.origin}/auth/callback&response_type=code&scope=openid`;
      {%- else %}
      router.push('/dashboard');
      {%- endif %}
    } catch (err: any) {
      setError(err.message || '{% if cookiecutter.default_language == "fa" %}خطا در ورود{% else %}Login failed{% endif %}');
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
            {% if cookiecutter.default_language == 'fa' %}ورود به حساب کاربری{% else %}Sign in to your account{% endif %}
          </h2>
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

          <div className={styles.field}>
            <label htmlFor="password" className={styles.label}>
              {% if cookiecutter.default_language == 'fa' %}رمز عبور{% else %}Password{% endif %}
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className={styles.input}
              placeholder="{% if cookiecutter.default_language == 'fa' %}رمز عبور خود را وارد کنید{% else %}Enter your password{% endif %}"
              required
              disabled={isLoading}
            />
          </div>

          <div className={styles.options}>
            <label className={styles.checkbox}>
              <input type="checkbox" />
              <span>{% if cookiecutter.default_language == 'fa' %}مرا به خاطر بسپار{% else %}Remember me{% endif %}</span>
            </label>
            <Link href="/forgot-password" className={styles.link}>
              {% if cookiecutter.default_language == 'fa' %}فراموشی رمز عبور{% else %}Forgot password?{% endif %}
            </Link>
          </div>

          <button 
            type="submit" 
            className={styles.button}
            disabled={isLoading}
          >
            {isLoading ? (
              <span className={styles.spinner}>⏳</span>
            ) : (
              '{% if cookiecutter.default_language == "fa" %}ورود{% else %}Sign in{% endif %}'
            )}
          </button>
        </form>

        <div className={styles.footer}>
          <span>{% if cookiecutter.default_language == 'fa' %}حساب کاربری ندارید؟{% else %}Don't have an account?{% endif %}</span>
          <Link href="/register" className={styles.link}>
            {% if cookiecutter.default_language == 'fa' %}ثبت‌نام{% else %}Sign up{% endif %}
          </Link>
        </div>
      </div>
    </div>
  );
}
