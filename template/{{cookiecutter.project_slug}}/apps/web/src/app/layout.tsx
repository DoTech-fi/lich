import type { Metadata } from 'next'
import '@/styles/globals.css'

export const metadata: Metadata = {
  title: '{{ cookiecutter.project_name }}',
  description: '{{ cookiecutter.project_description }}',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="{{ cookiecutter.default_language }}"{% if cookiecutter.default_language == 'fa' %} dir="rtl"{% endif %}>
      <body>{children}</body>
    </html>
  )
}
