# نصب

## پیش‌نیازها

- **Python 3.10+** - [دانلود Python](https://python.org)
- **Docker** - برای دیتابیس و سرویس‌ها ضروری است
- **Node.js 18+** - برای توسعه فرانت‌اند

## نصب Lich CLI

### از PyPI (پیشنهاد شده)

```bash
pip install lich
```

### تایید نصب

```bash
lich --version
# 🧙 Lich Framework v1.4.1
```

### آپدیت به آخرین نسخه

```bash
pip install --upgrade lich
```

## ابزارهای اختیاری

برای بهترین تجربه توسعه، این ابزارها را نصب کنید:

### IPython (برای `lich shell`)

```bash
pip install ipython
```

### pytest-watch (برای `lich test --watch`)

```bash
pip install pytest-watch
```

## مراحل بعدی

بعد از نصب، اولین پروژه را بسازید:

```bash
lich init
```

[:octicons-arrow-right-24: راهنمای شروع سریع](quickstart.md)
