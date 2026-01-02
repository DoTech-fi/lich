# lich make policy

ساخت authorization policy برای کنترل دسترسی.

## استفاده

```bash
lich make policy <Name>
```

## مثال

```bash
$ lich make policy Article

✅ Policy ArticlePolicy ساخته شد!
```

## کد تولید شده

```python
class ArticlePolicy:
    def can_view(self, user: User, article: Article) -> bool:
        """آیا کاربر می‌تواند این مقاله را ببیند؟"""
        if article.is_public:
            return True
        return article.author_id == user.id
    
    def can_edit(self, user: User, article: Article) -> bool:
        """آیا کاربر می‌تواند این مقاله را ویرایش کند؟"""
        return article.author_id == user.id or user.is_admin
```

## استفاده در API

```python
@router.put("/{id}")
async def update_article(id: UUID, current_user: User = Depends(get_current_user)):
    article = await service.get(id)
    
    if not ArticlePolicy().can_edit(current_user, article):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # ادامه بروزرسانی...
```
