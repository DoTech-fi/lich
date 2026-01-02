'use client';

/**
 * Sidebar Component
 * Responsive navigation sidebar with collapsible menu
 */

import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import styles from './Sidebar.module.css';

interface NavItem {
  label: string;
  href: string;
  icon: string;
}

const navItems: NavItem[] = [
  { label: '{% if cookiecutter.default_language == "fa" %}داشبورد{% else %}Dashboard{% endif %}', href: '/dashboard', icon: '📊' },
  { label: '{% if cookiecutter.default_language == "fa" %}پروفایل{% else %}Profile{% endif %}', href: '/profile', icon: '👤' },
  { label: '{% if cookiecutter.default_language == "fa" %}تنظیمات{% else %}Settings{% endif %}', href: '/settings', icon: '⚙️' },
];

export default function Sidebar() {
  const pathname = usePathname();
  const [isCollapsed, setIsCollapsed] = useState(false);

  return (
    <aside className={`${styles.sidebar} ${isCollapsed ? styles.collapsed : ''}`}>
      <div className={styles.header}>
        <Link href="/" className={styles.logo}>
          {isCollapsed ? '🚀' : '{{ cookiecutter.project_name }}'}
        </Link>
        <button 
          className={styles.toggle}
          onClick={() => setIsCollapsed(!isCollapsed)}
          aria-label="Toggle sidebar"
        >
          {isCollapsed ? '→' : '←'}
        </button>
      </div>

      <nav className={styles.nav}>
        {navItems.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className={`${styles.navItem} ${pathname === item.href ? styles.active : ''}`}
          >
            <span className={styles.icon}>{item.icon}</span>
            {!isCollapsed && <span className={styles.label}>{item.label}</span>}
          </Link>
        ))}
      </nav>

      <div className={styles.footer}>
        <Link href="/logout" className={styles.navItem}>
          <span className={styles.icon}>🚪</span>
          {!isCollapsed && <span className={styles.label}>{% if cookiecutter.default_language == "fa" %}خروج{% else %}Logout{% endif %}</span>}
        </Link>
      </div>
    </aside>
  );
}
