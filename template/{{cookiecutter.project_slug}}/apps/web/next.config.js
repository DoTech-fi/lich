/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  {%- if cookiecutter.use_i18n == 'yes' %}
  i18n: {
    locales: ['{{ cookiecutter.default_language }}', '{% if cookiecutter.default_language == "fa" %}en{% else %}fa{% endif %}'],
    defaultLocale: '{{ cookiecutter.default_language }}',
  },
  {%- endif %}
}

module.exports = nextConfig
